from django.urls import include, path
from rest_framework import routers

from .views import (weather_data_view, BuildingDevicesView, BuildingEnergyView,BuildingViewSet, BuildingEnergySourcesRaportsView, BuildingExchangeEnergyStorageRaportsView,
                    DeviceViewSet, BuildingEnergyMeasurementViewSet, RoomViewSet, BuildingEnergyGridSurplusRaportsView, BuildingPhotovoltaicsSufficiencyRaportsView)

app_name = "smarthome"


router = routers.SimpleRouter()
router.register(r"buildings", BuildingViewSet)
router.register(r"rooms", RoomViewSet)
router.register(r"devices", DeviceViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # path("devices/", DeviceViewSet.as_view({'get': 'list'}), name="devices"),
    path(
        "devices/<int:pk>/",
        DeviceViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="devices",
    ),
    path(
        "buildings/<int:pk>/energy-measurements/",
        BuildingEnergyMeasurementViewSet.as_view(),
        name="building-energy-measurements",
    ),
    path("buildings/<int:pk>/energy/", BuildingEnergyView.as_view(), name="energy"),
    path(
        "buildings/<int:pk>/devices/",
        BuildingDevicesView.as_view(),
        name="building-devices",
    ),
    path(
        "buildings/<int:pk>/energy-sources/",
        BuildingEnergySourcesRaportsView.as_view(),
        name="building-energy-sources",
    ),
    path(
        "buildings/<int:pk>/energy-grid-surplus/",
        BuildingEnergyGridSurplusRaportsView.as_view(),
        name="building-energy-grid-surplus",
    ),
    path(
        "buildings/<int:pk>/photovoltaics-sufficiency/",
        BuildingPhotovoltaicsSufficiencyRaportsView.as_view(),
        name="building-photovoltaics-sufficiency",
    ),
    path(
        "buildings/<int:pk>/exchange-energy/",
        BuildingExchangeEnergyStorageRaportsView.as_view(),
        name="building-exchange-energy",
    ),
    path('weather/', weather_data_view, name='weather-data-view'),
]
