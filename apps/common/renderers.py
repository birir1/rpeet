"""
Custom renderer and exception handler implementing the KCK API envelope pattern.

Every API response is wrapped in a standard envelope:
  Success:  {"success": true, "data": ...}
  List:     {"success": true, "count": N, "next": ..., "previous": ..., "data": [...]}
  Error:    {"success": false, "error": "...", "code": "..."}

I chose this envelope pattern because the Laravel frontend needs a predictable response
structure. Without it, the frontend would need to check HTTP status codes AND parse
different response shapes for each endpoint. With the envelope, every response has
a "success" boolean the frontend can check first, and error messages are always in
the same location regardless of whether they come from validation, authentication, or
server errors.

Author: Meshack Tirop (Tirop Meshack Kimutai)
"""
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler


class KCKRenderer(JSONRenderer):
    """
    Wraps DRF responses in the KCK envelope:
      Success : {"success": true, "data": ...}
      List    : {"success": true, "count": N, "next": ..., "previous": ..., "data": [...]}
      Error   : {"success": false, "error": "...", "code": "..."}
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # If the response already has our envelope keys, pass through
        if isinstance(data, dict) and "success" in data:
            return super().render(data, accepted_media_type, renderer_context)

        if status.is_success(response.status_code):
            # Paginated responses from KCKPagination already have count/next/previous/data
            if isinstance(data, dict) and "results" in data:
                envelope = {
                    "success": True,
                    "count": data.get("count", 0),
                    "next": data.get("next"),
                    "previous": data.get("previous"),
                    "data": data["results"],
                }
            else:
                envelope = {"success": True, "data": data}
        else:
            # Error responses
            error_msg = data
            code = "ERROR"
            if isinstance(data, dict):
                error_msg = data.get("detail", data.get("error", data))
                code = data.get("code", "ERROR")
            envelope = {
                "success": False,
                "error": error_msg,
                "code": code,
            }

        return super().render(envelope, accepted_media_type, renderer_context)


def kck_exception_handler(exc, context):
    """
    Custom exception handler that returns errors in the KCK envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        code = "ERROR"
        if isinstance(exc, APIException):
            code = exc.default_code if hasattr(exc, "default_code") else "ERROR"
            code = str(code).upper()

        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            detail = detail["detail"]
        elif isinstance(detail, list):
            detail = detail[0] if detail else str(exc)

        response.data = {
            "success": False,
            "error": detail if isinstance(detail, str) else str(detail),
            "code": code,
        }

    return response
