#!/usr/bin/env python3
"""Standalone Phase 1 test - validates config structure without full dependencies."""

import sys
from pathlib import Path

# Test basic Python imports work
print("=" * 70)
print("PHASE 1 STANDALONE VALIDATION")
print("=" * 70)
print()

tests_passed = 0
tests_failed = 0

def test(name, condition, error_msg=""):
    """Simple test helper."""
    global tests_passed, tests_failed
    if condition:
        print(f"✓ {name}")
        tests_passed += 1
        return True
    else:
        print(f"✗ {name}")
        if error_msg:
            print(f"  Error: {error_msg}")
        tests_failed += 1
        return False

# Test 1: Verify files exist
print("1. Checking modified files exist...")
files_to_check = [
    "invokeai/backend/model_manager/configs/base.py",
    "invokeai/backend/model_manager/configs/cloud_models.py",
    "invokeai/backend/model_manager/taxonomy.py",
    "invokeai/backend/model_manager/configs/factory.py",
]

for file in files_to_check:
    path = Path(file)
    test(f"  {file}", path.exists(), f"File not found: {path}")

# Test 2: Verify CloudModelConfigBase exists in base.py
print("\n2. Checking CloudModelConfigBase in base.py...")
base_py = Path("invokeai/backend/model_manager/configs/base.py").read_text()
test("  CloudModelConfigBase class defined", "class CloudModelConfigBase" in base_py)
test("  CloudModelConfigBase inherits ABC, BaseModel", "CloudModelConfigBase(ABC, BaseModel)" in base_py)
test("  No hash field in CloudModelConfigBase", 'hash: str = Field(' not in base_py.split("class CloudModelConfigBase")[1].split("class Config_Base")[0])
test("  No path field in CloudModelConfigBase", 'path: Path = Field(' not in base_py.split("class CloudModelConfigBase")[1].split("class Config_Base")[0])
test("  Discriminator handles both hierarchies", "isinstance(v, (Config_Base, CloudModelConfigBase))" in base_py)

# Test 3: Verify cloud base types in taxonomy.py
print("\n3. Checking cloud base types in taxonomy.py...")
taxonomy_py = Path("invokeai/backend/model_manager/taxonomy.py").read_text()
test("  CloudGemini base type", 'CloudGemini = "cloud-gemini"' in taxonomy_py)
test("  CloudImagen base type", 'CloudImagen = "cloud-imagen"' in taxonomy_py)
test("  CloudOpenAI base type", 'CloudOpenAI = "cloud-openai"' in taxonomy_py)

# Test 4: Verify cloud_models.py refactoring
print("\n4. Checking cloud_models.py refactoring...")
cloud_models_py = Path("invokeai/backend/model_manager/configs/cloud_models.py").read_text()
test("  Imports CloudModelConfigBase", "from invokeai.backend.model_manager.configs.base import CloudModelConfigBase" in cloud_models_py)
test("  CloudModelConfig inherits CloudModelConfigBase", "class CloudModelConfig(CloudModelConfigBase):" in cloud_models_py)
test("  GeminiFlashImageConfig has CloudGemini base", 'base: Literal[BaseModelType.CloudGemini] = BaseModelType.CloudGemini' in cloud_models_py)
test("  ImagenUltraConfig has CloudImagen base", 'base: Literal[BaseModelType.CloudImagen] = BaseModelType.CloudImagen' in cloud_models_py)
test("  OpenAIImageConfig has CloudOpenAI base", 'base: Literal[BaseModelType.CloudOpenAI] = BaseModelType.CloudOpenAI' in cloud_models_py)
test("  No variant field in GeminiFlashImageConfig", 'variant: Literal["google-gemini"]' not in cloud_models_py)
test("  No from_model_on_disk method", "from_model_on_disk" not in cloud_models_py)

# Test 5: Verify factory.py integration
print("\n5. Checking factory.py integration...")
factory_py = Path("invokeai/backend/model_manager/configs/factory.py").read_text()
test("  Imports GeminiFlashImageConfig", "GeminiFlashImageConfig" in factory_py)
test("  Imports ImagenUltraConfig", "ImagenUltraConfig" in factory_py)
test("  Imports OpenAIImageConfig", "OpenAIImageConfig" in factory_py)
test("  GeminiFlashImageConfig in union", "Annotated[GeminiFlashImageConfig, GeminiFlashImageConfig.get_tag()]" in factory_py)
test("  ImagenUltraConfig in union", "Annotated[ImagenUltraConfig, ImagenUltraConfig.get_tag()]" in factory_py)
test("  OpenAIImageConfig in union", "Annotated[OpenAIImageConfig, OpenAIImageConfig.get_tag()]" in factory_py)

# Test 6: Verify Python syntax
print("\n6. Checking Python syntax...")
import py_compile
for file in files_to_check:
    try:
        py_compile.compile(file, doraise=True)
        test(f"  {file} syntax", True)
    except py_compile.PyCompileError as e:
        test(f"  {file} syntax", False, str(e))

# Summary
print("\n" + "=" * 70)
if tests_failed == 0:
    print(f"✅ ALL {tests_passed} TESTS PASSED")
    print("=" * 70)
    print()
    print("Phase 1 validation successful!")
    print("- CloudModelConfigBase hierarchy correctly implemented")
    print("- Cloud base types (CloudGemini, CloudImagen, CloudOpenAI) added")
    print("- Cloud configs refactored to use new base")
    print("- Factory union properly registered")
    print()
    sys.exit(0)
else:
    print(f"❌ {tests_failed} TEST(S) FAILED, {tests_passed} passed")
    print("=" * 70)
    sys.exit(1)
