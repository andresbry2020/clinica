from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Patient, Treatment
from .serializers import (
    PatientSerializer,
    TreatmentSerializer,
    ActiveTreatmentSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name", "identification"]
    ordering_fields = ["created_at", "last_name"]

    @action(detail=True, methods=["get"], url_path="active-treatment")
    def active_treatment(self, request, pk=None):
        patient = self.get_object()

        active_treatment = (
            Treatment.objects
            .filter(patient=patient, status=Treatment.Status.ACTIVE)
            .first()
        )

        data = {
            "has_active_treatment": active_treatment is not None,
            "treatment": active_treatment,
        }

        serializer = ActiveTreatmentSerializer(data)
        return Response(serializer.data)


class TreatmentViewSet(viewsets.ModelViewSet):
    queryset = Treatment.objects.select_related("patient").all()
    serializer_class = TreatmentSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "patient"]
    search_fields = ["name"]
    ordering_fields = ["start_date", "created_at"]