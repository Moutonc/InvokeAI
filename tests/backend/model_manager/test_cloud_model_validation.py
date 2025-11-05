"""Comprehensive validation tests for cloud model Phase 1 and Phase 2."""

import os
from unittest.mock import MagicMock, patch

import pytest

from invokeai.app.services.cloud_models import (
    APIKeyNotFoundException,
    CloudModelAlreadyExistsException,
    CloudModelNotFoundException,
    CloudModelRegistrationRequest,
    CloudModelService,
)
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import (
    BaseModelType,
    CloudProviderType,
    ModelFormat,
    ModelSourceType,
    ModelType,
)


class TestPhase1ArchitectureValidation:
    """Validate Phase 1 architecture implementation."""

    def test_cloud_model_config_base_hierarchy(self):
        """Test that CloudModelConfigBase hierarchy is properly implemented."""
        # All three configs should inherit from CloudModelConfigBase
        from invokeai.backend.model_manager.configs.base import CloudModelConfigBase

        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        # Should be instance of CloudModelConfigBase
        assert isinstance(config, CloudModelConfigBase)

    def test_no_file_fields_on_cloud_configs(self):
        """Test that cloud configs don't have file-related fields."""
        configs = [
            GeminiFlashImageConfig(
                name="Test Gemini",
                source="https://ai.google.dev/",
                source_type=ModelSourceType.CLOUD,
            ),
            ImagenUltraConfig(
                name="Test Imagen",
                source="https://cloud.google.com/",
                source_type=ModelSourceType.CLOUD,
            ),
            OpenAIImageConfig(
                name="Test OpenAI",
                source="https://platform.openai.com/",
                source_type=ModelSourceType.CLOUD,
            ),
        ]

        for config in configs:
            # Should NOT have file fields
            assert not hasattr(config, "hash")
            assert not hasattr(config, "path")
            assert not hasattr(config, "file_size")

            # Serialized form should also not have these fields
            config_dict = config.model_dump()
            assert "hash" not in config_dict
            assert "path" not in config_dict
            assert "file_size" not in config_dict

    def test_unique_base_types_for_discrimination(self):
        """Test that each provider has unique base type."""
        gemini = GeminiFlashImageConfig(
            name="Gemini",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        imagen = ImagenUltraConfig(
            name="Imagen",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        openai = OpenAIImageConfig(
            name="OpenAI",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
        )

        # Each should have unique base type
        assert gemini.base == BaseModelType.CloudGemini
        assert imagen.base == BaseModelType.CloudImagen
        assert openai.base == BaseModelType.CloudOpenAI

        # All bases should be different
        bases = [gemini.base, imagen.base, openai.base]
        assert len(bases) == len(set(bases))

    def test_unique_discriminator_tags(self):
        """Test that each provider has unique discriminator tag."""
        gemini = GeminiFlashImageConfig(
            name="Gemini",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        imagen = ImagenUltraConfig(
            name="Imagen",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        openai = OpenAIImageConfig(
            name="OpenAI",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
        )

        gemini_tag = gemini.get_tag().tag
        imagen_tag = imagen.get_tag().tag
        openai_tag = openai.get_tag().tag

        # All tags should be unique
        tags = [gemini_tag, imagen_tag, openai_tag]
        assert len(tags) == len(set(tags))

        # Tags should have expected format
        assert gemini_tag == "main.cloud_rest.cloud-gemini"
        assert imagen_tag == "main.cloud_rest.cloud-imagen"
        assert openai_tag == "main.cloud_rest.cloud-openai"

    def test_factory_discriminated_union_includes_cloud_configs(self):
        """Test that factory discriminated union includes cloud configs."""
        from invokeai.backend.model_manager.configs.factory import AnyModelConfigValidator

        # Create configs
        configs = [
            GeminiFlashImageConfig(
                name="Gemini",
                source="https://ai.google.dev/",
                source_type=ModelSourceType.CLOUD,
            ),
            ImagenUltraConfig(
                name="Imagen",
                source="https://cloud.google.com/",
                source_type=ModelSourceType.CLOUD,
            ),
            OpenAIImageConfig(
                name="OpenAI",
                source="https://platform.openai.com/",
                source_type=ModelSourceType.CLOUD,
            ),
        ]

        # All should be valid in the union
        for config in configs:
            config_dict = config.model_dump()
            validated = AnyModelConfigValidator.validate_python(config_dict)
            assert type(validated) == type(config)


class TestPhase2ServiceLayerValidation:
    """Validate Phase 2 service layer implementation."""

    @pytest.fixture
    def mock_model_record_service(self):
        """Create mock model record service."""
        return MagicMock()

    @pytest.fixture
    def cloud_service(self, mock_model_record_service):
        """Create cloud model service."""
        return CloudModelService(mock_model_record_service)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_registration_creates_correct_config_type(
        self, cloud_service, mock_model_record_service
    ):
        """Test that registration creates correct config type for each provider."""
        mock_model_record_service.search_by_attr.return_value = []

        def add_model_side_effect(config):
            return config

        mock_model_record_service.add_model.side_effect = add_model_side_effect

        # Test Gemini
        gemini_request = CloudModelRegistrationRequest(
            name="Test Gemini",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        gemini_result = cloud_service.register_model(gemini_request)
        assert isinstance(gemini_result, GeminiFlashImageConfig)
        assert gemini_result.base == BaseModelType.CloudGemini

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"})
    def test_registration_validates_api_keys(
        self, cloud_service, mock_model_record_service
    ):
        """Test that registration validates API keys."""
        mock_model_record_service.search_by_attr.return_value = []

        # Imagen with valid project
        imagen_request = CloudModelRegistrationRequest(
            name="Test Imagen",
            provider=CloudProviderType.GoogleImagen,
            cloud_model_id="imagen-4.0-ultra-generate-001",
            source="https://cloud.google.com/",
        )

        def add_model_side_effect(config):
            return config

        mock_model_record_service.add_model.side_effect = add_model_side_effect

        result = cloud_service.register_model(imagen_request)
        assert isinstance(result, ImagenUltraConfig)

    @patch.dict(os.environ, {}, clear=True)
    def test_registration_fails_without_api_key(
        self, cloud_service, mock_model_record_service
    ):
        """Test that registration fails without API key."""
        request = CloudModelRegistrationRequest(
            name="Test",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        with pytest.raises(APIKeyNotFoundException):
            cloud_service.register_model(request)

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_duplicate_detection(self, cloud_service, mock_model_record_service):
        """Test that service detects duplicate models."""
        # Mock existing model
        existing_config = GeminiFlashImageConfig(
            name="Existing Model",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        mock_model_record_service.search_by_attr.return_value = [existing_config]

        request = CloudModelRegistrationRequest(
            name="Existing Model",
            provider=CloudProviderType.GoogleGemini,
            cloud_model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/",
        )

        with pytest.raises(CloudModelAlreadyExistsException):
            cloud_service.register_model(request)

    def test_list_models_filters_by_provider(
        self, cloud_service, mock_model_record_service
    ):
        """Test that list_models correctly filters by provider."""
        # Create mixed list of models
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

        mock_model_record_service.search_by_attr.return_value = [
            gemini_config,
            imagen_config,
        ]

        # Filter by Gemini
        result = cloud_service.list_models(provider=CloudProviderType.GoogleGemini)
        assert len(result) == 1
        assert isinstance(result[0], GeminiFlashImageConfig)

        # Filter by Imagen
        result = cloud_service.list_models(provider=CloudProviderType.GoogleImagen)
        assert len(result) == 1
        assert isinstance(result[0], ImagenUltraConfig)

    def test_get_model_validates_cloud_model_type(
        self, cloud_service, mock_model_record_service
    ):
        """Test that get_model validates it's a cloud model."""
        from invokeai.backend.model_manager.configs.main import Main_Diffusers_SD1_Config
        from invokeai.backend.model_manager.taxonomy import ModelVariantType, SchedulerPredictionType, ModelSourceType

        # Mock returning a non-cloud model
        sd_config = Main_Diffusers_SD1_Config(
            name="SD Model",
            path="/path/to/model",
            source="test",
            base=BaseModelType.StableDiffusion1,
            hash="fake-hash-123",
            file_size=1000000,
            source_type=ModelSourceType.Path,
            prediction_type=SchedulerPredictionType.Epsilon,
            variant=ModelVariantType.Normal,
        )

        mock_model_record_service.get_model.return_value = sd_config

        with pytest.raises(CloudModelNotFoundException):
            cloud_service.get_model("test-key")

    def test_delete_model_validates_cloud_model_type(
        self, cloud_service, mock_model_record_service
    ):
        """Test that delete_model validates it's a cloud model."""
        from invokeai.backend.model_manager.configs.main import Main_Diffusers_SD1_Config
        from invokeai.backend.model_manager.taxonomy import ModelVariantType, SchedulerPredictionType, ModelSourceType

        # Mock returning a non-cloud model
        sd_config = Main_Diffusers_SD1_Config(
            name="SD Model",
            path="/path/to/model",
            source="test",
            base=BaseModelType.StableDiffusion1,
            hash="fake-hash-123",
            file_size=1000000,
            source_type=ModelSourceType.Path,
            prediction_type=SchedulerPredictionType.Epsilon,
            variant=ModelVariantType.Normal,
        )

        mock_model_record_service.get_model.return_value = sd_config

        with pytest.raises(CloudModelNotFoundException):
            cloud_service.delete_model("test-key")


class TestProviderSpecificFeatures:
    """Test provider-specific features and constraints."""

    def test_gemini_aspect_ratios(self):
        """Test Gemini aspect ratio support."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        # Should have 10 aspect ratios
        assert len(config.supported_aspect_ratios) == 10

        # Check specific ratios
        expected_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"]
        for ratio in expected_ratios:
            assert ratio in config.supported_aspect_ratios

        # Should support seed
        assert config.supports_seed is True

        # Should NOT support negative prompt
        assert config.supports_negative_prompt is False

    def test_imagen_batch_and_safety(self):
        """Test Imagen batch generation and safety features."""
        config = ImagenUltraConfig(
            name="Test",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        # Batch generation support
        assert config.max_batch_size == 4

        # Safety features
        assert len(config.safety_levels) == 3
        assert "block_medium_and_above" in config.safety_levels

        # SynthID watermark
        assert config.supports_synthid_watermark is True

        # Prompt enhancement
        assert config.supports_prompt_enhancement is True

    def test_openai_quality_and_style(self):
        """Test OpenAI quality and style options."""
        config = OpenAIImageConfig(
            name="Test",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
        )

        # Quality options
        assert len(config.quality_options) == 2
        assert "standard" in config.quality_options
        assert "hd" in config.quality_options

        # Style options
        assert len(config.style_options) == 2
        assert "vivid" in config.style_options
        assert "natural" in config.style_options

        # DALL-E 3 constraints
        assert config.max_batch_size == 1  # No batch for DALL-E 3
        assert config.supports_seed is False  # No seed support
        assert config.supports_revised_prompt is True  # GPT-4 enhancement


class TestBackwardsCompatibility:
    """Test backwards compatibility and migration."""

    def test_existing_provider_implementations_unchanged(self):
        """Test that existing provider implementations are not affected."""
        # Provider implementations should still exist and work
        from invokeai.app.services.cloud_providers.google_gemini_provider import (
            GoogleGeminiProvider,
        )
        from invokeai.app.services.cloud_providers.google_imagen_provider import (
            GoogleImagenProvider,
        )
        from invokeai.app.services.cloud_providers.openai_provider import (
            OpenAIProvider,
        )

        # Should be importable
        assert GoogleGeminiProvider is not None
        assert GoogleImagenProvider is not None
        assert OpenAIProvider is not None

    def test_existing_loaders_unchanged(self):
        """Test that existing model loaders are not affected."""
        from invokeai.backend.model_manager.load.model_loaders.cloud_model_loader import (
            CloudModelLoader,
        )

        # Should be importable
        assert CloudModelLoader is not None

    def test_existing_invocations_unchanged(self):
        """Test that existing invocation nodes are not affected."""
        from invokeai.app.invocations.gemini_text_to_image import (
            GeminiTextToImageInvocation,
        )

        # Should be importable
        assert GeminiTextToImageInvocation is not None
