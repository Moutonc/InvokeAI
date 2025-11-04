"""Abstract base class for cloud model registration and management."""

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field

from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType


class CloudModelNotFoundException(Exception):
    """Raised when a cloud model is not found."""


class CloudModelAlreadyExistsException(Exception):
    """Raised when attempting to register a cloud model that already exists."""


class InvalidCloudProviderException(Exception):
    """Raised when an invalid cloud provider is specified."""


class APIKeyNotFoundException(Exception):
    """Raised when an API key is not found for a cloud provider."""


class CloudModelRegistrationRequest(BaseModel):
    """Request to register a cloud model."""

    name: str = Field(description="Human-readable name for the model")
    provider: CloudProviderType = Field(description="Cloud provider type")
    cloud_model_id: str = Field(description="Model ID on the cloud service")
    source: str = Field(description="Documentation URL or API endpoint")
    description: Optional[str] = Field(default=None, description="Optional description")


CloudModelConfig = GeminiFlashImageConfig | ImagenUltraConfig | OpenAIImageConfig


class CloudModelServiceBase(ABC):
    """Abstract base class for cloud model service."""

    @abstractmethod
    def register_model(self, request: CloudModelRegistrationRequest) -> CloudModelConfig:
        """
        Register a new cloud model.

        Args:
            request: Registration request with provider and model details

        Returns:
            The created model config

        Raises:
            CloudModelAlreadyExistsException: If a model with the same name already exists
            InvalidCloudProviderException: If the provider is not recognized
            APIKeyNotFoundException: If API key validation fails
        """
        pass

    @abstractmethod
    def get_model(self, key: str) -> CloudModelConfig:
        """
        Get a cloud model by key.

        Args:
            key: Model key

        Returns:
            The model config

        Raises:
            CloudModelNotFoundException: If the model is not found
        """
        pass

    @abstractmethod
    def list_models(
        self, provider: Optional[CloudProviderType] = None
    ) -> List[CloudModelConfig]:
        """
        List all cloud models, optionally filtered by provider.

        Args:
            provider: Optional provider filter

        Returns:
            List of cloud model configs
        """
        pass

    @abstractmethod
    def delete_model(self, key: str) -> None:
        """
        Delete a cloud model.

        Args:
            key: Model key

        Raises:
            CloudModelNotFoundException: If the model is not found
        """
        pass

    @abstractmethod
    def validate_api_key(self, provider: CloudProviderType) -> bool:
        """
        Validate that an API key exists for the given provider.

        Args:
            provider: Cloud provider type

        Returns:
            True if API key is available

        Raises:
            APIKeyNotFoundException: If no API key is configured
        """
        pass
