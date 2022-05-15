from copy import deepcopy
from datetime import datetime, timedelta, time
import json
from services.smart_home import SmartHomeEnergyGenerator, SmartHomeEnergyReceiver, SmartHomeEnergyStorage, SmartHomeDevice
from users.models import User
from rest_framework import viewsets, generics, status, mixins
from rest_framework.permissions import AllowAny
from .models import Building, Device, EnergyGenerator, EnergyMeasurement, EnergyReceiver, EnergyStorage, Floor, Room
from .serializers import BuildingSerializer, BuildingListSerializer, DeviceSerializer, RoomSerializer, EnergyMeasurementViewSerializer, EnergyMeasurementSerializer
from services.smart_home import SmartHomeUser, SmartHomeBuilding
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import transaction
from collections import defaultdict

class BuildingFromJsonFileViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [
        AllowAny,
    ]

    @transaction.atomic
    def create(self, request):
        with open("dane_json.txt", "r") as f:
            devices = json.load(f)
        user = User.objects.get(id=1)
        building = Building(name="house_arizona", user=user, id=devices[0].get("building"))
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
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        smart_devices=[]
        for device in devices:
            for_smart = deepcopy(device)
            smart_device_class = {
                "EnergyReceiver": SmartHomeEnergyReceiver,
                "EnergyGenerator": SmartHomeEnergyGenerator,
                "EnergyStorage": SmartHomeEnergyStorage
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


class DeviceViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [
        AllowAny,
    ]

    @classmethod
    def get_extra_actions(cls):
        return []

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        json_device = super().partial_update(request, *args, **kwargs)
        smart_device_class = {
                    "EnergyReceiver": SmartHomeEnergyReceiver,
                    "EnergyGenerator": SmartHomeEnergyGenerator,
                    "EnergyStorage": SmartHomeEnergyStorage
                }.get(json_device.data["type"])
        smart_device = smart_device_class(json_device.data)
        resp = smart_device.update_state()
        return Response(resp.json(), status=resp.status_code)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [
        AllowAny,
    ]

class BuildingEnergyView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    #returns building energy usage hour by hour for current day
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
                        device["energy_measurements"][hour] = self._get_energy_by_device_id(devices_energies, device["id"])

        return Response(serialized_building)
    
    def _get_energy_by_device_id(self, devices, id_):
        device_energy =  next((dev for dev in devices if dev["device_id"] == id_))
        return {
            "energy_value": device_energy.get("energy_value"),
            "price": device_energy.get("price")
        }
    


class EnergyMeasurementViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = EnergyMeasurement.objects.all()
    serializer_class = EnergyMeasurementViewSerializer
    permission_classes = [
        AllowAny,
    ]

    @classmethod
    def get_extra_actions(cls):
        return []
    
    def get(self, request, *args, **kwargs):
        serializer = EnergyMeasurementViewSerializer(data=request.query_params)
        if serializer.is_valid():
            print(serializer.data)
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = validated_data.get("building")
            building = get_object_or_404(Building, id=building.id)
            serialized_building = BuildingSerializer(building).data

            self._initialize_device_energy_dicts(serialized_building)
            energy_measurements = EnergyMeasurement.objects.filter(date__range=[start_date, end_date], device__building=building)

            for floor in serialized_building.get("building_floors"):
                for room in floor.get("floor_rooms"):
                    for device in room.get("room_devices"):
                        energy_data = [data for data in energy_measurements if data.device.id == device.get("id")]
                        for day in energy_data:
                            if device.get("id")==1:
                                print(day)
                            date_str = "%Y-%m-%d"
                            device["energy_data"]["energy_sum"][day.date.strftime(date_str)] = day.energy_value
                            device["energy_data"]["energy_price"][day.date.strftime(date_str)] = day.calculated_price
                            device["energy_data"]["energy_source"][day.date.strftime(date_str)] = day.energy_source
                
            return Response(serialized_building)
    
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = EnergyMeasurementViewSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.to_internal_value(serializer.data)
            start_date = validated_data.get("start_date")
            end_date = validated_data.get("end_date")
            building = validated_data.get("building")
            building = get_object_or_404(Building, id=building.id)
            serialized_building = BuildingSerializer(building).data
            smart_building = SmartHomeBuilding(serialized_building)

            measurements = []
            days = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]
            for day in days:
                start_datetime = datetime.combine(day, time(0,0,0))
                end_datetime = datetime.combine(day, time(23,59,59))
                day_energy_data = smart_building.get_energy(start_datetime, end_datetime)
                
                for energy_data in day_energy_data:
                    device_obj = Device.objects.get(id=energy_data["device_id"])
                    measurements.append(EnergyMeasurement(
                        device=device_obj, 
                        date=day, 
                        energy_value=energy_data.get("energy_value"), 
                        calculated_price=energy_data.get("calculated_price"),
                        energy_source=energy_data.get("energy_source"))
                        )
            energy_measurements = EnergyMeasurement.objects.bulk_create(measurements, ignore_conflicts=True)
            serializer = EnergyMeasurementSerializer(energy_measurements, many=True)
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
        smart_devices=[]
        for device in device_data:
            device["resourcetype"] = device.get("type")
            device["building"] = building.id
            serializer = self.serializer_class(data=device)
            if serializer.is_valid():
                serializer.save()
                smart_device_class = {
                    "EnergyReceiver": SmartHomeEnergyReceiver,
                    "EnergyGenerator": SmartHomeEnergyGenerator,
                    "EnergyStorage": SmartHomeEnergyStorage
                }.get(serializer.data["type"])
                smart_devices.append(smart_device_class(serializer.data))
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        smart_building = SmartHomeBuilding(building.__dict__)
                
        resp = smart_building.push_devices(smart_devices)
        return Response(resp.json(), status=resp.status_code)
