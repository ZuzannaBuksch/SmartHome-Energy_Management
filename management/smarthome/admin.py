from django.contrib import admin

from .models import (Building, Device, EnergyDailyMeasurement, EnergyGenerator, EnergySourcesRaport, EnergySurplusRaport, EnergySurplusLossRaport,
                     EnergyReceiver, EnergyStorage, Floor, Room)

admin.site.register(Device)
admin.site.register(Room)
admin.site.register(Floor)
admin.site.register(EnergyDailyMeasurement)
admin.site.register(Building)
admin.site.register(EnergyStorage)
admin.site.register(EnergyReceiver)
admin.site.register(EnergyGenerator)
admin.site.register(EnergySourcesRaport)
admin.site.register(EnergySurplusLossRaport)
admin.site.register(EnergySurplusRaport)

# Register your models here.
