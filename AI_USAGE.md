# Uso de Inteligencia Artificial

Este proyecto fue desarrollado con el apoyo de **Antigravity (Google Deepmind)** como herramienta de IA.
El uso de IA estuvo presente en varias etapas del desarrollo.

---

## 1. Guía de estructura del proyecto

**Herramienta:** Antigravity (Google Deepmind)

**Problema consultado:**
Cómo estructurar un proyecto Django + DRF con Docker Compose para una API de gestión de pacientes y tratamientos.

**Prompt utilizado:**
> "Guíame paso a paso para crear una API REST con Django, Django REST Framework y PostgreSQL usando Docker Compose. El proyecto debe gestionar pacientes y tratamientos con endpoints CRUD, paginación, filtros y tests."

**Propuesta generada:**
La IA generó la estructura completa del proyecto incluyendo `settings.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `Dockerfile` y `docker-compose.yml`.

**Cambios realizados:**
- Ajusté los nombres de los campos del modelo según los requerimientos de la prueba (`identification`, `first_name`, `last_name`, `birth_date`).
- Cambié el nombre del proyecto Django de `clinic` a `clinica`.
- Ajusté el `docker-compose.yml` para incluir el `healthcheck` correcto.

**Verificación:**
- El proyecto levanta correctamente con `docker compose up --build`.
- Todos los endpoints responden en `http://localhost:8000/api/`.

---

## 2. Manejador de errores personalizado

**Herramienta:** Antigravity (Google Deepmind)

**Problema consultado:**
Cómo implementar un manejador de errores global en DRF que normalice todas las respuestas de error en un formato JSON consistente.

**Prompt utilizado:**
> "¿Cómo implementar un custom_exception_handler en Django REST Framework que normalice todos los errores (validación, 404, 500) en una estructura JSON uniforme con campos error, status_code, message y details?"

**Propuesta generada:**
```python
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": True,
            "status_code": response.status_code,
            "message": response.data.get("detail", "Error de validación."),
            "details": response.data,
        }
    return response
```

**Cambios realizados:**
- Extraí la lógica de `message` a una función `_get_message()` separada para manejar correctamente tanto `dict` como listas de errores, ya que DRF a veces retorna listas en lugar de diccionarios.

**Verificación:**
- Tests con datos inválidos confirman que el formato de error es consistente.
- Recursos inexistentes retornan `{"error": true, "status_code": 404, ...}`.

---

## 3. Ejercicio de revisión de código con N+1

**Herramienta:** Antigravity (Google Deepmind)

**Problema consultado:**
Identificar y corregir problemas en el siguiente código generado por IA:

```python
@api_view(["GET"])
def patients(request):
    patients = Patient.objects.all()
    data = []
    for patient in patients:
        treatments = Treatment.objects.filter(patient=patient)
        data.append({
            "id": patient.id,
            "name": patient.name,
            "treatments": list(treatments.values())
        })
    return Response(data)
```

**Prompt utilizado:**
> "Identifica todos los problemas de este código Django: N+1 queries, paginación, serialización, performance, seguridad y escalabilidad."

**Propuesta generada:**
La IA identificó 6 problemas: N+1 queries, ausencia de paginación, serialización manual insegura, campo inexistente (`patient.name`), sin filtros y sin control de campos expuestos.

**Cambios realizados:**
- Confirmé cada problema identificado revisando la documentación de DRF.
- Implementé la versión corregida usando `ModelViewSet` con `prefetch_related`, `PageNumberPagination` y `ModelSerializer`.

**Verificación:**
- El ViewSet corregido genera exactamente 2 queries para cualquier cantidad de pacientes (1 para pacientes + 1 para tratamientos con prefetch).
- Los tests de listado confirman que la paginación funciona correctamente.

---

## Conclusión

La IA fue una herramienta de aceleración del desarrollo, no un reemplazo del criterio técnico. Cada propuesta fue revisada, entendida y ajustada antes de ser incorporada al proyecto. Los tests automatizados fueron la principal forma de verificar que el código generado funcionaba correctamente.
