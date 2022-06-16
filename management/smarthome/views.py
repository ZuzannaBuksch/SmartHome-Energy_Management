from collections import defaultdict
from datetime import datetime
from django.forms.models import model_to_dict
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.smart_home import (SmartHomeEnergyGenerator,
                                 SmartHomeEnergyReceiver,
                                 SmartHomeEnergyStorage)

from data_providers import WeatherDataProvider
from .measurements_manager import EnergyMeasurementsManager
from .models import (Building, Device, EnergyDailyMeasurement, EnergyGenerator, EnergyMeasurement,
                     EnergyReceiver, EnergySourcesRaport, EnergyStorage, EnergySurplusLossRaport, EnergySurplusRaport, ExchangeEnergyStorageRaport, Floor, PhotovoltaicsSufficiencyRaport, Room)
from .serializers import (BuildingListSerializer, BuildingSerializer, DateRangeSerializer,
                          DeviceSerializer, EnergyDailyMeasurementSerializer,
                          DateTimeRangeSerializer, EnergyMeasurementSerializer, EnergySourcesRaportSerializer, EnergySurplusLossRaportSerializer, EnergySurplusRaportSerializer, ExchangeEnergyStorageRaportSerializer, PhotovoltaicsSufficiencyRaportSerializer, RoomSerializer)




