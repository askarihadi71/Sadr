import hashlib
import mimetypes
import os
import pathlib
from typing import Tuple
from uuid import uuid4

from django.conf import settings
from django.core import exceptions
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from django.utils.encoding import filepath_to_uri
from django.utils.text import get_valid_filename
from django.utils import timezone


def _validate_file_size(file_obj):
    max_size =  5000000

    if file_obj.size > max_size:
        raise ValidationError(f"File is too large. It should not exceed {bytes_to_mib(max_size)} MiB")

def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


def file_generate_upload_path(instance, filename):
    return f"files/{instance.file_name}"

def validate_MaxFileSize(value):
    maxSize = 10 * 1024 * 1024
    size = value.size
    if size > maxSize:
        raise ValidationError(
            _('max file size error.'),
            params={'max_size':maxSize/(1024*1024)}
        )

def hashed_upload_path(instance, filename):
    base_directory = 'Files/'
    salt = timezone.now().__str__()
    filename, extension = os.path.splitext(filename)
    if not extension:
        extension = '.unk'
    basename = get_valid_filename(filename)[:64]
    hashed = hashlib.sha256(salt + basename.encode()).hexdigest()
    filename = f"{hashed}{extension}"

    return filepath_to_uri(os.path.join(base_directory, filename))


def file_generate_local_upload_url(*, file_id: str):
    url = reverse("api:files:upload:direct:local", kwargs={"file_id": file_id})

    app_domain: str = settings.APP_DOMAIN  # type: ignore

    return f"{app_domain}{url}"


def bytes_to_mib(value: int) -> float:
    # 1 bytes = 9.5367431640625E-7 mebibytes
    return value * 9.5367431640625e-7
