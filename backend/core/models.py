from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """
    Representa un paciente en el sistema.
    
    identification: documento de identidad (único, para evitar duplicados)
    birth_date: fecha de nacimiento
    created_at: timestamp automático de cuándo fue creado el registro
    """
    identification = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Los más recientes primero por defecto
        indexes = [
            # Índice en identification para búsquedas rápidas
            models.Index(fields=["identification"], name="patient_identification_idx"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.identification})"


class Treatment(models.Model):
    """
    Representa un tratamiento asignado a un paciente.
    
    status: puede ser 'active', 'completed' o 'cancelled'
    end_date: es opcional (null) si el tratamiento sigue activo
    """
    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        COMPLETED = "completed", "Completado"
        CANCELLED = "cancelled", "Cancelado"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,       # Si se elimina el paciente, se eliminan sus tratamientos
        related_name="treatments",       # patient.treatments.all() para acceder desde el paciente
    )
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Opcional
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [
            # Índice compuesto para la query de tratamiento activo (muy común)
            models.Index(fields=["patient", "status"], name="treatment_patient_status_idx"),
        ]

    def __str__(self):
        return f"{self.name} - {self.patient} ({self.status})"