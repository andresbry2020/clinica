from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, TreatmentViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"treatments", TreatmentViewSet, basename="treatment")

urlpatterns = [
    path("", include(router.urls)),
]