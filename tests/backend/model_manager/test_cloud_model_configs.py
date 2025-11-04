"""Tests for cloud model configurations (Phase 1).

Tests the CloudModelConfigBase hierarchy and cloud provider configs:
- GeminiFlashImageConfig
- ImagenUltraConfig
- OpenAIImageConfig

Verifies:
1. Config instantiation
2. Discriminated union serialization/deserialization
3. Unique discriminator tags
4. No file-related fields required
5. Factory integration
"""

import pytest
from pydantic import ValidationError

from invokeai.backend.model_manager.configs.cloud_models import (
    CloudModelConfig,
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.configs.factory import AnyModelConfigValidator
from invokeai.backend.model_manager.taxonomy import (
    BaseModelType,
    CloudProviderType,
    ModelFormat,
    ModelSourceType,
    ModelType,
)


class TestCloudModelConfigInstantiation:
    """Test cloud model config creation."""

    def test_gemini_config_creation(self):
        """Test GeminiFlashImageConfig can be instantiated."""
        config = GeminiFlashImageConfig(
            name="Gemini 2.5 Flash Image",
            source="https://ai.google.dev/gemini-api/docs/image-generation",
            source_type=ModelSourceType.CLOUD,
        )

        assert config.name == "Gemini 2.5 Flash Image"
        assert config.type == ModelType.Main
        assert config.base == BaseModelType.CloudGemini
        assert config.format == ModelFormat.CloudREST
        assert config.provider == CloudProviderType.GoogleGemini
        assert config.cloud_model_id == "gemini-2.5-flash-image"
        assert config.source_type == ModelSourceType.CLOUD

    def test_imagen_config_creation(self):
        """Test ImagenUltraConfig can be instantiated."""
        config = ImagenUltraConfig(
            name="Imagen 4 Ultra",
            source="https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api",
            source_type=ModelSourceType.CLOUD,
        )

        assert config.name == "Imagen 4 Ultra"
        assert config.type == ModelType.Main
        assert config.base == BaseModelType.CloudImagen
        assert config.format == ModelFormat.CloudREST
        assert config.provider == CloudProviderType.GoogleImagen
        assert config.cloud_model_id == "imagen-4.0-ultra-generate-001"

    def test_openai_config_creation(self):
        """Test OpenAIImageConfig can be instantiated."""
        config = OpenAIImageConfig(
            name="DALL-E 3",
            source="https://platform.openai.com/docs/guides/image-generation",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-3",
        )

        assert config.name == "DALL-E 3"
        assert config.type == ModelType.Main
        assert config.base == BaseModelType.CloudOpenAI
        assert config.format == ModelFormat.CloudREST
        assert config.provider == CloudProviderType.OpenAI
        assert config.cloud_model_id == "dall-e-3"

    def test_openai_config_with_dalle2(self):
        """Test OpenAIImageConfig with DALL-E 2."""
        config = OpenAIImageConfig(
            name="DALL-E 2",
            source="https://platform.openai.com/docs/guides/image-generation",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-2",
        )

        assert config.cloud_model_id == "dall-e-2"


class TestCloudModelConfigFields:
    """Test cloud model configs don't have file-related fields."""

    def test_no_file_fields_on_gemini(self):
        """GeminiFlashImageConfig should not have file-related fields."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        # These fields should NOT exist
        assert not hasattr(config, "hash")
        assert not hasattr(config, "path")
        assert not hasattr(config, "file_size")

    def test_no_file_fields_on_imagen(self):
        """ImagenUltraConfig should not have file-related fields."""
        config = ImagenUltraConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        assert not hasattr(config, "hash")
        assert not hasattr(config, "path")
        assert not hasattr(config, "file_size")

    def test_no_file_fields_on_openai(self):
        """OpenAIImageConfig should not have file-related fields."""
        config = OpenAIImageConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        assert not hasattr(config, "hash")
        assert not hasattr(config, "path")
        assert not hasattr(config, "file_size")


class TestCloudModelConfigTags:
    """Test discriminator tags for cloud configs."""

    def test_unique_tags(self):
        """Each cloud config should have a unique tag."""
        gemini_tag = GeminiFlashImageConfig.get_tag().tag
        imagen_tag = ImagenUltraConfig.get_tag().tag
        openai_tag = OpenAIImageConfig.get_tag().tag

        tags = [gemini_tag, imagen_tag, openai_tag]

        # All tags must be unique
        assert len(tags) == len(set(tags)), f"Tags are not unique: {tags}"

    def test_gemini_tag_format(self):
        """GeminiFlashImageConfig should have expected tag format."""
        tag = GeminiFlashImageConfig.get_tag().tag
        assert tag == "main.cloud_rest.cloud-gemini"

    def test_imagen_tag_format(self):
        """ImagenUltraConfig should have expected tag format."""
        tag = ImagenUltraConfig.get_tag().tag
        assert tag == "main.cloud_rest.cloud-imagen"

    def test_openai_tag_format(self):
        """OpenAIImageConfig should have expected tag format."""
        tag = OpenAIImageConfig.get_tag().tag
        assert tag == "main.cloud_rest.cloud-openai"


class TestCloudModelConfigSerialization:
    """Test cloud config serialization/deserialization via discriminated union."""

    def test_gemini_roundtrip(self):
        """Test GeminiFlashImageConfig serialization roundtrip."""
        original = GeminiFlashImageConfig(
            name="Gemini Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        # Serialize to dict
        config_dict = original.model_dump()

        # Deserialize via discriminated union
        restored = AnyModelConfigValidator.validate_python(config_dict)

        # Should restore to correct type
        assert isinstance(restored, GeminiFlashImageConfig)
        assert restored.key == original.key
        assert restored.name == original.name
        assert restored.base == BaseModelType.CloudGemini

    def test_imagen_roundtrip(self):
        """Test ImagenUltraConfig serialization roundtrip."""
        original = ImagenUltraConfig(
            name="Imagen Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        config_dict = original.model_dump()
        restored = AnyModelConfigValidator.validate_python(config_dict)

        assert isinstance(restored, ImagenUltraConfig)
        assert restored.key == original.key
        assert restored.name == original.name
        assert restored.base == BaseModelType.CloudImagen

    def test_openai_roundtrip(self):
        """Test OpenAIImageConfig serialization roundtrip."""
        original = OpenAIImageConfig(
            name="OpenAI Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        config_dict = original.model_dump()
        restored = AnyModelConfigValidator.validate_python(config_dict)

        assert isinstance(restored, OpenAIImageConfig)
        assert restored.key == original.key
        assert restored.name == original.name
        assert restored.base == BaseModelType.CloudOpenAI

    def test_discriminator_distinguishes_providers(self):
        """Test discriminator properly distinguishes between cloud providers."""
        gemini = GeminiFlashImageConfig(
            name="Gemini",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )
        imagen = ImagenUltraConfig(
            name="Imagen",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )
        openai = OpenAIImageConfig(
            name="OpenAI",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        # Serialize all configs
        configs = [gemini, imagen, openai]
        config_dicts = [c.model_dump() for c in configs]

        # Deserialize and verify types are preserved
        restored = [AnyModelConfigValidator.validate_python(d) for d in config_dicts]

        assert isinstance(restored[0], GeminiFlashImageConfig)
        assert isinstance(restored[1], ImagenUltraConfig)
        assert isinstance(restored[2], OpenAIImageConfig)


class TestCloudModelConfigProviderSettings:
    """Test provider-specific settings."""

    def test_gemini_aspect_ratios(self):
        """Test Gemini config has correct aspect ratios."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        assert "1:1" in config.supported_aspect_ratios
        assert "16:9" in config.supported_aspect_ratios
        assert len(config.supported_aspect_ratios) == 10

    def test_imagen_safety_levels(self):
        """Test Imagen config has correct safety levels."""
        config = ImagenUltraConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        assert "block_low_and_above" in config.safety_levels
        assert "block_medium_and_above" in config.safety_levels
        assert "block_only_high" in config.safety_levels

    def test_openai_quality_options(self):
        """Test OpenAI config has correct quality options."""
        config = OpenAIImageConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
        )

        assert "standard" in config.quality_options
        assert "hd" in config.quality_options

    def test_provider_settings_customization(self):
        """Test provider_settings can be customized."""
        custom_settings = {
            "api_version": "v2",
            "timeout": 60,
        }

        config = GeminiFlashImageConfig(
            name="Test",
            source="https://example.com",
            source_type=ModelSourceType.CLOUD,
            provider_settings=custom_settings,
        )

        assert config.provider_settings == custom_settings
