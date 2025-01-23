from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import APIException

import logging

logger = logging.getLogger("db")


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}

class InternalServerError(APIException):
    status_code = 500
    default_detail = 'Internal Server Error.'

    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        self.detail = detail

class BadRequest(APIException):
    status_code = 400
    default_detail = 'Bad Request.'
    
    def __init__(self, detail=None):
        if detail is None:
            detail = self.default_detail
        self.detail = detail

# class ValidationErrorHandlerMixin:
#     def handle_exception(self, exc):
#         if isinstance(exc, exceptions.ValidationError):
#             return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
#
#         logger.error(exc)
#         return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def custom_exception_handler(exc, ctx):
    """
        {
            "message": "Error message",
            "extra": {}
        }
        """
        
    if ctx:
        view = ctx.get('view', None)
        request = ctx.get('request', None)
        view_name = view.__class__.__name__ if view else 'Unknown view'
        
    logger.error(
        f"viewName = {view_name}, method: {request.method if request else 'Unknown method'}, exception: {exc}"
    )
        
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        logger.error(exc)
        if isinstance(exc, ApplicationError):
            data = {"message": exc.message, "extra": exc.extra}
            return Response(data, status=400)

        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    if isinstance(exc, exceptions.ValidationError):
        response.data["message"] = "Validation error"
        response.data["extra"] = {"fields": response.data["detail"]}
    else:
        response.data["message"] = response.data["detail"]
        response.data["extra"] = {}

    del response.data["detail"]
    
    
    return response