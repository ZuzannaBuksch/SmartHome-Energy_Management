from rest_framework import serializers

from .models import Building, Room, Device, EnergyGenerator, EnergyReceiver, EnergyStorage, Floor, EnergyDailyMeasurement
from rest_polymorphic.serializers import PolymorphicSerializer
from django.utils.functional import lazy


class AbstractDeviceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Device
        fields = "__all__"


class EnergyGeneratorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = EnergyGenerator
        fields = ('id', 'building', 'name', 'state', 'room','efficiency', 'type', 'generation_power')


class EnergyReceiverSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = EnergyReceiver
        fields = ('id', 'building', 'name', 'state', 'room', 'device_power', 'type', 'supply_voltage')


class EnergyStorageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = EnergyStorage
        fields = ('id', 'building', 'name', 'state', 'room', 'capacity', 'battery_charge', 'type', 'battery_voltage')


class DeviceSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
            Device: AbstractDeviceSerializer,
            EnergyGenerator: EnergyGeneratorSerializer,
            EnergyReceiver: EnergyReceiverSerializer,
            EnergyStorage: EnergyStorageSerializer
        }


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    room_devices = DeviceSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = "__all__"
        extra_fields = ["room_devices"]


class FloorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    floor_rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Floor
        fields = "__all__"
        extra_fields = ["floor_rooms"]


class BuildingSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(
    #     default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault())
    # )
    id = serializers.IntegerField()
    building_floors = FloorSerializer(many=True, read_only=True)

    class Meta:
        model = Building
        fields = "__all__"
        extra_fields = ["building_floors"]


class BuildingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class EnergyDailyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyDailyMeasurement
        fields = "__all__"

class BuildingIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ("id", )


class EnergyDailyMeasurementViewSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%Y-%m-%d", input_formats=['%Y-%m-%d'])
    end_date = serializers.DateField(format="%Y-%m-%d", input_formats=['%Y-%m-%d'], required=False)
    building = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
