from django.urls import include, path
from rest_framework import routers

from .views import (BuildingDevicesView, BuildingEnergyView,
                    BuildingFromJsonFileViewSet, BuildingViewSet,
                    DeviceViewSet, EnergyMeasurementViewSet, RoomViewSet)

app_name = "smarthome"


router = routers.SimpleRouter()
router.register(r"buildings", BuildingViewSet)
router.register(r"rooms", RoomViewSet)
router.register(r"devices", DeviceViewSet)
router.register(r"json-buildings", BuildingFromJsonFileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("devices/", DeviceViewSet.as_view({'get': 'list'}), name="devices"),
    path(
        "devices/<int:pk>/",
        DeviceViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="devices",
    ),
    path(
        "energy-measurements/",
        EnergyMeasurementViewSet.as_view(),
        name="energy-measurements",
    ),
    path("buildings/<int:pk>/energy/", BuildingEnergyView.as_view(), name="energy"),
    path(
        "buildings/<int:pk>/devices/",
        BuildingDevicesView.as_view(),
        name="building-devices",
    ),
]
