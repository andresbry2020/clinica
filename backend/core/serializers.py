from rest_framework import serializers
from .models import Patient, Treatment


class TreatmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Treatment
        fields = [
            "id", "patient", "name",
            "start_date", "end_date",
            "status", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "La fecha de fin debe ser posterior a la fecha de inicio."}
            )
        return attrs


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            "id", "identification", "first_name",
            "last_name", "birth_date", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_identification(self, value):
        instance = self.instance
        qs = Patient.objects.filter(identification=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un paciente con esta identificación."
            )
        return value


class ActiveTreatmentSerializer(serializers.Serializer):
    has_active_treatment = serializers.BooleanField()
    treatment = TreatmentSerializer(allow_null=True)