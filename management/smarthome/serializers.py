from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (Building, Device, EnergyDailyMeasurement, EnergyGenerator, EnergyMeasurement,
                     EnergyReceiver, EnergySourcesRaport, EnergyStorage, EnergySurplusLossRaport, EnergySurplusRaport, ExchangeEnergyStorageRaport, Floor, PhotovoltaicsSufficiencyRaport, Room)


class AbstractDeviceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Device
        fields = "__all__"


class EnergyGeneratorSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnergyGenerator
        fields = (
            "id",
            "building",
            "name",
            "state",
            "room",
            "efficiency",
            "type",
            "generation_power",
        )


class EnergyReceiverSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = EnergyReceiver
        fields = (
            "id",
            "building",
            "name",
            "state",
            "room",
            "device_power",
            "type",
            "supply_voltage",
        )


class EnergyStorageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = EnergyStorage
        fields = (
            "id",
            "building",
            "name",
            "state",
            "room",
            "capacity",
            "type",
            "battery_voltage",
        )


class DeviceSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Device: AbstractDeviceSerializer,
        EnergyGenerator: EnergyGeneratorSerializer,
        EnergyReceiver: EnergyReceiverSerializer,
        EnergyStorage: EnergyStorageSerializer,
    }


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
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

class EnergySourcesRaportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySourcesRaport
        fields = "__all__"

class EnergySurplusRaportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySurplusRaport
        fields = "__all__"

class EnergySurplusLossRaportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySurplusLossRaport
        fields = "__all__"

class PhotovoltaicsSufficiencyRaportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotovoltaicsSufficiencyRaport
        fields = "__all__"

class ExchangeEnergyStorageRaportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeEnergyStorageRaport
        fields = "__all__"

class BuildingIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ("id",)

class EnergyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyMeasurement
        fields = "__all__"

class DateTimeRangeSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S"])
    end_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", input_formats=["%Y-%m-%d %H:%M:%S"], required=True
    )

class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    end_date = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
