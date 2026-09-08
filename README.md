Clinic API

API REST para gestión de pacientes y tratamientos médicos.
Construida con Python, Django, Django REST Framework y PostgreSQL.

## Tecnologías

- **Backend**: Python 3.12 + Django 5 + Django REST Framework
- **Base de datos**: PostgreSQL 16
- **Contenedores**: Docker Compose
- **Documentación**: Swagger (drf-spectacular)

## Requisitos

- Docker Desktop instalado y corriendo

## Instalación y ejecución

```bash
git clone <tu-repo>
cd ips
docker compose up --build
```

- API disponible en: http://localhost:8000/api/
- Documentación Swagger: http://localhost:8000/api/schema/docs/

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta Django | django-insecure-... |
| `DEBUG` | Modo debug | True |
| `ALLOWED_HOSTS` | Hosts permitidos | * |
| `DB_NAME` | Nombre de la base de datos | clinic_db |
| `DB_USER` | Usuario PostgreSQL | clinic_user |
| `DB_PASSWORD` | Contraseña PostgreSQL | clinic_password |
| `DB_HOST` | Host de la BD | db |
| `DB_PORT` | Puerto PostgreSQL | 5432 |

## Migraciones

```bash
docker compose exec backend python manage.py migrate
```

## Ejecución de tests

```bash
docker compose exec backend python manage.py test core --verbosity=2
```

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/patients/` | Crear paciente |
| `GET` | `/api/patients/` | Listar pacientes (paginado) |
| `GET` | `/api/patients/{id}/` | Obtener paciente por ID |
| `PATCH` | `/api/patients/{id}/` | Actualizar parcialmente paciente |
| `GET` | `/api/patients/{id}/active-treatment/` | Consultar tratamiento activo |
| `POST` | `/api/treatments/` | Crear tratamiento |
| `GET` | `/api/treatments/` | Listar tratamientos (paginado) |
| `GET` | `/api/treatments/{id}/` | Obtener tratamiento por ID |
| `PATCH` | `/api/treatments/{id}/` | Actualizar parcialmente tratamiento |

### Filtros disponibles

- `GET /api/patients/?search=Ana` — buscar por nombre, apellido o identificación
- `GET /api/treatments/?status=active` — filtrar tratamientos por estado
- `GET /api/treatments/?patient=1` — filtrar tratamientos por paciente
- `GET /api/patients/?ordering=-created_at` — ordenar resultados

## Arquitectura

```
ips/
├── backend/
│   ├── clinica/          ← configuración Django (settings, urls)
│   └── core/             ← app principal
│       ├── models.py     ← modelos Patient y Treatment
│       ├── serializers.py
│       ├── views.py      ← ViewSets con filtros y paginación
│       ├── urls.py
│       ├── exceptions.py ← manejo de errores personalizado
│       └── tests.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```
## Uso de IA

Ver [AI_USAGE.md](./AI_USAGE.md) para el detalle completo del uso de inteligencia artificial en este proyecto.
