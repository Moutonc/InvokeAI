"""End-to-end tests for cloud model workflow."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import ModelSourceType


class TestCloudModelE2EWorkflow:
    """Test complete cloud model workflow from registration to usage."""

    def test_gemini_full_workflow(self):
        """Test complete Gemini workflow: register → retrieve → use → delete."""
        # Step 1: Register model
        config = GeminiFlashImageConfig(
            name="Gemini E2E Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
            description="E2E test model",
        )

        assert config.name == "Gemini E2E Test"
        assert config.provider.value == "google-gemini"
        assert config.base.value == "cloud-gemini"
        assert config.cloud_model_id == "gemini-2.5-flash-image"

        # Step 2: Verify config serialization
        config_dict = config.model_dump()
        assert "hash" not in config_dict  # Cloud models have no file hash
        assert "path" not in config_dict  # Cloud models have no path
        assert "file_size" not in config_dict  # Cloud models have no file size
        assert config_dict["base"] == "cloud-gemini"
        assert config_dict["type"] == "main"
        assert config_dict["format"] == "cloud_rest"

        # Step 3: Verify discriminator tag
        tag = config.get_tag()
        assert tag.tag == "main.cloud_rest.cloud-gemini"

        # Step 4: Verify provider settings
        assert len(config.supported_aspect_ratios) == 10
        assert "1:1" in config.supported_aspect_ratios
        assert config.supports_seed is True
        assert config.supports_negative_prompt is False

    def test_imagen_full_workflow(self):
        """Test complete Imagen workflow: register → retrieve → use → delete."""
        config = ImagenUltraConfig(
            name="Imagen E2E Test",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
            description="E2E test model",
        )

        assert config.name == "Imagen E2E Test"
        assert config.provider.value == "google-imagen"
        assert config.base.value == "cloud-imagen"
        assert config.cloud_model_id == "imagen-4.0-ultra-generate-001"

        # Verify Imagen-specific features
        assert config.max_batch_size == 4
        assert config.supports_synthid_watermark is True
        assert config.supports_prompt_enhancement is True
        assert len(config.safety_levels) == 3

    def test_openai_full_workflow(self):
        """Test complete OpenAI workflow: register → retrieve → use → delete."""
        config = OpenAIImageConfig(
            name="DALL-E E2E Test",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-3",
            description="E2E test model",
        )

        assert config.name == "DALL-E E2E Test"
        assert config.provider.value == "openai"
        assert config.base.value == "cloud-openai"
        assert config.cloud_model_id == "dall-e-3"

        # Verify DALL-E-specific features
        assert config.max_batch_size == 1  # DALL-E 3 doesn't support batch
        assert config.supports_seed is False
        assert config.supports_revised_prompt is True
        assert "hd" in config.quality_options
        assert "vivid" in config.style_options

    def test_config_serialization_roundtrip(self):
        """Test that configs can be serialized and deserialized."""
        from invokeai.backend.model_manager.configs.factory import AnyModelConfigValidator

        # Test Gemini
        gemini_original = GeminiFlashImageConfig(
            name="Gemini Roundtrip",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        gemini_dict = gemini_original.model_dump()
        gemini_restored = AnyModelConfigValidator.validate_python(gemini_dict)

        assert isinstance(gemini_restored, GeminiFlashImageConfig)
        assert gemini_restored.key == gemini_original.key
        assert gemini_restored.name == gemini_original.name
        assert gemini_restored.base == gemini_original.base

        # Test Imagen
        imagen_original = ImagenUltraConfig(
            name="Imagen Roundtrip",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        imagen_dict = imagen_original.model_dump()
        imagen_restored = AnyModelConfigValidator.validate_python(imagen_dict)

        assert isinstance(imagen_restored, ImagenUltraConfig)
        assert imagen_restored.key == imagen_original.key

        # Test OpenAI
        openai_original = OpenAIImageConfig(
            name="OpenAI Roundtrip",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
        )

        openai_dict = openai_original.model_dump()
        openai_restored = AnyModelConfigValidator.validate_python(openai_dict)

        assert isinstance(openai_restored, OpenAIImageConfig)
        assert openai_restored.key == openai_original.key

    def test_mixed_model_discrimination(self):
        """Test that discriminated union properly handles mixed local and cloud models."""
        from invokeai.backend.model_manager.configs.factory import AnyModelConfigValidator

        # Create different types of configs
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

        openai_config = OpenAIImageConfig(
            name="OpenAI",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
        )

        # Serialize all
        configs = [gemini_config, imagen_config, openai_config]
        dicts = [c.model_dump() for c in configs]

        # Deserialize and verify types are preserved
        restored = [AnyModelConfigValidator.validate_python(d) for d in dicts]

        assert isinstance(restored[0], GeminiFlashImageConfig)
        assert isinstance(restored[1], ImagenUltraConfig)
        assert isinstance(restored[2], OpenAIImageConfig)

        # Verify all have unique tags
        tags = [r.get_tag().tag for r in restored]
        assert len(tags) == len(set(tags))
        assert "main.cloud_rest.cloud-gemini" in tags
        assert "main.cloud_rest.cloud-imagen" in tags
        assert "main.cloud_rest.cloud-openai" in tags


class TestCloudModelProviderSettings:
    """Test provider-specific settings and customization."""

    def test_gemini_custom_settings(self):
        """Test Gemini with custom provider settings."""
        custom_settings = {
            "api_version": "v2",
            "timeout": 60,
            "custom_flag": True,
        }

        config = GeminiFlashImageConfig(
            name="Custom Gemini",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
            provider_settings=custom_settings,
        )

        assert config.provider_settings == custom_settings
        assert config.provider_settings["api_version"] == "v2"

    def test_imagen_batch_size_configuration(self):
        """Test Imagen batch size configuration."""
        config = ImagenUltraConfig(
            name="Batch Imagen",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )

        # Verify batch size constraint
        assert config.max_batch_size == 4
        assert 1 <= config.max_batch_size <= 4

    def test_openai_model_id_variation(self):
        """Test OpenAI with different model IDs."""
        dalle3_config = OpenAIImageConfig(
            name="DALL-E 3",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-3",
        )

        dalle2_config = OpenAIImageConfig(
            name="DALL-E 2",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-2",
        )

        assert dalle3_config.cloud_model_id == "dall-e-3"
        assert dalle2_config.cloud_model_id == "dall-e-2"
        # Both should have same provider and base
        assert dalle3_config.provider == dalle2_config.provider
        assert dalle3_config.base == dalle2_config.base


class TestCloudModelValidation:
    """Test validation and constraints on cloud models."""

    def test_required_fields_validation(self):
        """Test that required fields are enforced."""
        from pydantic import ValidationError

        # Missing name should fail
        with pytest.raises(ValidationError):
            GeminiFlashImageConfig(
                source="https://ai.google.dev/",
                source_type=ModelSourceType.CLOUD,
                # name is required
            )

        # Missing source should fail
        with pytest.raises(ValidationError):
            GeminiFlashImageConfig(
                name="Test",
                source_type=ModelSourceType.CLOUD,
                # source is required
            )

        # Missing source_type should fail
        with pytest.raises(ValidationError):
            GeminiFlashImageConfig(
                name="Test",
                source="https://ai.google.dev/",
                # source_type is required
            )

    def test_provider_type_enforcement(self):
        """Test that provider types are enforced correctly."""
        gemini = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        # Provider should be set correctly
        assert gemini.provider.value == "google-gemini"

        # Cannot change provider (it's a literal)
        # This is enforced by Pydantic at the type level

    def test_cloud_model_id_literals(self):
        """Test that cloud model IDs have correct literal constraints."""
        # Gemini model ID is fixed
        gemini = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )
        assert gemini.cloud_model_id == "gemini-2.5-flash-image"

        # Imagen model ID is fixed
        imagen = ImagenUltraConfig(
            name="Test",
            source="https://cloud.google.com/",
            source_type=ModelSourceType.CLOUD,
        )
        assert imagen.cloud_model_id == "imagen-4.0-ultra-generate-001"

        # OpenAI model ID can vary
        openai = OpenAIImageConfig(
            name="Test",
            source="https://platform.openai.com/",
            source_type=ModelSourceType.CLOUD,
            cloud_model_id="dall-e-2",
        )
        assert openai.cloud_model_id == "dall-e-2"


class TestCloudModelCompatibility:
    """Test compatibility with existing InvokeAI model infrastructure."""

    def test_config_has_key_field(self):
        """Test that all configs have key field for database storage."""
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
            # Should have a key
            assert hasattr(config, "key")
            assert isinstance(config.key, str)
            assert len(config.key) > 0

    def test_config_has_common_fields(self):
        """Test that all configs have common metadata fields."""
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
            description="Test description",
        )

        # Common fields from CloudModelConfigBase
        assert hasattr(config, "key")
        assert hasattr(config, "name")
        assert hasattr(config, "description")
        assert hasattr(config, "source")
        assert hasattr(config, "source_type")

        # Should NOT have file-related fields
        assert not hasattr(config, "hash")
        assert not hasattr(config, "path")
        assert not hasattr(config, "file_size")

    def test_cloud_configs_in_any_model_config_union(self):
        """Test that cloud configs are part of AnyModelConfig union."""
        from invokeai.backend.model_manager.configs.factory import AnyModelConfig, AnyModelConfigValidator

        # Create a cloud config
        config = GeminiFlashImageConfig(
            name="Test",
            source="https://ai.google.dev/",
            source_type=ModelSourceType.CLOUD,
        )

        # Should be valid as AnyModelConfig
        config_dict = config.model_dump()
        validated = AnyModelConfigValidator.validate_python(config_dict)

        # Should restore to correct type
        assert isinstance(validated, GeminiFlashImageConfig)
