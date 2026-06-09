"""Object storage helpers for raw research artifacts."""

from typing import Protocol

import boto3
from botocore.client import BaseClient

from signal_forge_api.config import Settings


class ObjectStore(Protocol):
    """Protocol for storing bytes in object storage."""

    def put_bytes(self, key: str, content: bytes, content_type: str | None) -> None:
        """Store bytes at an object key."""


class S3ObjectStore:
    """S3-compatible object store backed by MinIO locally."""

    def __init__(self, settings: Settings) -> None:
        """Create the object store client from settings."""
        self._bucket = settings.minio_bucket
        self._client: BaseClient = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
        )

    def put_bytes(self, key: str, content: bytes, content_type: str | None) -> None:
        """Store bytes at an object key, creating the bucket if needed."""
        self._ensure_bucket()
        kwargs: dict[str, object] = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": content,
        }
        if content_type:
            kwargs["ContentType"] = content_type
        self._client.put_object(**kwargs)

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except Exception:  # noqa: BLE001 - boto3 raises service-specific dynamic exceptions.
            self._client.create_bucket(Bucket=self._bucket)


def get_object_store(settings: Settings) -> ObjectStore:
    """Build the configured object store."""
    return S3ObjectStore(settings)