@api_view()
def weather_data_view(request):
    serializer = DateTimeRangeSerializer(data=request.query_params)
    if serializer.is_valid(raise_exception=True):
        validated_data = serializer.to_internal_value(serializer.data)
        start_date = validated_data.get("start_datetime")
        end_date = validated_data.get("end_datetime")
        weather_data = WeatherDataProvider().get_data(start_date, end_date)
        return Response(weather_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    list_serializer_class = BuildingListSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return self.list_serializer_class
        return self.serializer_class


    # def get_queryset(self):
    #     return self.request.user.user_buildings.all()


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [
        AllowAny,
    ]

    @classmethod
    def get_extra_actions(cls):
        return []

    def _get_device_class_by_type(self, type_):
        return {
            EnergyReceiver.__name__: SmartHomeEnergyReceiver,
            EnergyGenerator.__name__: SmartHomeEnergyGenerator,
            EnergyStorage.__name__: SmartHomeEnergyStorage,
        }.get(type_)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        json_device = super().partial_update(request, *args, **kwargs)
        smart_device_class = self._get_device_class_by_type(json_device.data["type"])
        smart_device = smart_device_class(json_device.data)
        resp = smart_device.update_state()
        return Response(resp.json(), status=resp.status_code)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [
        AllowAny,
    ]



class BuildingEnergyView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [
        AllowAny,
    ]
    queryset = EnergyMeasurement.objects.all()
    serializer_class = DateRangeSerializer

    @classmethod
    def get_extra_actions(cls):
        return []

    # api/buildings/1/energy
    def get(self, request, *args, **kwargs):
        serializer = DateRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = get_object_or_404(Building, id=kwargs.get("pk"))
            serialized_building = BuildingSerializer(building).data

            energy_measurements = self.get_queryset().filter(
                date__range=[start_date, end_date]
            )

            for floor in serialized_building.get("building_floors"):
                for room in floor.get("floor_rooms"):
                    for device in room.get("room_devices"):
                        device = self._get_receiver_energy_data(device, energy_measurements)
            
            no_room_receivers = EnergyReceiver.objects.all().filter(building=building, room=None)
            other_devices = [self._get_receiver_energy_data(model_to_dict(device), energy_measurements) for device in no_room_receivers]
            serialized_building["other_devices"]=other_devices
            photovoltaics_data = self._get_photovoltaics_data(building, energy_measurements)
            serialized_building["photovoltaics"] = photovoltaics_data
            return Response(serialized_building)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = DateRangeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = get_object_or_404(Building, id=kwargs.get("pk"))
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            daily_measurements = EnergyDailyMeasurement.objects.all().filter(
                device__building=building, datetime__range=[start_datetime, end_datetime]
            )
            devices_dates_energy_sum = defaultdict(lambda: defaultdict(lambda:0))
            for measurement in daily_measurements:
                devices_dates_energy_sum[measurement.device][measurement.datetime.date()] += measurement.energy_value
            energy_measurements = []
            for device, data in devices_dates_energy_sum.items():
                for date, energy_sum in data.items():
                    energy_measurements.append(EnergyMeasurement(device=device, date=date, energy_value=energy_sum))
            serializer = EnergyMeasurementSerializer(energy_measurements, many=True)
            EnergyMeasurement.objects.bulk_create(energy_measurements, ignore_conflicts=True)
        return Response(serializer.data)

    def _get_receiver_energy_data(self, device, energy_measurements):
        device["energy_data"] = {}
        energy_data = [
                    data
                    for data in energy_measurements
                    if data.device.id == device.get("id")
                ]
        energy_sum = 0
        for measurement in energy_data:
            date_str = "%Y-%m-%d"
            device["energy_data"][measurement.date.strftime(date_str)] = measurement.energy_value
            energy_sum+=measurement.energy_value
        
        device["energy_sum"] = energy_sum
        return device

    def _get_photovoltaics_data(self, building, energy_measurements):
        try:
            photovoltaics_device = EnergyGenerator.objects.all().get(building=building)
        except EnergyGenerator.DoesNotExist:
            return {}

        photovoltaics_data = model_to_dict(photovoltaics_device)
        photovoltaics_data["energy_data"] = {}
        energy_data = [
                        data
                        for data in energy_measurements
                        if data.device.id == photovoltaics_device.id
                    ]
        energy_sum = 0
        for measurement in energy_data:
            date_str = "%Y-%m-%d"
            photovoltaics_data["energy_data"][measurement.date.strftime(date_str)] = measurement.energy_value
            energy_sum+=measurement.energy_value
        
        photovoltaics_data["energy_sum"]=energy_sum
        return photovoltaics_data

class BuildingEnergyMeasurementViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    queryset = EnergyDailyMeasurement.objects.all()
    serializer_class = DateTimeRangeSerializer
    permission_classes = [
        AllowAny,
    ]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get_queryset(self):
        return self.queryset.filter(device__building__pk=self.kwargs["pk"])


    def get(self, request, *args, **kwargs):
        serializer = DateTimeRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_datetime")
            end_date = validated_data.get("end_datetime")
            building = get_object_or_404(Building, id=kwargs.get("pk"))
            serialized_building = BuildingSerializer(building).data

            energy_measurements = self.get_queryset().filter(
                datetime__range=[start_date, end_date]
            )

            for floor in serialized_building.get("building_floors"):
                for room in floor.get("floor_rooms"):
                    for device in room.get("room_devices"):
                        device = self._get_receiver_energy_data(device, energy_measurements)
     
            no_room_receivers = EnergyReceiver.objects.all().filter(building=building, room=None)
            other_devices = [self._get_receiver_energy_data(model_to_dict(device), energy_measurements) for device in no_room_receivers]
            serialized_building["other_devices"]=other_devices
            photovoltaics_data = self._get_photovoltaics_data(building, energy_measurements)
            serialized_building["photovoltaics"] = photovoltaics_data
            return Response(serialized_building, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = DateTimeRangeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.to_internal_value(serializer.data)
            start_datetime = validated_data.get("start_datetime")
            end_datetime = validated_data.get("end_datetime")
            building = get_object_or_404(Building, id=kwargs.get("pk"))

            measurements, sources, surpluses = EnergyMeasurementsManager(building).download_home_energy(
                start_datetime, end_datetime
            )

            serializer_sources = EnergySourcesRaportSerializer(sources, many=True)
            serializer_measurements = EnergyDailyMeasurementSerializer(measurements, many=True)
            response = {"sources": serializer_sources.data, "surpluses": {}, "measurements": serializer_measurements.data}
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_receiver_energy_data(self, device, energy_measurements):
        device["energy_data"] = {}
        energy_data = [
            data
            for data in energy_measurements
            if data.device.id == device.get("id")
        ]
        energy_sum = 0
        for measurement in energy_data:
            datetime_str = "%Y-%m-%d %H:%M:%S"
            device["energy_data"][measurement.datetime.strftime(datetime_str)] = measurement.energy_value
            energy_sum+=measurement.energy_value
        
        device["energy_sum"] = energy_sum
        return device

    def _get_photovoltaics_data(self, building, energy_measurements):
        try:
            photovoltaics_device = EnergyGenerator.objects.all().get(building=building)
        except EnergyGenerator.DoesNotExist:
            return {}

        photovoltaics_data = model_to_dict(photovoltaics_device)
        photovoltaics_data["energy_data"] = {}
        energy_data = [
                        data
                        for data in energy_measurements
                        if data.device.id == photovoltaics_device.id
                    ]
        energy_sum = 0
        for measurement in energy_data:
            datetime_str = "%Y-%m-%d %H:%M:%S"
            photovoltaics_data["energy_data"][measurement.datetime.strftime(datetime_str)] = measurement.energy_value
            energy_sum+=measurement.energy_value
        
        photovoltaics_data["energy_sum"]=energy_sum
        return photovoltaics_data

class DatesRangeFilterView(generics.ListAPIView):
    def get_queryset(self):
        return self.queryset.filter(building__pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        serializer = DateTimeRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_datetime")
            end_date = validated_data.get("end_datetime")

            raports = self.get_queryset().filter(
               Q(date_time_from__range=[start_date, end_date]) |
               Q(date_time_to__range=[start_date, end_date])
            )
            for raport in raports:
                raport.date_time_from = raport.date_time_from if raport.date_time_from >= start_date else start_date
                raport.date_time_to = raport.date_time_to if raport.date_time_to <= end_date else end_date
            serializer = self.get_serializer(raports, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuildingEnergySourcesRaportsView(DatesRangeFilterView):
    queryset = EnergySourcesRaport.objects.all()
    serializer_class = EnergySourcesRaportSerializer
    permission_classes = [
        AllowAny,
    ]


class BuildingExchangeEnergyStorageRaportsView(DatesRangeFilterView):
    queryset = ExchangeEnergyStorageRaport.objects.all()
    serializer_class = ExchangeEnergyStorageRaportSerializer
    permission_classes = [
        AllowAny,
    ]

class SingleDateRangeFilterView(generics.ListAPIView):
    def get_queryset(self):
        return self.queryset.filter(building__pk=self.kwargs["pk"])


    def get(self, request, *args, **kwargs):
        serializer = DateTimeRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_datetime")
            end_date = validated_data.get("end_datetime")

            raports = self.get_queryset().filter(date_time__range=[start_date, end_date])

            serializer = self.get_serializer(raports, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuildingPhotovoltaicsSufficiencyRaportsView(SingleDateRangeFilterView):
    queryset = PhotovoltaicsSufficiencyRaport.objects.all()
    serializer_class = PhotovoltaicsSufficiencyRaportSerializer
    permission_classes = [
        AllowAny,
    ]


class BuildingEnergyGridSurplusRaportsView(generics.ListAPIView):
    queryset = EnergySurplusRaport.objects.all()
    serializer_class = EnergySurplusRaportSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        return self.queryset.filter(building__pk=self.kwargs["pk"])

    def get_loss_queryset(self):
        return EnergySurplusLossRaport.objects.all().filter(building__pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        serializer = DateTimeRangeSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_datetime")
            end_date = validated_data.get("end_datetime")

            raports = self.get_queryset().filter(date_time__range=[start_date, end_date])
            raports_loss = self.get_loss_queryset().filter(date_time__range=[start_date, end_date])

            serializer = EnergySurplusRaportSerializer(raports, many=True)
            loss_serializer = EnergySurplusLossRaportSerializer(raports_loss, many=True)
            resp = {"grid_surplus_data": serializer.data, "grid_surplus_loss_data": loss_serializer.data}
            return Response(resp, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuildingDevicesView(generics.ListAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [
        AllowAny,
    ]

    def get_queryset(self):
        return self.queryset.filter(building__pk=self.kwargs["pk"])

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        building = get_object_or_404(Building, id=kwargs.get("pk"))
        device_data = request.data
        for device in device_data:
            device["resourcetype"] = device.get("type")
            device["building"] = building.id
            serializer = self.serializer_class(data=device)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response({}, status=status.HTTP_200_OK)
