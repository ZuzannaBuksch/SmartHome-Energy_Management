from django.core.validators import MaxValueValidator
from django.db import models
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from users.models import User
from django.forms.models import model_to_dict
from services.smart_home import SmartHomeBuilding, SmartHomeUser, SmartHomeEnergyGenerator, SmartHomeEnergyReceiver, SmartHomeEnergyStorage

class Building(models.Model):
    name = models.CharField(max_length=100, null=True)
    icon = models.IntegerField(null=True, blank=True, default=0)
    use_exchange_energy = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, related_name="user_buildings", null=False, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Building: {str(self.id)} | name: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        smart_user = SmartHomeUser(model_to_dict(self.user))
        building = {"name": self.name, "icon": self.icon, "id": self.id, "user": self.user}
        smart_building = SmartHomeBuilding(building)
        smart_user.push_buildings([smart_building])

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
    name = models.CharField(max_length=100, null=False)
    state = models.BooleanField(null=False, default=False)
    room = models.ForeignKey(
        Room,
        related_name="room_devices",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        smart_building = SmartHomeBuilding(model_to_dict(self.building))
        device = {"name": self.name, "type": self.type,  "state": self.state, "id": self.id, "device_power": self.device_power, "supply_voltage": self.supply_voltage}
        smart_device = SmartHomeEnergyReceiver(device)
        smart_building.push_devices([smart_device])

class EnergyGenerator(Device):
    generation_power = models.FloatField() #Wat

    def __str__(self):
        return f"Energy generating device: {str(self.id)} | name: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        smart_building = SmartHomeBuilding(model_to_dict(self.building))
        device = {"name": self.name, "type": self.type,  "state": self.state, "id": self.id, "generation_power": self.generation_power}
        smart_device = SmartHomeEnergyGenerator(device)
        smart_building.push_devices([smart_device])

class EnergyStorage(Device):
    capacity = models.FloatField()  # [kWh]
    battery_voltage = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Energy storing device: {str(self.id)} | name: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        smart_building = SmartHomeBuilding(model_to_dict(self.building))
        device = {"name": self.name, "type": self.type,  "state": self.state, "id": self.id, "capacity": self.capacity, "battery_voltage": self.battery_voltage}
        smart_device = SmartHomeEnergyStorage(device)
        smart_building.push_devices([smart_device])

class EnergyDailyMeasurement(models.Model):
    datetime = models.DateTimeField(auto_now=False, null=False)
    energy_value = models.FloatField(null=False)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="device_daily_measurements"
    )

    class Meta:
        unique_together = (
            "device",
            "datetime",
        )

    def __str__(self):
        return f"Measurement: {str(self.id)} | device: {self.device.name} | datetime: {self.datetime}"


class EnergyMeasurement(models.Model):
    date = models.DateField(auto_now=False, null=False)
    energy_value = models.FloatField(null=False)
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

class ExchangeEnergyStorageRaport(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="building_exchange_raports",
        null=False,
        on_delete=models.CASCADE,
    )
    total_value = models.FloatField(null=False)
    remained_value = models.FloatField(null=False)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    date_time_from = models.DateTimeField()
    date_time_to = models.DateTimeField()

    class Meta:
        unique_together = ('building', 'date_time_from',)

class EnergySurplusLossRaport(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="building_surplus_loss_raports",
        null=False,
        on_delete=models.CASCADE,
    )
    value = models.FloatField(null=False)
    date_time = models.DateTimeField()

    class Meta:
        unique_together = ('building', 'date_time',)

class EnergySurplusRaport(models.Model):
    #is for Grid Surplus
    TRANSFER = 'TRANSFER'
    DEVICES_POWERING= 'DEVICES_POWERING'
    BATTERY_CHARGING = 'BATTERY_CHARGING'
    usage_types = [
        (TRANSFER, "transfer"),
        (DEVICES_POWERING, "devices_powering"),
        (BATTERY_CHARGING, "battery_charging")
    ]
    usage_type = models.CharField(max_length=20, choices=usage_types)
    building = models.ForeignKey(
        Building,
        related_name="building_surplus_raports",
        null=False,
        on_delete=models.CASCADE,
    )
    value = models.FloatField(null=False)
    date_time = models.DateTimeField()

    class Meta:
        unique_together = ('building', 'date_time', 'usage_type', 'value')

    def save(self, *args, **kwargs):
        try:
            current_value = EnergySurplusRaport.objects.filter(building=self.building).last().value
        except AttributeError:
            current_value = 0
        
        if self.value<=0 and self.usage_type == EnergySurplusRaport.BATTERY_CHARGING:
                return

        if self.usage_type == EnergySurplusRaport.TRANSFER:
            value_to_grid = 0.8*float(self.value)
            value_loss = 0.2*float(self.value)
            try:
                loss = EnergySurplusLossRaport.objects.get(building=self.building, date_time=self.date_time)
                loss.value+=value_loss
                loss.save(update_fields=["value"])
            except EnergySurplusLossRaport.DoesNotExist:
                EnergySurplusLossRaport.objects.create(value=value_loss, building=self.building, date_time=self.date_time)
            self.value = float(current_value)+value_to_grid

        else:
            self.value = current_value-self.value
        
        return super().save(*args, **kwargs)

class EnergySourcesRaport(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="building_energy_sources_raports",
        null=False,
        on_delete=models.CASCADE,
    )
    energy_sources = JSONField(null=False)
    date_time_from = models.DateTimeField()
    date_time_to = models.DateTimeField()

    class Meta:
        unique_together = ('building', 'date_time_from',)

class PhotovoltaicsSufficiencyRaport(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="building_photovoltaics_sufficiency_raports",
        null=False,
        on_delete=models.CASCADE,
    )
    sufficiency_percentage = models.FloatField(null=False)
    date_time = models.DateTimeField()

    class Meta:
        unique_together = ('building', 'date_time',)

class Schedule(models.Model):
    building = models.ForeignKey(
        Building,
        related_name="building_schedules",
        null=False,
        on_delete=models.CASCADE,
    )
    device = models.ForeignKey(
        Device, related_name="device_schedules", null=False, on_delete=models.CASCADE
    )
    state = models.BooleanField(null=False, default=False)
    state_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=None
    )
    date_time_from = models.DateTimeField()
    date_time_to = models.DateTimeField()

    class Meta:
        unique_together = (
            "device",
            "date_time_from",
        )

    def __str__(self):
        return f"Schedule: {str(self.id)} | device: {self.device.name}"
