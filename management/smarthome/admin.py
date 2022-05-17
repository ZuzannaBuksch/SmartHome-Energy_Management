from django.contrib import admin
from .models import Device, Building, EnergyGenerator, EnergyReceiver, EnergyStorage, Room, Floor, EnergyDailyMeasurement

admin.site.register(Device)
admin.site.register(Room)
admin.site.register(Floor)
admin.site.register(EnergyDailyMeasurement)
admin.site.register(Building)
admin.site.register(EnergyStorage)
admin.site.register(EnergyReceiver)
admin.site.register(EnergyGenerator)

# Register your models here.
