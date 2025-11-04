"""Tests for cloud model service (Phase 2)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from invokeai.app.services.cloud_models import (
    APIKeyNotFoundException,
    CloudModelAlreadyExistsException,
    CloudModelNotFoundException,
    CloudModelRegistrationRequest,
    CloudModelService,
    InvalidCloudProviderException,
)
from invokeai.app.services.model_records import DuplicateModelException, UnknownModelException
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType, ModelSourceType


@pytest.fixture
def mock_model_record_service():
    """Create a mock model record service."""
    return MagicMock()


@pytest.fixture
def cloud_service(mock_model_record_service):
    """Create a cloud model service with mocked dependencies."""
    return CloudModelService(mock_model_record_service)


class TestCloudModelServiceRegistration:
    """Test cloud model registration."""

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_register_gemini_model(self, cloud_service, mock_model_record_service):
        """Test registering a Gemini model."""
        request = CloudModelRegistrationRequest(
            name="Test Gemini",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        # Mock no existing models
        mock_model_record_service.search_by_attr.return_value = []

        # Mock add_model to return the config
        def add_model_side_effect(config):
            return config

        mock_model_record_service.add_model.side_effect = add_model_side_effect

        result = cloud_service.register_model(request)

        assert isinstance(result, GeminiFlashImageConfig)
        assert result.name == "Test Gemini"
        assert result.source_type == ModelSourceType.CLOUD
        mock_model_record_service.add_model.assert_called_once()

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"})
    def test_register_imagen_model(self, cloud_service, mock_model_record_service):
        """Test registering an Imagen model."""
        request = CloudModelRegistrationRequest(
            name="Test Imagen",
            provider=CloudProviderType.GoogleImagen,
            cloud_model_id="imagen-4.0-ultra-generate-001",
            source="https://cloud.google.com/",
        )

        mock_model_record_service.search_by_attr.return_value = []

        def add_model_side_effect(config):
            return config

        mock_model_record_service.add_model.side_effect = add_model_side_effect

        result = cloud_service.register_model(request)

        assert isinstance(result, ImagenUltraConfig)
        assert result.name == "Test Imagen"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_register_openai_model(self, cloud_service, mock_model_record_service):
        """Test registering an OpenAI model."""
        request = CloudModelRegistrationRequest(
            name="Test DALL-E",
            provider=CloudProviderType.OpenAI,
            cloud_model_id="dall-e-3",
            source="https://platform.openai.com/",
        )

        mock_model_record_service.search_by_attr.return_value = []

        def add_model_side_effect(config):
            return config

        mock_model_record_service.add_model.side_effect = add_model_side_effect

        result = cloud_service.register_model(request)

        assert isinstance(result, OpenAIImageConfig)
        assert result.name == "Test DALL-E"
        assert result.cloud_model_id == "dall-e-3"

    @patch.dict(os.environ, {}, clear=True)
    def test_register_without_api_key_fails(self, cloud_service, mock_model_record_service):
        """Test that registration fails without API key."""
        request = CloudModelRegistrationRequest(
            name="Test Gemini",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        with pytest.raises(APIKeyNotFoundException):
            cloud_service.register_model(request)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_register_duplicate_model_fails(self, cloud_service, mock_model_record_service):
        """Test that registering a duplicate model fails."""
        request = CloudModelRegistrationRequest(
            name="Existing Model",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        # Mock existing model with same name
        existing_config = GeminiFlashImageConfig(
            name="Existing Model",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        mock_model_record_service.search_by_attr.return_value = [existing_config]

        with pytest.raises(CloudModelAlreadyExistsException):
            cloud_service.register_model(request)


class TestCloudModelServiceRetrieval:
    """Test cloud model retrieval."""

    def test_get_model_success(self, cloud_service, mock_model_record_service):
        """Test getting a cloud model by key."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        mock_model_record_service.get_model.return_value = config

        result = cloud_service.get_model("test-key")

        assert result == config
        mock_model_record_service.get_model.assert_called_once_with("test-key")

    def test_get_model_not_found(self, cloud_service, mock_model_record_service):
        """Test getting a non-existent model."""
        mock_model_record_service.get_model.side_effect = UnknownModelException("Not found")

        with pytest.raises(CloudModelNotFoundException):
            cloud_service.get_model("nonexistent-key")

    def test_list_models_all(self, cloud_service, mock_model_record_service):
        """Test listing all cloud models."""
        gemini_config = GeminiFlashImageConfig(
            name="Gemini",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        imagen_config = ImagenUltraConfig(
            name="Imagen",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        mock_model_record_service.search_by_attr.return_value = [gemini_config, imagen_config]

        result = cloud_service.list_models()

        assert len(result) == 2
        assert gemini_config in result
        assert imagen_config in result

    def test_list_models_filtered_by_provider(self, cloud_service, mock_model_record_service):
        """Test listing models filtered by provider."""
        gemini_config = GeminiFlashImageConfig(
            name="Gemini",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        imagen_config = ImagenUltraConfig(
            name="Imagen",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        mock_model_record_service.search_by_attr.return_value = [gemini_config, imagen_config]

        result = cloud_service.list_models(provider=CloudProviderType.GoogleGemini)

        # Should only return Gemini models
        assert len(result) == 1
        assert result[0] == gemini_config


class TestCloudModelServiceDeletion:
    """Test cloud model deletion."""

    def test_delete_model_success(self, cloud_service, mock_model_record_service):
        """Test deleting a cloud model."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        mock_model_record_service.get_model.return_value = config

        cloud_service.delete_model("test-key")

        mock_model_record_service.del_model.assert_called_once_with("test-key")

    def test_delete_model_not_found(self, cloud_service, mock_model_record_service):
        """Test deleting a non-existent model."""
        mock_model_record_service.get_model.side_effect = UnknownModelException("Not found")

        with pytest.raises(CloudModelNotFoundException):
            cloud_service.delete_model("nonexistent-key")


class TestAPIKeyValidation:
    """Test API key validation."""

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_validate_gemini_api_key(self, cloud_service):
        """Test validating Gemini API key."""
        result = cloud_service.validate_api_key(CloudProviderType.GoogleGemini)
        assert result is True

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"})
    def test_validate_imagen_api_key(self, cloud_service):
        """Test validating Imagen project."""
        result = cloud_service.validate_api_key(CloudProviderType.GoogleImagen)
        assert result is True

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"})
    def test_validate_openai_api_key(self, cloud_service):
        """Test validating OpenAI API key."""
        result = cloud_service.validate_api_key(CloudProviderType.OpenAI)
        assert result is True

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_missing_api_key(self, cloud_service):
        """Test validation fails when API key is missing."""
        with pytest.raises(APIKeyNotFoundException):
            cloud_service.validate_api_key(CloudProviderType.GoogleGemini)
