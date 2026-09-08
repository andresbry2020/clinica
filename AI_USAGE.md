# Uso de Inteligencia Artificial

Este proyecto fue desarrollado con el apoyo de **Antigravity (Google Deepmind)**.
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
- Ajusté los nombres de los campos del modelo según los requerimientos (`identification`, `first_name`, `last_name`, `birth_date`).
- Cambié el nombre del proyecto Django de `clinic` a `clinica`.
- Ajusté el `docker-compose.yml` para incluir el `healthcheck` correcto.

**Verificación:**
- El proyecto levanta correctamente con `docker compose up --build`.
- Todos los endpoints responden en `http://localhost:8000/api/`.

---

## 2. Manejador de errores personalizado

**Herramienta:** Antigravity (Google Deepmind)

**Problema consultado:**
Cómo implementar un manejador de errores global en DRF que normalice todas las respuestas en un formato JSON consistente.

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
- Extraí la lógica de `message` a una función `_get_message()` separada para manejar tanto `dict` como listas de errores, ya que DRF a veces retorna listas en lugar de diccionarios.

**Verificación:**
- Tests con datos inválidos confirman que el formato de error es consistente.
- Recursos inexistentes retornan `{"error": true, "status_code": 404, ...}`.

---

## 3. Ejercicio de IA — Endpoint lento con 100.000 pacientes

**Herramienta:** Antigravity (Google Deepmind)

**Escenario:**
Un endpoint de pacientes tarda demasiado cuando existen 100.000 pacientes y múltiples tratamientos por paciente.

**Prompt utilizado:**
> "Tengo este endpoint Django que es muy lento con 100.000 pacientes. Identifica el problema y propón la solución óptima explicando el impacto en PostgreSQL y Django ORM:
>
> @api_view(['GET'])
> def patients(request):
>     patients = Patient.objects.all()
>     data = []
>     for patient in patients:
>         treatments = Treatment.objects.filter(patient=patient)
>         data.append({'id': patient.id, 'name': patient.name, 'treatments': list(treatments.values())})
>     return Response(data)"

**Problemas identificados por la IA:**

| # | Problema | Impacto |
|---|----------|---------|
| 1 | **N+1 queries** | Con 100.000 pacientes = 100.001 queries a PostgreSQL |
| 2 | **Sin paginación** | Se cargan todos los registros en memoria de una vez |
| 3 | **`fields = '__all__'` / `.values()`** | Expone campos sensibles sin control |
| 4 | **`patient.name` no existe** | El modelo tiene `first_name` y `last_name` |
| 5 | **Sin índices** | PostgreSQL hace full table scan en cada filtro |
| 6 | **Sin caché** | Cada request regenera toda la respuesta |

**Solución propuesta por la IA y adoptada:**

```python
# ✅ Versión corregida
class PatientViewSet(viewsets.ModelViewSet):
    # prefetch_related resuelve el N+1:
    # En lugar de 100.001 queries → solo 2 queries totales
    queryset = Patient.objects.prefetch_related("treatments").all()
    serializer_class = PatientSerializer          # Campos controlados explícitamente
    pagination_class = PageNumberPagination       # Máximo 20 por página
    filter_backends = [SearchFilter, OrderingFilter]
```

**Impacto en PostgreSQL y Django ORM:**

- **`prefetch_related("treatments")`**: Django ejecuta exactamente 2 queries — una para todos los pacientes y otra para todos los tratamientos relacionados. Los combina en Python. Sin esto, con 100.000 pacientes serían 100.001 queries.

- **Paginación (`PAGE_SIZE = 20`)**: PostgreSQL usa `LIMIT 20 OFFSET 0` en lugar de traer todos los registros. Reduce drásticamente el uso de memoria y tiempo de respuesta.

- **Índices en el modelo**: Se agregaron índices en `identification` y en `(patient, status)` para que PostgreSQL use Index Scan en lugar de Sequential Scan, lo que es hasta 100x más rápido en tablas grandes.

- **Serializer con campos explícitos**: Evita traer columnas innecesarias de PostgreSQL y previene exponer datos sensibles.

**Cambios realizados sobre la propuesta:**
- Usé `ModelViewSet` en lugar de `@api_view` para aprovechar toda la funcionalidad de DRF.
- Agregué `select_related("patient")` en `TreatmentViewSet` para el caso inverso.
- Los índices los definí directamente en el modelo con `class Meta: indexes = [...]`.

**Verificación:**
- Con `django-debug-toolbar` (o logs de Django) se confirma que el endpoint genera exactamente 2 queries independientemente del número de pacientes.
- Los tests de listado confirman que la paginación retorna máximo 20 resultados con `count` y `next`.

---

## 4. Revisión de código generado por IA

**Código revisado:**
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

**Problemas identificados:**

### ❌ N+1 Queries
Por cada paciente se ejecuta una query adicional para obtener sus tratamientos.
Con 1.000 pacientes = 1.001 queries. Con 100.000 = 100.001 queries.
**Solución:** `Patient.objects.prefetch_related("treatments").all()`

### ❌ Sin paginación
Se retornan TODOS los registros en una sola respuesta.
Con 100.000 pacientes la respuesta puede superar los 500MB y agotar la memoria del servidor.
**Solución:** Configurar `PageNumberPagination` con `PAGE_SIZE = 20`.

### ❌ Serialización manual insegura
`.values()` expone TODOS los campos del modelo incluyendo posibles datos sensibles.
**Solución:** Usar `ModelSerializer` con `fields = [...]` explícitos.

### ❌ Campo inexistente
`patient.name` no existe en el modelo. El modelo tiene `first_name` y `last_name`.
Esto lanza `AttributeError` en tiempo de ejecución.
**Solución:** Usar el serializer que mapea correctamente los campos.

### ❌ Sin filtros ni búsqueda
No hay forma de filtrar pacientes. El cliente recibe todo o nada.
**Solución:** `filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]`

### ❌ Sin control de seguridad
No hay autenticación ni permisos. Cualquiera puede acceder a todos los datos.
**Solución:** `permission_classes = [IsAuthenticated]`

### ❌ Sin manejo de errores
Si ocurre un error, Django retorna HTML en lugar de JSON.
**Solución:** `custom_exception_handler` registrado en `settings.py`.

---

## Conclusión

La IA fue una herramienta de aceleración del desarrollo, no un reemplazo del criterio técnico.
Cada propuesta fue revisada, entendida y ajustada antes de ser incorporada.
Los tests automatizados fueron la principal forma de verificar que el código generado funcionaba correctamente.
