import time
import logging
from functools import wraps
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # Use Django-compatible logger

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper


def validate_input(func):
    """Decorator to validate input data."""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return wrapper

def handle_exceptions(func):
    """Decorator to handle errors like duplicate records and database failures."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            logging.error(f"Database Integrity Error: {str(e)}")
            return Response({"error": "Duplicate record detected."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logging.error(f"Validation Error: {e.message_dict}")
            return Response({"error": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            logging.error(f"DRF Validation Error: {e.detail}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            logging.error(f"Missing Field: {str(e)}")
            return Response({"error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Unexpected Error: {str(e)}")
            return Response({"error": "Internal Server Error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper
