from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": True,
            "status_code": response.status_code,
            "message": _get_message(response.data),
            "details": response.data,
        }

    return response


def _get_message(data):
    if isinstance(data, dict):
        return data.get("detail", "Error de validación.")
    if isinstance(data, list):
        return data[0] if data else "Error desconocido."
    return str(data)