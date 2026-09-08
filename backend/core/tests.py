from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Patient, Treatment


class PatientTests(APITestCase):

    def setUp(self):
        self.patient_data = {
            "identification": "12345678",
            "first_name": "Ana",
            "last_name": "García",
            "birth_date": "1990-05-15",
        }
        self.patient = Patient.objects.create(**self.patient_data)
        self.list_url = reverse("patient-list")
        self.detail_url = reverse("patient-detail", kwargs={"pk": self.patient.pk})

    def test_crear_paciente_exitoso(self):
        data = {
            "identification": "99999999",
            "first_name": "Carlos",
            "last_name": "López",
            "birth_date": "1985-03-20",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)

    def test_crear_paciente_identificacion_duplicada(self):
        response = self.client.post(self.list_url, self.patient_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_pacientes(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_obtener_paciente_por_id(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["identification"], "12345678")

    def test_paciente_inexistente_retorna_404(self):
        url = reverse("patient-detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_actualizar_parcialmente_paciente(self):
        response = self.client.patch(
            self.detail_url, {"first_name": "María"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "María")
        self.assertEqual(response.data["last_name"], "García")

    def test_campos_requeridos_retorna_400(self):
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TreatmentTests(APITestCase):

    def setUp(self):
        self.patient = Patient.objects.create(
            identification="11111111",
            first_name="Luis",
            last_name="Martínez",
            birth_date="1975-08-10",
        )
        self.list_url = reverse("treatment-list")

    def test_crear_tratamiento_exitoso(self):
        data = {
            "patient": self.patient.pk,
            "name": "Fisioterapia",
            "start_date": "2024-01-01",
            "status": "active",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fecha_fin_anterior_a_inicio_retorna_400(self):
        data = {
            "patient": self.patient.pk,
            "name": "Fisioterapia",
            "start_date": "2024-01-01",
            "end_date": "2023-12-31",
            "status": "active",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_estado_tratamiento(self):
        treatment = Treatment.objects.create(
            patient=self.patient,
            name="Quimioterapia",
            start_date="2024-01-01",
            status="active",
        )
        url = reverse("treatment-detail", kwargs={"pk": treatment.pk})
        response = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")


class ActiveTreatmentTests(APITestCase):

    def setUp(self):
        self.patient = Patient.objects.create(
            identification="22222222",
            first_name="Elena",
            last_name="Ruiz",
            birth_date="1988-12-01",
        )
        self.url = reverse("patient-active-treatment", kwargs={"pk": self.patient.pk})

    def test_sin_tratamientos_retorna_false(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["has_active_treatment"])
        self.assertIsNone(response.data["treatment"])

    def test_con_tratamiento_activo_retorna_true(self):
        Treatment.objects.create(
            patient=self.patient,
            name="Radioterapia",
            start_date="2024-06-01",
            status="active",
        )
        response = self.client.get(self.url)
        self.assertTrue(response.data["has_active_treatment"])
        self.assertEqual(response.data["treatment"]["name"], "Radioterapia")

    def test_solo_tratamiento_completado_retorna_false(self):
        Treatment.objects.create(
            patient=self.patient,
            name="Diálisis",
            start_date="2023-01-01",
            end_date="2023-06-01",
            status="completed",
        )
        response = self.client.get(self.url)
        self.assertFalse(response.data["has_active_treatment"])

    def test_paciente_inexistente_retorna_404(self):
        url = reverse("patient-active-treatment", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)