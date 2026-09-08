from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from core.models import Patient, Treatment


class Command(BaseCommand):
    """
    Management command para cargar datos de demostración.

    Uso:
        python manage.py seed_data           → crea los datos
        python manage.py seed_data --clear   → borra todo y recrea los datos
    """

    help = "Carga datos de demostración: pacientes y tratamientos de ejemplo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina todos los datos existentes antes de crear los nuevos",
        )

    def handle(self, *args, **options):

        if options["clear"]:
            self.stdout.write(self.style.WARNING("🗑️  Eliminando datos existentes..."))
            Treatment.objects.all().delete()
            Patient.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Datos eliminados."))

        self.stdout.write(self.style.NOTICE("\n👤 Creando pacientes..."))
        patients = self._create_patients()

        self.stdout.write(self.style.NOTICE("\n💊 Creando tratamientos..."))
        self._create_treatments(patients)

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Datos de demostración cargados correctamente."
            f"\n   → {Patient.objects.count()} pacientes"
            f"\n   → {Treatment.objects.count()} tratamientos"
            f"\n\n📖 Explora la API en: http://localhost:8000/api/"
            f"\n📚 Documentación en:  http://localhost:8000/api/schema/docs/"
        ))

    def _create_patients(self):
        """Crea 5 pacientes de ejemplo."""

        patients_data = [
            {
                "identification": "10234567",
                "first_name": "Ana",
                "last_name": "García",
                "birth_date": date(1990, 5, 15),
            },
            {
                "identification": "20345678",
                "first_name": "Luis",
                "last_name": "Martínez",
                "birth_date": date(1978, 8, 22),
            },
            {
                "identification": "30456789",
                "first_name": "Elena",
                "last_name": "Ruiz",
                "birth_date": date(1995, 3, 10),
            },
            {
                "identification": "40567890",
                "first_name": "Carlos",
                "last_name": "López",
                "birth_date": date(1965, 11, 30),
            },
            {
                "identification": "50678901",
                "first_name": "María",
                "last_name": "Torres",
                "birth_date": date(2000, 1, 5),
            },
        ]

        patients = []
        for data in patients_data:
            patient, created = Patient.objects.get_or_create(
                identification=data["identification"],
                defaults=data,
            )
            status = "creado" if created else "ya existía"
            self.stdout.write(f"   {'✅' if created else '⏭️ '} {patient.first_name} {patient.last_name} — {status}")
            patients.append(patient)

        return patients

    def _create_treatments(self, patients):
        """Crea 10 tratamientos distribuidos entre los pacientes."""

        ana, luis, elena, carlos, maria = patients

        treatments_data = [
            # Ana — tiene 1 tratamiento activo y 1 completado
            {
                "patient": ana,
                "name": "Fisioterapia lumbar",
                "start_date": date(2024, 1, 10),
                "end_date": None,
                "status": Treatment.Status.ACTIVE,
            },
            {
                "patient": ana,
                "name": "Control nutricional",
                "start_date": date(2023, 3, 1),
                "end_date": date(2023, 9, 1),
                "status": Treatment.Status.COMPLETED,
            },

            # Luis — tiene 1 tratamiento activo
            {
                "patient": luis,
                "name": "Quimioterapia ciclo 3",
                "start_date": date(2024, 3, 15),
                "end_date": None,
                "status": Treatment.Status.ACTIVE,
            },

            # Elena — tiene 2 tratamientos completados y 1 cancelado
            {
                "patient": elena,
                "name": "Rehabilitación rodilla",
                "start_date": date(2023, 6, 1),
                "end_date": date(2023, 12, 1),
                "status": Treatment.Status.COMPLETED,
            },
            {
                "patient": elena,
                "name": "Terapia psicológica",
                "start_date": date(2022, 1, 15),
                "end_date": date(2022, 7, 15),
                "status": Treatment.Status.COMPLETED,
            },
            {
                "patient": elena,
                "name": "Acupuntura",
                "start_date": date(2024, 2, 1),
                "end_date": None,
                "status": Treatment.Status.CANCELLED,
            },

            # Carlos — tiene 2 tratamientos activos (el más cargado)
            {
                "patient": carlos,
                "name": "Diálisis renal",
                "start_date": date(2023, 10, 1),
                "end_date": None,
                "status": Treatment.Status.ACTIVE,
            },
            {
                "patient": carlos,
                "name": "Control cardiológico",
                "start_date": date(2024, 1, 1),
                "end_date": None,
                "status": Treatment.Status.ACTIVE,
            },

            # María — sin tratamientos activos (solo 1 completado)
            # → útil para probar el endpoint /active-treatment/ con has_active=false
            {
                "patient": maria,
                "name": "Vacunación antigripal",
                "start_date": date(2023, 4, 1),
                "end_date": date(2023, 4, 30),
                "status": Treatment.Status.COMPLETED,
            },

            # Paciente extra de Carlos para hacer más interesantes las queries SQL
            {
                "patient": carlos,
                "name": "Radioterapia",
                "start_date": date(2022, 5, 1),
                "end_date": date(2022, 11, 1),
                "status": Treatment.Status.COMPLETED,
            },
        ]

        for data in treatments_data:
            treatment, created = Treatment.objects.get_or_create(
                patient=data["patient"],
                name=data["name"],
                defaults=data,
            )
            status = "creado" if created else "ya existía"
            self.stdout.write(
                f"   {'✅' if created else '⏭️ '} [{treatment.status.upper()}] "
                f"{treatment.name} → {treatment.patient.first_name} — {status}"
            )
