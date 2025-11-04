#!/usr/bin/env python3
"""Basic Phase 1 test - config instantiation with minimal dependencies."""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("PHASE 1 BASIC CONFIG INSTANTIATION TEST")
print("=" * 70)
print()

try:
    # Test imports
    print("1. Testing imports...")
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
    print("✓ All imports successful")
    print()

    # Test Gemini config
    print("2. Testing GeminiFlashImageConfig instantiation...")
    gemini = GeminiFlashImageConfig(
        name="Gemini 2.5 Flash",
        source="https://ai.google.dev/gemini-api/docs/image-generation",
        source_type=ModelSourceType.CLOUD,
    )
    assert gemini.base == BaseModelType.CloudGemini
    assert gemini.provider == CloudProviderType.GoogleGemini
    assert gemini.cloud_model_id == "gemini-2.5-flash-image"
    assert not hasattr(gemini, "hash")
    assert not hasattr(gemini, "path")
    print(f"✓ Created Gemini config: {gemini.name}")
    print(f"  Key: {gemini.key}")
    print(f"  Tag: {gemini.get_tag().tag}")
    print()

    # Test Imagen config
    print("3. Testing ImagenUltraConfig instantiation...")
    imagen = ImagenUltraConfig(
        name="Imagen 4 Ultra",
        source="https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api",
        source_type=ModelSourceType.CLOUD,
    )
    assert imagen.base == BaseModelType.CloudImagen
    assert imagen.provider == CloudProviderType.GoogleImagen
    assert imagen.cloud_model_id == "imagen-4.0-ultra-generate-001"
    print(f"✓ Created Imagen config: {imagen.name}")
    print(f"  Key: {imagen.key}")
    print(f"  Tag: {imagen.get_tag().tag}")
    print()

    # Test OpenAI config
    print("4. Testing OpenAIImageConfig instantiation...")
    openai = OpenAIImageConfig(
        name="DALL-E 3",
        source="https://platform.openai.com/docs/guides/image-generation",
        source_type=ModelSourceType.CLOUD,
        cloud_model_id="dall-e-3",
    )
    assert openai.base == BaseModelType.CloudOpenAI
    assert openai.provider == CloudProviderType.OpenAI
    assert openai.cloud_model_id == "dall-e-3"
    print(f"✓ Created OpenAI config: {openai.name}")
    print(f"  Key: {openai.key}")
    print(f"  Tag: {openai.get_tag().tag}")
    print()

    # Test unique tags
    print("5. Testing unique discriminator tags...")
    tags = [
        gemini.get_tag().tag,
        imagen.get_tag().tag,
        openai.get_tag().tag,
    ]
    assert len(tags) == len(set(tags)), f"Tags are not unique: {tags}"
    print(f"✓ All tags are unique:")
    for tag in tags:
        print(f"  - {tag}")
    print()

    # Test serialization
    print("6. Testing serialization...")
    gemini_dict = gemini.model_dump()
    assert "base" in gemini_dict
    assert "type" in gemini_dict
    assert "format" in gemini_dict
    assert gemini_dict["base"] == "cloud-gemini"
    assert gemini_dict["type"] == "main"
    assert gemini_dict["format"] == "cloud_rest"
    assert "hash" not in gemini_dict
    assert "path" not in gemini_dict
    print("✓ Serialization works correctly")
    print(f"  Discriminator fields: base={gemini_dict['base']}, type={gemini_dict['type']}, format={gemini_dict['format']}")
    print()

    print("=" * 70)
    print("✅ ALL BASIC TESTS PASSED")
    print("=" * 70)
    print()
    print("Summary:")
    print("- All three cloud configs instantiate correctly")
    print("- No file fields (hash, path, file_size) present")
    print("- Unique discriminator tags generated")
    print("- Serialization includes correct discriminator fields")
    print()
    sys.exit(0)

except Exception as e:
    print()
    print("=" * 70)
    print(f"❌ TEST FAILED: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()
    sys.exit(1)
