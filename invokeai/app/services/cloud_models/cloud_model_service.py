"""Cloud model registration and management service implementation."""

import os
from typing import List, Optional

from invokeai.app.services.cloud_models.cloud_model_service_base import (
    APIKeyNotFoundException,
    CloudModelAlreadyExistsException,
    CloudModelConfig,
    CloudModelNotFoundException,
    CloudModelRegistrationRequest,
    CloudModelServiceBase,
    InvalidCloudProviderException,
)
from invokeai.app.services.model_records import (
    DuplicateModelException,
    ModelRecordServiceBase,
    UnknownModelException,
)
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import (
    BaseModelType,
    CloudProviderType,
    ModelSourceType,
)


class CloudModelService(CloudModelServiceBase):
    """Service for managing cloud model registrations."""

    def __init__(self, model_record_service: ModelRecordServiceBase):
        """
        Initialize the cloud model service.

        Args:
            model_record_service: The model record service for persistence
        """
        self._model_records = model_record_service

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
        # Validate API key for the provider
        self.validate_api_key(request.provider)

        # Check if model with same name already exists
        existing_models = self._model_records.search_by_attr(model_name=request.name)
        if any(
            isinstance(m, (GeminiFlashImageConfig, ImagenUltraConfig, OpenAIImageConfig))
            for m in existing_models
        ):
            raise CloudModelAlreadyExistsException(
                f"Cloud model with name '{request.name}' already exists"
            )

        # Create the appropriate config based on provider
        config: CloudModelConfig
        if request.provider == CloudProviderType.GoogleGemini:
            config = GeminiFlashImageConfig(
                name=request.name,
                source=request.source,
                source_type=ModelSourceType.CLOUD,
                description=request.description,
                cloud_model_id=request.cloud_model_id,
            )
        elif request.provider == CloudProviderType.GoogleImagen:
            config = ImagenUltraConfig(
                name=request.name,
                source=request.source,
                source_type=ModelSourceType.CLOUD,
                description=request.description,
                cloud_model_id=request.cloud_model_id,
            )
        elif request.provider == CloudProviderType.OpenAI:
            config = OpenAIImageConfig(
                name=request.name,
                source=request.source,
                source_type=ModelSourceType.CLOUD,
                description=request.description,
                cloud_model_id=request.cloud_model_id,
            )
        else:
            raise InvalidCloudProviderException(
                f"Unsupported cloud provider: {request.provider}"
            )

        # Register with model record service
        try:
            return self._model_records.add_model(config)
        except DuplicateModelException as e:
            raise CloudModelAlreadyExistsException(str(e)) from e

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
        try:
            model = self._model_records.get_model(key)
            if not isinstance(model, (GeminiFlashImageConfig, ImagenUltraConfig, OpenAIImageConfig)):
                raise CloudModelNotFoundException(
                    f"Model with key '{key}' is not a cloud model"
                )
            return model
        except UnknownModelException as e:
            raise CloudModelNotFoundException(str(e)) from e

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
        # Get all models and filter for cloud models
        all_models = self._model_records.search_by_attr()
        cloud_models = [
            m
            for m in all_models
            if isinstance(m, (GeminiFlashImageConfig, ImagenUltraConfig, OpenAIImageConfig))
        ]

        # Apply provider filter if specified
        if provider is not None:
            if provider == CloudProviderType.GoogleGemini:
                cloud_models = [m for m in cloud_models if m.base == BaseModelType.CloudGemini]
            elif provider == CloudProviderType.GoogleImagen:
                cloud_models = [m for m in cloud_models if m.base == BaseModelType.CloudImagen]
            elif provider == CloudProviderType.OpenAI:
                cloud_models = [m for m in cloud_models if m.base == BaseModelType.CloudOpenAI]

        return cloud_models

    def delete_model(self, key: str) -> None:
        """
        Delete a cloud model.

        Args:
            key: Model key

        Raises:
            CloudModelNotFoundException: If the model is not found
        """
        # Verify it's a cloud model before deleting
        self.get_model(key)  # Raises CloudModelNotFoundException if not found or not cloud

        try:
            self._model_records.del_model(key)
        except UnknownModelException as e:
            raise CloudModelNotFoundException(str(e)) from e

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
        env_var_name = self._get_api_key_env_var(provider)
        api_key = os.getenv(env_var_name)

        if not api_key:
            raise APIKeyNotFoundException(
                f"API key not found for {provider.value}. "
                f"Please set {env_var_name} in .env file or environment variables."
            )

        return True

    @staticmethod
    def _get_api_key_env_var(provider: CloudProviderType) -> str:
        """Get the environment variable name for a provider's API key."""
        if provider == CloudProviderType.GoogleGemini:
            return "GOOGLE_API_KEY"
        elif provider == CloudProviderType.GoogleImagen:
            # Imagen uses Application Default Credentials, check for project ID
            return "GOOGLE_CLOUD_PROJECT"
        elif provider == CloudProviderType.OpenAI:
            return "OPENAI_API_KEY"
        else:
            raise InvalidCloudProviderException(f"Unknown provider: {provider}")
