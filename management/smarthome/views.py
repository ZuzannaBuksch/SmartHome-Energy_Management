import json
from collections import defaultdict
from copy import deepcopy
import datetime

from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from services.smart_home import (SmartHomeBuilding, SmartHomeDevice,
                                 SmartHomeDeviceRaport,
                                 SmartHomeEnergyGenerator,
                                 SmartHomeEnergyReceiver,
                                 SmartHomeEnergyStorage, SmartHomeUser)
from services.smart_home.smart_raport import (
    JobType, SmartHomeChargeStateRaport, SmartHomeStorageChargingAndUsageRaport)
from users.models import User

from .energy_manager import BuildingEnergyManager
from .models import (Building, Device, EnergyDailyMeasurement, EnergyGenerator,
                     EnergyReceiver, EnergyStorage, Floor, Room)
from .serializers import (BuildingListSerializer, BuildingSerializer,
                          DeviceSerializer, EnergyDailyMeasurementSerializer,
                          EnergyDailyMeasurementViewSerializer, RoomSerializer)


class BuildingFromJsonFileViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [
        AllowAny,
    ]

    @transaction.atomic
    def create(self, request):
        # device = Device.objects.get(id=33)
        # smart_device = SmartHomeEnergyStorage(device.__dict__)
        # # raport = SmartHomeStorageChargingAndUsageRaport({"date_time_from": "2022-05-09 14:05:02", "date_time_to": "2022-05-09 14:06:02", "job_type": JobType.CHARGING.value})

        # resp = smart_device.get_raports(
        #     start_date=datetime(2022, 5, 9, 0, 0, 0),
        #     end_date=datetime(2022, 5, 9, 23, 59, 59),
        # )
        # print(resp)
        # return Response(resp.json(), status=resp.status_code)

        # device = Device.objects.get(id=33)
        # smart_device = SmartHomeEnergyStorage({**model_to_dict(device), "type": device.type})
        # raports = smart_device.get_charge_state_raports(start_date=datetime.datetime(2022, 5, 9, 0, 0, 0), end_date=datetime.datetime(2022, 5, 24, 23, 59, 59))
        # new_raport = SmartHomeChargeStateRaport({"date": datetime.datetime(2022,5,21,12,0,0), "charge_value": 0})
        # smart_device.push_charge_state_raports([new_raport])

        # start_date=datetime.datetime(2022, 5, 9, 0, 0, 0)
        # end_date=datetime.datetime(2022, 5, 24, 23, 59, 59)
        # building = Building.objects.get(id=1)
        # smart_building = SmartHomeBuilding(building.__dict__)
        # storage_data = smart_building.get_energy_storage(start_date, end_date)

        with open("dane_json.txt", "r") as f:
            devices = json.load(f)
        user = User.objects.get(id=1)
        building = Building(
            name="house_arizona", user=user, id=devices[0].get("building")
        )
        building.save()
        floor = Floor(level=1, building=building)
        floor.save()
        for device in devices:
            if device["room"]:
                room = Room(name=device["room"], floor=floor, area=10)
                room.save()
                device["room"] = room.id
            else:
                room = None
            device["resourcetype"] = device.get("type")
            device["building"] = building.id
            serializer = DeviceSerializer(data=device)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        smart_devices = []
        for device in devices:
            for_smart = deepcopy(device)
            smart_device_class = {
                "EnergyReceiver": SmartHomeEnergyReceiver,
                "EnergyGenerator": SmartHomeEnergyGenerator,
                "EnergyStorage": SmartHomeEnergyStorage,
            }.get(device["type"])
            smart_devices.append(smart_device_class(for_smart))

        smart_user = SmartHomeUser(user.__dict__)
        smart_building = SmartHomeBuilding(building.__dict__)
        smart_user.push_buildings([smart_building])
        resp = smart_building.push_devices(smart_devices)
        return Response(resp.json(), status=resp.status_code)


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

    @transaction.atomic
    def create(self, request):
        response = super().create(request)
        user = get_object_or_404(User, id=response.data.get("user"))
        smart_user = SmartHomeUser(user.__dict__)
        smart_building = SmartHomeBuilding(response.data)
        resp = smart_user.push_buildings([smart_building])
        return Response(resp.json(), status=resp.status_code)

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

    @transaction.atomic
    def create(self, request):
        if not request.data.get("id"):
            request.data["id"] = Device.objects.all().last().id + 1
        json_device = super().create(request)
        building = get_object_or_404(Building, id=json_device.data.get("building"))
        smart_building = SmartHomeBuilding(model_to_dict(building))
        smart_device_class = self._get_device_class_by_type(json_device.data["type"])
        smart_device = smart_device_class(json_device.data)
        resp = smart_building.push_devices([smart_device])
        return Response(resp.json(), status=resp.status_code)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [
        AllowAny,
    ]


