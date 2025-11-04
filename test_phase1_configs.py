#!/usr/bin/env python3
"""Test Phase 1: Verify cloud model config instantiation and discriminated union."""

import sys
from pathlib import Path

# Add InvokeAI to path
sys.path.insert(0, str(Path(__file__).parent))

from invokeai.backend.model_manager.configs.cloud_models import (
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


def test_gemini_config():
    """Test GeminiFlashImageConfig instantiation."""
    print("\n1. Testing GeminiFlashImageConfig instantiation...")

    config = GeminiFlashImageConfig(
        name="Gemini 2.5 Flash Image",
        source="https://ai.google.dev/gemini-api/docs/image-generation",
        source_type=ModelSourceType.CLOUD,
    )

    # Check fields
    assert config.type == ModelType.Main
    assert config.base == BaseModelType.CloudGemini
    assert config.format == ModelFormat.CloudREST
    assert config.provider == CloudProviderType.GoogleGemini
    assert config.cloud_model_id == "gemini-2.5-flash-image"

    # Check that file fields are NOT present
    assert not hasattr(config, "hash")
    assert not hasattr(config, "path")
    assert not hasattr(config, "file_size")

    print("✓ GeminiFlashImageConfig instantiation successful")
    print(f"  - Config key: {config.key}")
    print(f"  - Tag: {config.get_tag()}")
    return config


def test_imagen_config():
    """Test ImagenUltraConfig instantiation."""
    print("\n2. Testing ImagenUltraConfig instantiation...")

    config = ImagenUltraConfig(
        name="Imagen 4 Ultra",
        source="https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api",
        source_type=ModelSourceType.CLOUD,
    )

    # Check fields
    assert config.type == ModelType.Main
    assert config.base == BaseModelType.CloudImagen
    assert config.format == ModelFormat.CloudREST
    assert config.provider == CloudProviderType.GoogleImagen
    assert config.cloud_model_id == "imagen-4.0-ultra-generate-001"

    print("✓ ImagenUltraConfig instantiation successful")
    print(f"  - Config key: {config.key}")
    print(f"  - Tag: {config.get_tag()}")
    return config


def test_openai_config():
    """Test OpenAIImageConfig instantiation."""
    print("\n3. Testing OpenAIImageConfig instantiation...")

    config = OpenAIImageConfig(
        name="DALL-E 3",
        source="https://platform.openai.com/docs/guides/image-generation",
        source_type=ModelSourceType.CLOUD,
        cloud_model_id="dall-e-3",
    )

    # Check fields
    assert config.type == ModelType.Main
    assert config.base == BaseModelType.CloudOpenAI
    assert config.format == ModelFormat.CloudREST
    assert config.provider == CloudProviderType.OpenAI
    assert config.cloud_model_id == "dall-e-3"

    print("✓ OpenAIImageConfig instantiation successful")
    print(f"  - Config key: {config.key}")
    print(f"  - Tag: {config.get_tag()}")
    return config


def test_discriminated_union(gemini_config, imagen_config, openai_config):
    """Test that configs can be serialized/deserialized via discriminated union."""
    print("\n4. Testing discriminated union serialization/deserialization...")

    configs = [gemini_config, imagen_config, openai_config]

    for i, config in enumerate(configs, 1):
        # Serialize to dict
        config_dict = config.model_dump()
        print(f"\n  4.{i}. Testing {config.__class__.__name__}:")
        print(f"     - Serialized discriminator fields: type={config_dict['type']}, format={config_dict['format']}, base={config_dict['base']}")

        # Deserialize via discriminated union
        restored_config = AnyModelConfigValidator.validate_python(config_dict)

        # Verify type is preserved
        assert isinstance(restored_config, config.__class__)
        assert restored_config.key == config.key
        assert restored_config.name == config.name

        print(f"     ✓ Successfully deserialized as {restored_config.__class__.__name__}")

    print("\n✓ Discriminated union test successful")


def test_unique_tags():
    """Test that each cloud config has a unique tag."""
    print("\n5. Testing unique tags...")

    gemini_tag = GeminiFlashImageConfig.get_tag()
    imagen_tag = ImagenUltraConfig.get_tag()
    openai_tag = OpenAIImageConfig.get_tag()

    print(f"  - GeminiFlashImageConfig tag: {gemini_tag}")
    print(f"  - ImagenUltraConfig tag: {imagen_tag}")
    print(f"  - OpenAIImageConfig tag: {openai_tag}")

    # All tags must be unique
    tags = [gemini_tag.tag, imagen_tag.tag, openai_tag.tag]
    assert len(tags) == len(set(tags)), "Tags are not unique!"

    print("✓ All tags are unique")


def main():
    """Run all Phase 1 tests."""
    print("=" * 70)
    print("PHASE 1 CONFIG TESTS")
    print("=" * 70)

    try:
        # Test instantiation
        gemini_config = test_gemini_config()
        imagen_config = test_imagen_config()
        openai_config = test_openai_config()

        # Test unique tags
        test_unique_tags()

        # Test discriminated union
        test_discriminated_union(gemini_config, imagen_config, openai_config)

        print("\n" + "=" * 70)
        print("✅ ALL PHASE 1 TESTS PASSED")
        print("=" * 70)
        return 0

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
