from django.db import models
from django.core.validators import MaxValueValidator
from polymorphic.models import PolymorphicModel
from users.models import User
from jsonfield import JSONField

class Building(models.Model):
    name = models.CharField(max_length=100, null=True)
    icon = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(
        User, related_name="user_buildings", null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Building: {str(self.id)} | name: {self.name}"

class Floor(models.Model):
    building = models.ForeignKey(
        Building, related_name="building_floors", null=False, on_delete=models.CASCADE
    )
    level = models.PositiveIntegerField(validators=[MaxValueValidator(10)])

class Room(models.Model):
    name = models.CharField(max_length=100, null=True)
    area = models.DecimalField(max_digits=4, decimal_places=1, null=False, blank=False)
    floor = models.ForeignKey(
        Floor, related_name="floor_rooms", null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Room: {str(self.id)} | name: {self.name}"

class Device(PolymorphicModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    state = models.BooleanField(null=False, default=False)
    room = models.ForeignKey(
        Room, related_name="room_devices", null=True, blank=True, on_delete=models.CASCADE
    )
    building = models.ForeignKey(
        Building, related_name="building_devices", on_delete=models.CASCADE
    )

    @property
    def type(self):
        return self.__class__.__name__


class EnergyReceiver(Device):
    device_power = models.FloatField() 
    supply_voltage = models.FloatField() 

    def __str__(self):
        return f"Energy receiving device: {str(self.id)} | name: {self.name}"


class EnergyGenerator(Device):
    generation_power = models.FloatField()
    
    def __str__(self):
        return f"Energy generating device: {str(self.id)} | name: {self.name}"


class EnergyStorage(Device):
    capacity = models.FloatField() #[Ah]
    battery_voltage = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Energy storing device: {str(self.id)} | name: {self.name}"


class EnergyDailyMeasurement(models.Model):
    datetime = models.DateTimeField(auto_now=False, null=False)
    energy_value = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    calculated_price = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    energy_source = models.CharField(max_length=100, null=False)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="device_daily_measurements"
    )

    class Meta:
        unique_together = (
            "device",
            "datetime",
        )

    def __str__(self):
        return f"Measurement: {str(self.id)} | device: {self.device.name} | date: {self.datetime}"

class EnergyMeasurement(models.Model):
    date = models.DateField(auto_now=False, null=False)
    energy_value = models.DecimalField(max_digits=10, decimal_places=3, null=False)
    calculated_price = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    energy_sources_percentage = JSONField(null=False)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="device_measurements"
    )

    class Meta:
        unique_together = (
            "device",
            "date",
        )

    def __str__(self):
        return f"Measurement: {str(self.id)} | device: {self.device.name} | date: {self.date}"


class Schedule(models.Model):
    building = models.ForeignKey(
        Building, related_name="building_schedules", null=False, on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        Device, related_name="device_schedules", null=False, on_delete=models.CASCADE
    )
    state = models.BooleanField(null=False, default=False)
    state_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()

    class Meta:
        unique_together = (
            "device",
            "date_from",
        )

    def __str__(self):
        return f"Schedule: {str(self.id)} | device: {self.device.name}"