class BuildingEnergyView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    # returns building energy usage hour by hour for current day
    permission_classes = [
        AllowAny,
    ]
    queryset = Building.objects.all()

    @classmethod
    def get_extra_actions(cls):
        return []

    # api/buildings/1/energy
    def get(self, request, *args, **kwargs):
        building = self.get_object()
        serialized_building = BuildingSerializer(building).data
        smart_building = SmartHomeBuilding(serialized_building)

        hours_energies = smart_building.get_energy_hour_by_hour()
        for floor in serialized_building.get("building_floors"):
            for room in floor.get("floor_rooms"):
                for device in room.get("room_devices"):
                    device["energy_measurements"] = {}
                    for hour, devices_energies in hours_energies.items():
                        device["energy_measurements"][
                            hour
                        ] = self._get_energy_by_device_id(
                            devices_energies, device["id"]
                        )

        return Response(serialized_building)

    def _get_energy_by_device_id(self, devices, id_):
        device_energy = next((dev for dev in devices if dev["device_id"] == id_))
        return {
            "energy_value": device_energy.get("energy_value"),
            "price": device_energy.get("price"),
        }


class EnergyMeasurementViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    queryset = EnergyDailyMeasurement.objects.all()
    serializer_class = EnergyDailyMeasurementViewSerializer
    permission_classes = [
        AllowAny,
    ]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        serializer = EnergyDailyMeasurementViewSerializer(data=request.query_params)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = validated_data.get("building")
            building = get_object_or_404(Building, id=building.id)
            serialized_building = BuildingSerializer(building).data

            self._initialize_device_energy_dicts(serialized_building)
            energy_measurements = EnergyDailyMeasurement.objects.filter(
                date__range=[start_date, end_date], device__building=building
            )

            for floor in serialized_building.get("building_floors"):
                for room in floor.get("floor_rooms"):
                    for device in room.get("room_devices"):
                        energy_data = [
                            data
                            for data in energy_measurements
                            if data.device.id == device.get("id")
                        ]
                        for day in energy_data:
                            if device.get("id") == 1:
                                print(day)
                            date_str = "%Y-%m-%d"
                            device["energy_data"]["energy_sum"][
                                day.date.strftime(date_str)
                            ] = day.energy_value
                            device["energy_data"]["energy_price"][
                                day.date.strftime(date_str)
                            ] = day.calculated_price
                            device["energy_data"]["energy_source"][
                                day.date.strftime(date_str)
                            ] = day.energy_source

            return Response(serialized_building)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = EnergyDailyMeasurementViewSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = validated_data.get("building")

            measurements = BuildingEnergyManager(building).manage_building_energy(
                start_date, end_date
            )
            serializer = EnergyDailyMeasurementSerializer(measurements, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _initialize_device_energy_dicts(self, building):
        for floor in building.get("building_floors"):
            for room in floor.get("floor_rooms"):
                for device in room.get("room_devices"):
                    d = defaultdict(lambda: {})
                    device["energy_data"] = d
        return building


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
        smart_devices = []
        for device in device_data:
            device["resourcetype"] = device.get("type")
            device["building"] = building.id
            serializer = self.serializer_class(data=device)
            if serializer.is_valid():
                serializer.save()
                smart_device_class = {
                    "EnergyReceiver": SmartHomeEnergyReceiver,
                    "EnergyGenerator": SmartHomeEnergyGenerator,
                    "EnergyStorage": SmartHomeEnergyStorage,
                }.get(serializer.data["type"])
                smart_devices.append(smart_device_class(serializer.data))
            else:
                return Response(
                    data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        smart_building = SmartHomeBuilding(building.__dict__)

        resp = smart_building.push_devices(smart_devices)
        return Response(resp.json(), status=resp.status_code)
