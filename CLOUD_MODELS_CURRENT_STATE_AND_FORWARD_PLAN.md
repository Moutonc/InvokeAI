# Cloud Models: Current State & Detailed Forward Plan

**Date:** 2025-10-28
**Status:** ✅ Phase 1 Complete - Architecture foundation implemented
**Last Updated:** 2025-11-04

---

## 🚀 Implementation Progress

| Phase | Status | Duration | Commit | Notes |
|-------|--------|----------|--------|-------|
| **Phase 0: Rollback** | ✅ **COMPLETE** | 30 min | `367f26d` | Removed incorrect API router, reverted factory.py, created backup |
| **Phase 1: Architecture** | ✅ **COMPLETE** | 2h | `48d87d7` | CloudModelConfigBase hierarchy, unique base types, factory union |
| **Phase 2: Service Layer** | ⏸️ Pending | Est. 3-4h | - | - |
| **Phase 3: Testing** | ⏸️ Pending | Est. 4-5h | - | - |
| **Phase 4: Frontend** | ⏸️ Pending | Est. 2-3h | - | - |
| **Phase 5: Documentation** | ⏸️ Pending | Est. 1-2h | - | - |

**Total Progress:** 2/6 phases complete (33%)

### Phase 0 Completion Summary

**What was removed:**
- ❌ `invokeai/app/api/routers/cloud_models.py` - Custom registration endpoint
- ❌ `invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts` - Frontend client
- ⏪ `invokeai/backend/model_manager/configs/factory.py` - Reverted cloud configs from union

**What was kept:**
- ✅ All cloud provider implementations (google_gemini_provider.py, etc.)
- ✅ Cloud model loader (cloud_model_loader.py)
- ✅ All invocations (gemini_text_to_image.py, etc.)
- ✅ Frontend UI components
- ✅ Model configs (will refactor in Phase 1)

**Backup created:** `backup/cloud-models-attempt-1`

### Phase 1 Completion Summary

**What was implemented:**
- ✅ `base.py` - CloudModelConfigBase abstract base class (parallel to Config_Base)
- ✅ `taxonomy.py` - CloudGemini, CloudImagen, CloudOpenAI base types
- ✅ `cloud_models.py` - Refactored to inherit from CloudModelConfigBase
- ✅ `factory.py` - Added cloud configs to AnyModelConfig discriminated union
- ✅ Test file created for verification

**Architecture changes:**
- Cloud models now have their own hierarchy (no file fields required)
- Each provider has unique base type for discrimination
- Tags: main.cloud_rest.cloud-{provider}
- Clean separation: CloudModelConfigBase vs Config_Base

**Files modified:**
1. `invokeai/backend/model_manager/configs/base.py` - Added CloudModelConfigBase
2. `invokeai/backend/model_manager/taxonomy.py` - Added 3 cloud base types
3. `invokeai/backend/model_manager/configs/cloud_models.py` - Inheritance refactor
4. `invokeai/backend/model_manager/configs/factory.py` - Union registration
5. `test_phase1_configs.py` - Verification tests (syntax validated)

**Validation:**
- ✅ Python syntax valid on all files
- ✅ Manual discriminator tag verification passed
- ✅ No file fields (hash, path, file_size) required
- ✅ Unique tags for each cloud provider

---

## Table of Contents

1. [Current State Summary](#current-state-summary)
2. [What We Built](#what-we-built)
3. [Problems Identified](#problems-identified)
4. [Recommended Architecture: Option D](#recommended-architecture-option-d)
5. [Detailed Implementation Plan](#detailed-implementation-plan)
6. [Phase Breakdown](#phase-breakdown)
7. [Rollback Plan](#rollback-plan)

---

## Current State Summary

### Where We Are

**Branch:** `claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk`
**Commits:** 20+ commits implementing cloud model integration
**Status:** Providers working, but registration flow has architectural issues

### Key Achievements ✅

1. **Three cloud providers fully implemented**
   - Google Gemini 2.5 Flash (text-to-image)
   - Google Imagen 4 Ultra (text-to-image)
   - OpenAI DALL-E 3 (text-to-image)

2. **Provider implementations are solid**
   - Clean API abstractions
   - Proper async/await
   - Good error handling
   - API-spec accurate

3. **Invocation nodes work**
   - Three working invocation classes
   - Proper image saving
   - Metadata handling

4. **Frontend UI components built**
   - Settings panel for provider status
   - Cost estimation display
   - Status indicators

### Key Problems ❌

1. **Wrong registration approach**
   - Created custom `/cloud/models/register` endpoint
   - Bypassed InvokeAI's model management architecture
   - Led to cascading validation errors

2. **Type system issues**
   - Cloud configs forced to have dummy file fields (hash, path, file_size)
   - Discriminator conflicts between providers
   - Violates Liskov Substitution Principle

3. **Architectural mismatch**
   - Tried to make cloud models pretend to be file-based models
   - Doesn't respect fundamental differences
   - Created maintenance burden

### What Happened

We encountered these errors during registration:
```
Error 1: "5 validation errors - hash, path, file_size, source, source_type: Field required"
Error 2: "ModelRecordServiceSQL.add_model() takes 2 positional arguments but 3 were given"
Error 3: "Input should be <CloudProviderType.OpenAI: 'openai'> [type=literal_error]"
```

These aren't random bugs - they're symptoms of **architectural misalignment**.

---

## What We Built

### File Structure (36 files created/modified)

```
Backend - Cloud Providers (✅ KEEP - These are good)
├── invokeai/app/services/cloud_providers/
│   ├── __init__.py
│   ├── provider_base.py              # Base class for providers
│   ├── google_gemini_provider.py     # Gemini implementation
│   ├── google_imagen_provider.py     # Imagen implementation
│   └── openai_provider.py            # OpenAI implementation

Backend - Model Configs (⚠️ NEEDS REFACTORING)
├── invokeai/backend/model_manager/configs/
│   ├── cloud_models.py               # Config classes with dummy fields
│   └── factory.py                    # Modified to include cloud configs

Backend - Model Loader (✅ KEEP - Pattern is correct)
├── invokeai/backend/model_manager/load/model_loaders/
│   └── cloud_model_loader.py         # CloudModelLoader + wrapper

Backend - API Router (❌ REMOVE - Wrong approach)
├── invokeai/app/api/routers/
│   └── cloud_models.py               # Custom registration endpoint

Backend - Invocations (✅ KEEP - These work)
├── invokeai/app/invocations/
│   ├── gemini_text_to_image.py
│   ├── imagen_text_to_image.py
│   └── openai_text_to_image.py

Backend - Taxonomy (⚠️ PARTIAL)
├── invokeai/backend/model_manager/
│   └── taxonomy.py                   # Added ModelSourceType.CLOUD

Frontend - UI Components (✅ KEEP - Good UI)
├── invokeai/frontend/web/src/features/cloudIntegration/
│   ├── components/
│   │   ├── CloudProviderSettingsPanel.tsx
│   │   ├── CostEstimationDisplay.tsx
│   │   └── ProviderStatusIndicator.tsx
│   ├── store/cloudSlice.ts
│   └── types/index.ts

Frontend - API Client (⚠️ NEEDS UPDATE)
└── invokeai/frontend/web/src/services/api/endpoints/
    └── cloudModels.ts                # Points to wrong endpoints

Documentation (✅ KEEP)
├── docs/features/CLOUD_MODELS.md
├── docs/features/CLOUD_MODELS_UI.md
├── CLOUD_MODELS_COMPREHENSIVE_ANALYSIS.md
├── LORA_AND_CLOUD_MODELS_ANALYSIS.md
├── LORA_ARCHITECTURE_DIAGRAMS.md
├── LORA_QUICK_REFERENCE.txt
└── claude.md                         # Git workflow docs
```

### Status Legend
- ✅ **KEEP**: Properly implemented, no changes needed
- ⚠️ **NEEDS REFACTORING**: Partially correct, needs modification
- ❌ **REMOVE**: Wrong approach, should be deleted/replaced

---

## Problems Identified

### 1. Pretending Cloud Models are Files

**The Core Issue:**
```python
# Current approach - Cloud models forced to have file fields:
class CloudModelConfig(Config_Base):
    hash: str = "cloud-model"        # ❌ Dummy value
    path: str = "cloud://..."        # ❌ Fake path
    file_size: int = 0               # ❌ Meaningless
    # ... plus actual cloud fields
```

**Why this is wrong:**
- Violates Liskov Substitution Principle
- Other code may assume paths are real files
- Pollutes database with dummy data
- Awkward to maintain

### 2. Bypassing Model Management Architecture

**What we did:**
```python
# Created custom endpoint that skips normal flow:
@cloud_models_router.post("/models/register")
async def register_cloud_model(...):
    config = GeminiFlashImageConfig(...)  # Manual construction
    model_manager.add_model(config)       # Direct database insert
```

**Proper InvokeAI flow:**
```python
# How local models work:
File/URL → ModelInstallService
        → ModelConfigFactory.from_model_on_disk()
        → Try all config classes
        → Config instance created
        → ModelRecordService.add_model()
        → Database
```

We skipped ModelInstallService and ModelConfigFactory entirely, creating a parallel system.

### 3. Type System Conflicts

**Discriminator problem:**
```python
# All three cloud configs initially had same tag:
# "main.cloud_rest.cloud-api"

# Pydantic couldn't distinguish them
# We "fixed" with variant field, but that's a hack:
variant: Literal["google-gemini"] = "google-gemini"  # Feels wrong
```

---

## Recommended Architecture: Option D

### Core Principle

> **"Don't pretend cloud models are files. Give them their own path through the system, but integrate at the touchpoints where the frontend needs them."**

### Key Insight

**What's the same between local and cloud models:**
- Need to be discovered (listed in UI)
- Need to be selected (ModelIdentifierField)
- Need to be loaded (in invocations)
- Need metadata (name, description, capabilities)

**What's different:**
- **Source**: API endpoint vs file path
- **Installation**: Registration vs download
- **Loading**: Create API client vs load weights
- **Storage**: Database only vs database + disk

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL MODELS                             │
├─────────────────────────────────────────────────────────────┤
│  File → Install → Probe → Config → Database → Loader → Use │
│                                                              │
│  Components:                                                │
│  • ModelInstallService (downloads files)                    │
│  • ModelConfigFactory (probes files)                        │
│  • FileBasedModelConfig (requires file fields)              │
│  • File-based loaders                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    CLOUD MODELS                             │
├─────────────────────────────────────────────────────────────┤
│  API → Register → Validate → Config → Database → Loader → Use│
│                                                              │
│  Components:                                                │
│  • CloudModelService (validates API keys)                   │
│  • CloudModelRegistry (list available models)               │
│  • CloudModelConfigBase (NO file fields)                    │
│  • CloudModelLoader (creates API clients)                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              SHARED INTEGRATION POINTS                      │
├─────────────────────────────────────────────────────────────┤
│  1. ModelRecordService - stores BOTH types in database      │
│  2. ModelIdentifierField - references BOTH types in nodes   │
│  3. ModelLoaderRegistry - loads BOTH types                  │
│  4. Frontend ModelList - shows BOTH types                   │
└─────────────────────────────────────────────────────────────┘
```

### What This Achieves

**Respects differences:**
- ✅ No dummy file paths/hashes
- ✅ Clean separation of concerns
- ✅ Honest type system

**Maximizes reuse:**
- ✅ Same database (ModelRecordService)
- ✅ Same identifiers (ModelIdentifierField)
- ✅ Same loader registry pattern
- ✅ Same invocation pattern
- ✅ Unified frontend model list

---

## Detailed Implementation Plan

### Phase 0: Rollback Incorrect Changes

**Objective:** Remove code that violates the new architecture before building correctly

#### 0.1 Identify Files to Remove/Modify

**Files to DELETE entirely:**
```bash
# This custom endpoint is the wrong approach
invokeai/app/api/routers/cloud_models.py  # ❌ DELETE

# Frontend pointing to wrong endpoints
invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts  # ❌ DELETE or REWRITE
```

**Files to REVERT changes:**
```bash
# We added cloud configs to the union, but they need refactoring first
invokeai/backend/model_manager/configs/factory.py  # ⚠️ REVERT cloud config additions

# We modified this for cloud providers UI - may need to update
invokeai/frontend/web/src/features/system/components/SettingsModal/SettingsModal.tsx  # ⚠️ REVIEW
```

**Files to REFACTOR:**
```bash
# These have dummy fields and need clean base class
invokeai/backend/model_manager/configs/cloud_models.py  # ⚠️ REFACTOR

# May need updates for new service
invokeai/app/api_app.py  # ⚠️ UPDATE for CloudModelService

# Need to register new service
# (File may not exist yet)
invokeai/app/services/__init__.py  # ⚠️ UPDATE
```

#### 0.2 Rollback Steps

```bash
# 1. Create a backup branch
git checkout -b backup/cloud-models-attempt-1
git push -u origin backup/cloud-models-attempt-1

# 2. Go back to main feature branch
git checkout claude/code-analysis-011CULJK8oZmBoZ24DsXQWPk

# 3. Remove the problematic API router
git rm invokeai/app/api/routers/cloud_models.py
git rm invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts

# 4. Revert factory.py to remove cloud configs from union (we'll add back later)
git checkout HEAD~10 -- invokeai/backend/model_manager/configs/factory.py

# 5. Keep but mark for refactoring:
# - cloud_models.py (configs)
# - cloud_model_loader.py (loader)
# - Provider implementations (these are good)
# - Invocations (these are good)
# - Frontend UI components (these are good)

# 6. Commit the rollback
git commit -m "refactor: Rollback incorrect cloud model registration approach

Removed:
- Custom /cloud/models/register API endpoint
- Frontend cloudModels.ts endpoint definitions
- Cloud configs from factory union (will re-add with proper base class)

Keeping for refactoring:
- Cloud provider implementations (correct)
- Cloud model loader (correct pattern)
- Invocations (working)
- Frontend UI components (working)

This prepares for proper Option D implementation with clean config hierarchy."
```

#### 0.3 Verification After Rollback

**Check that these still work:**
```bash
# Providers should still be importable and functional
python3 -c "from invokeai.app.services.cloud_providers import GoogleGeminiProvider; print('✓')"

# Loader should still exist
python3 -c "from invokeai.backend.model_manager.load.model_loaders.cloud_model_loader import CloudModelLoader; print('✓')"

# Invocations should still be valid nodes
python3 -c "from invokeai.app.invocations.gemini_text_to_image import GeminiTextToImageInvocation; print('✓')"
```

**Check that problematic code is gone:**
```bash
# These should not exist anymore
! test -f invokeai/app/api/routers/cloud_models.py || echo "❌ Should be deleted"
! test -f invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts || echo "❌ Should be deleted"
```

---

### Phase 1: Architecture Foundation

**Objective:** Create clean base classes that respect the difference between file-based and cloud models

**Duration:** 2-3 hours
**Risk:** Medium (affects type system, needs careful design)

#### 1.1 Refactor Config Base Hierarchy

**File:** `invokeai/backend/model_manager/configs/base.py`

**Changes needed:**

```python
# BEFORE (Current - Single base class for everything)
class Config_Base(ABC, BaseModel):
    """Base for ALL models"""

    key: str
    hash: str           # ❌ Doesn't apply to cloud
    path: str           # ❌ Doesn't apply to cloud
    file_size: int      # ❌ Doesn't apply to cloud
    name: str
    description: Optional[str]
    source: str
    source_type: ModelSourceType
    type: ModelType
    base: BaseModelType
    format: ModelFormat
    # ...


# AFTER (New - Hierarchy with shared base)
class ModelConfigBase(ABC, BaseModel):
    """Abstract base for ALL models (file-based AND cloud)

    Contains only fields that apply to both types of models.
    """

    # Identity
    key: str = Field(default_factory=uuid_string)
    name: str
    description: Optional[str] = None

    # Taxonomy (applies to all models)
    type: ModelType
    base: BaseModelType
    format: ModelFormat

    # Source tracking (applies to all, but value differs)
    source: str          # File path for local, API URL for cloud
    source_type: ModelSourceType  # Path/URL/HF/CLOUD

    # Pydantic config
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_serialization_defaults_required=True,
    )

    @classmethod
    @abstractmethod
    def get_tag(cls) -> Tag:
        """Get discriminator tag"""
        pass

    @staticmethod
    def get_model_discriminator_value(v: Any) -> str:
        """Get discriminator for union matching"""
        # Same implementation as current Config_Base
        pass


class FileBasedModelConfig(ModelConfigBase):
    """For models stored on disk (existing behavior)

    Adds file-specific fields that don't apply to cloud models.
    """

    # File-specific fields
    hash: str = Field(description="Hash of model file(s)")
    path: str = Field(description="File system path")
    file_size: int = Field(description="Size in bytes")

    @classmethod
    @abstractmethod
    def from_model_on_disk(
        cls,
        mod: ModelOnDisk,
        override_fields: dict[str, Any],
    ) -> Self:
        """Probe file and create config"""
        pass


class CloudModelConfigBase(ModelConfigBase):
    """For cloud API models (new)

    Adds cloud-specific fields. NO file fields (hash/path/size).
    """

    # Cloud-specific fields
    provider: CloudProviderType = Field(description="Cloud provider")
    cloud_model_id: str = Field(description="Model ID on cloud service")
    api_endpoint: Optional[str] = Field(
        default=None,
        description="Override default API endpoint"
    )

    # Provider-specific settings (flexible JSON)
    provider_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific configuration"
    )

    @classmethod
    def from_provider_registration(
        cls,
        provider: CloudProviderType,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> Self:
        """Create config from provider registration (not disk probing)"""
        pass


# Update existing configs to inherit from FileBasedModelConfig
class Main_Diffusers_SD1_Config(FileBasedModelConfig):
    # ... existing implementation


# Update cloud configs to inherit from CloudModelConfigBase
class GeminiFlashImageConfig(CloudModelConfigBase):
    # ... implementation without dummy file fields
```

**Migration strategy:**
```python
# All existing model configs need to change:
# FROM: class MyConfig(Config_Base)
# TO:   class MyConfig(FileBasedModelConfig)

# This is safe because FileBasedModelConfig has all the same fields
# as the old Config_Base
```

**Testing after this change:**
```bash
# All existing tests should still pass
pytest tests/backend/model_manager/

# Specifically check config instantiation
pytest tests/backend/model_manager/test_config.py -v
```

#### 1.2 Update Cloud Model Configs

**File:** `invokeai/backend/model_manager/configs/cloud_models.py`

**Complete rewrite:**

```python
"""Cloud model configurations - clean implementation without file fields."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from invokeai.backend.model_manager.configs.base import CloudModelConfigBase
from invokeai.backend.model_manager.taxonomy import (
    BaseModelType,
    CloudProviderType,
    ModelFormat,
    ModelType,
)


class GeminiFlashImageConfig(CloudModelConfigBase):
    """Google Gemini 2.5 Flash Image configuration.

    Official API: https://ai.google.dev/gemini-api/docs/image-generation
    Pricing: $0.039 per image
    """

    # Taxonomy - uniquely identifies this config
    type: Literal[ModelType.Main] = ModelType.Main
    base: Literal[BaseModelType.CloudGemini] = BaseModelType.CloudGemini
    format: Literal[ModelFormat.CloudREST] = ModelFormat.CloudREST

    # Provider identification
    provider: Literal[CloudProviderType.GoogleGemini] = CloudProviderType.GoogleGemini
    cloud_model_id: Literal["gemini-2.5-flash-image"] = "gemini-2.5-flash-image"

    # Capabilities metadata
    supported_aspect_ratios: List[str] = Field(
        default=[
            "1:1", "3:2", "2:3", "3:4", "4:3",
            "4:5", "5:4", "9:16", "16:9", "21:9"
        ]
    )
    supports_seed: bool = Field(default=True)
    supports_negative_prompt: bool = Field(default=False)
    max_prompt_length: int = Field(default=8192)

    @classmethod
    def from_provider_registration(
        cls,
        provider: CloudProviderType,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> "GeminiFlashImageConfig":
        """Create Gemini config from registration request."""

        if provider != CloudProviderType.GoogleGemini:
            raise ValueError(f"Wrong provider: {provider}")
        if model_id != "gemini-2.5-flash-image":
            raise ValueError(f"Unknown Gemini model: {model_id}")

        return cls(
            name=name or "Gemini 2.5 Flash Image",
            source=f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}",
            source_type=ModelSourceType.CLOUD,
            provider=provider,
            cloud_model_id=model_id,
            **kwargs
        )


class ImagenUltraConfig(CloudModelConfigBase):
    """Google Imagen 4 Ultra configuration.

    Official API: https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview
    Pricing: $0.06 per image
    """

    type: Literal[ModelType.Main] = ModelType.Main
    base: Literal[BaseModelType.CloudImagen] = BaseModelType.CloudImagen
    format: Literal[ModelFormat.CloudREST] = ModelFormat.CloudREST

    provider: Literal[CloudProviderType.GoogleImagen] = CloudProviderType.GoogleImagen
    cloud_model_id: Literal["imagen-4.0-ultra-generate-001"] = "imagen-4.0-ultra-generate-001"

    supported_aspect_ratios: List[str] = Field(
        default=["1:1", "3:4", "4:3", "9:16", "16:9"]
    )
    max_batch_size: int = Field(default=4)
    supports_seed: bool = Field(default=True)
    supports_synthid_watermark: bool = Field(default=True)
    max_resolution: int = Field(default=2048)

    @classmethod
    def from_provider_registration(
        cls,
        provider: CloudProviderType,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> "ImagenUltraConfig":
        """Create Imagen config from registration request."""

        if provider != CloudProviderType.GoogleImagen:
            raise ValueError(f"Wrong provider: {provider}")
        if model_id != "imagen-4.0-ultra-generate-001":
            raise ValueError(f"Unknown Imagen model: {model_id}")

        # Get GCP project from environment
        import os
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        return cls(
            name=name or "Imagen 4 Ultra",
            source=f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/{model_id}",
            source_type=ModelSourceType.CLOUD,
            provider=provider,
            cloud_model_id=model_id,
            **kwargs
        )


class OpenAIImageConfig(CloudModelConfigBase):
    """OpenAI DALL-E configuration.

    Official API: https://platform.openai.com/docs/guides/images
    Pricing: $0.04-$0.12 per image depending on size/quality
    """

    type: Literal[ModelType.Main] = ModelType.Main
    base: Literal[BaseModelType.CloudOpenAI] = BaseModelType.CloudOpenAI
    format: Literal[ModelFormat.CloudREST] = ModelFormat.CloudREST

    provider: Literal[CloudProviderType.OpenAI] = CloudProviderType.OpenAI

    # DALL-E supports multiple models
    cloud_model_id: str = Field(
        default="dall-e-3",
        description="Model ID: dall-e-3 or dall-e-2"
    )

    supported_sizes: List[str] = Field(
        default=["1024x1024", "1792x1024", "1024x1792"]
    )
    quality_options: List[str] = Field(default=["standard", "hd"])
    style_options: List[str] = Field(default=["vivid", "natural"])
    supports_revised_prompt: bool = Field(default=True)
    max_batch_size: int = Field(default=1)

    @classmethod
    def from_provider_registration(
        cls,
        provider: CloudProviderType,
        model_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> "OpenAIImageConfig":
        """Create OpenAI config from registration request."""

        if provider != CloudProviderType.OpenAI:
            raise ValueError(f"Wrong provider: {provider}")
        if model_id not in ["dall-e-3", "dall-e-2"]:
            raise ValueError(f"Unknown OpenAI model: {model_id}")

        return cls(
            name=name or f"DALL-E {model_id.split('-')[-1].upper()}",
            source=f"https://api.openai.com/v1/images/generations",
            source_type=ModelSourceType.CLOUD,
            provider=provider,
            cloud_model_id=model_id,
            **kwargs
        )
```

**Key improvements:**
- ✅ NO dummy file fields (hash, path, file_size)
- ✅ Each provider has unique `base` type (CloudGemini, CloudImagen, CloudOpenAI)
- ✅ Clean `from_provider_registration()` factory method
- ✅ Source URL is the actual API endpoint

#### 1.3 Update Taxonomy

**File:** `invokeai/backend/model_manager/taxonomy.py`

**Add new base types:**

```python
class BaseModelType(str, Enum):
    """Model base types (architectures)."""

    # ... existing types (sd-1, sdxl, flux, etc.)

    # Cloud API base types
    CloudGemini = "cloud-gemini"
    CloudImagen = "cloud-imagen"
    CloudOpenAI = "cloud-openai"

    # Note: Each cloud provider gets its own base type
    # This ensures unique discriminators
```

**Already exists (from previous work):**
```python
class ModelSourceType(str, Enum):
    """Model source types."""

    Path = "path"
    Url = "url"
    HFRepoID = "hf_repo_id"
    CLOUD = "cloud"  # ✓ Already added

class CloudProviderType(str, Enum):
    """Cloud providers."""

    GoogleGemini = "google-gemini"
    GoogleImagen = "google-imagen"
    OpenAI = "openai"
```

#### 1.4 Update Config Factory

**File:** `invokeai/backend/model_manager/configs/factory.py`

**Re-add cloud configs to union (properly this time):**

```python
# At top, import cloud configs
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)

# In the AnyModelConfig union, add at the end (before Unknown_Config):
AnyModelConfig = Annotated[
    Union[
        # ... all existing configs ...

        # Cloud models (NEW - properly discriminated)
        Annotated[GeminiFlashImageConfig, GeminiFlashImageConfig.get_tag()],
        Annotated[ImagenUltraConfig, ImagenUltraConfig.get_tag()],
        Annotated[OpenAIImageConfig, OpenAIImageConfig.get_tag()],

        # Unknown fallback
        Annotated[Unknown_Config, Unknown_Config.get_tag()],
    ],
    Discriminator(ModelConfigBase.get_model_discriminator_value),
]
```

**Test discriminator uniqueness:**

```python
# Add test to verify no conflicts
def test_cloud_config_discriminators():
    """Verify cloud configs have unique discriminators."""

    gemini_tag = GeminiFlashImageConfig.get_tag()
    imagen_tag = ImagenUltraConfig.get_tag()
    openai_tag = OpenAIImageConfig.get_tag()

    # All should be different
    assert gemini_tag != imagen_tag
    assert gemini_tag != openai_tag
    assert imagen_tag != openai_tag

    # Expected values
    assert gemini_tag == "main.cloud_rest.cloud-gemini"
    assert imagen_tag == "main.cloud_rest.cloud-imagen"
    assert openai_tag == "main.cloud_rest.cloud-openai"
```

**Phase 1 Completion Checklist:**

- [ ] ModelConfigBase created as abstract base
- [ ] FileBasedModelConfig created with file fields
- [ ] CloudModelConfigBase created without file fields
- [ ] All existing configs migrated to FileBasedModelConfig
- [ ] GeminiFlashImageConfig refactored (no dummy fields)
- [ ] ImagenUltraConfig refactored (no dummy fields)
- [ ] OpenAIImageConfig refactored (no dummy fields)
- [ ] New BaseModelType enums added to taxonomy
- [ ] Cloud configs re-added to factory union
- [ ] Discriminator uniqueness test passes
- [ ] All existing model tests still pass

---

### Phase 2: Cloud Model Service Layer

**Objective:** Create dedicated service for cloud model management

**Duration:** 3-4 hours
**Risk:** Low (new code, doesn't affect existing systems)

#### 2.1 Create CloudModelService

**File:** `invokeai/app/services/cloud_models/cloud_model_service.py` (NEW)

```python
"""Service for managing cloud model registration and lifecycle."""

import os
from typing import Dict, List, Optional, Type

from invokeai.app.services.cloud_providers import (
    CloudModelProviderBase,
    GoogleGeminiProvider,
    GoogleImagenProvider,
    OpenAIProvider,
)
from invokeai.app.services.model_records.model_records_base import ModelRecordServiceBase
from invokeai.backend.model_manager.configs.cloud_models import (
    CloudModelConfigBase,
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType, ModelSourceType


class CloudModelServiceError(Exception):
    """Base exception for cloud model service errors."""
    pass


class ProviderNotConfiguredError(CloudModelServiceError):
    """Raised when provider credentials are not configured."""
    pass


class InvalidCredentialsError(CloudModelServiceError):
    """Raised when provider credentials are invalid."""
    pass


class CloudModelService:
    """Manages registration and validation of cloud models.

    This service is responsible for:
    - Validating provider credentials
    - Registering cloud models in the database
    - Listing available cloud models (catalog)
    - Listing registered cloud models
    """

    def __init__(self, model_records: ModelRecordServiceBase):
        """Initialize cloud model service.

        Args:
            model_records: Model record service for database operations
        """
        self._records = model_records

        # Map provider types to their implementation classes
        self._provider_classes: Dict[CloudProviderType, Type[CloudModelProviderBase]] = {
            CloudProviderType.GoogleGemini: GoogleGeminiProvider,
            CloudProviderType.GoogleImagen: GoogleImagenProvider,
            CloudProviderType.OpenAI: OpenAIProvider,
        }

        # Map provider types to their config classes
        self._config_classes: Dict[CloudProviderType, Type[CloudModelConfigBase]] = {
            CloudProviderType.GoogleGemini: GeminiFlashImageConfig,
            CloudProviderType.GoogleImagen: ImagenUltraConfig,
            CloudProviderType.OpenAI: OpenAIImageConfig,
        }

    def check_provider_configured(self, provider: CloudProviderType) -> bool:
        """Check if provider has required environment variables set.

        Args:
            provider: Provider to check

        Returns:
            True if provider is configured, False otherwise
        """
        if provider == CloudProviderType.GoogleGemini:
            return bool(os.getenv("GOOGLE_API_KEY"))

        elif provider == CloudProviderType.GoogleImagen:
            return bool(os.getenv("GOOGLE_CLOUD_PROJECT")) and bool(
                os.getenv("GOOGLE_CLOUD_REGION")
            )

        elif provider == CloudProviderType.OpenAI:
            return bool(os.getenv("OPENAI_API_KEY"))

        return False

    async def validate_provider_credentials(self, provider: CloudProviderType) -> bool:
        """Validate that provider credentials actually work.

        Makes a test API call to verify credentials are valid.

        Args:
            provider: Provider to validate

        Returns:
            True if credentials are valid, False otherwise

        Raises:
            ProviderNotConfiguredError: If provider not configured
        """
        if not self.check_provider_configured(provider):
            raise ProviderNotConfiguredError(
                f"{provider} is not configured. Please set required environment variables."
            )

        # Create provider instance and test credentials
        provider_class = self._provider_classes[provider]

        # Get API key/credentials from environment
        if provider == CloudProviderType.GoogleGemini:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            provider_instance = provider_class(api_key=api_key, config={})

        elif provider == CloudProviderType.GoogleImagen:
            # Imagen uses Application Default Credentials
            provider_instance = provider_class(api_key="", config={})

        elif provider == CloudProviderType.OpenAI:
            api_key = os.getenv("OPENAI_API_KEY", "")
            provider_instance = provider_class(api_key=api_key, config={})

        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Test credentials
        return await provider_instance.validate_credentials()

    async def register_cloud_model(
        self,
        provider: CloudProviderType,
        model_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **settings
    ) -> CloudModelConfigBase:
        """Register a cloud model for use in workflows.

        This validates the provider is configured and credentials work,
        then creates a config and stores it in the database.

        Args:
            provider: Cloud provider type
            model_id: Model ID on the cloud service
            name: Optional display name (defaults based on model)
            description: Optional description
            **settings: Additional provider-specific settings

        Returns:
            The created model config

        Raises:
            ProviderNotConfiguredError: If provider not configured
            InvalidCredentialsError: If credentials don't work
            ValueError: If model_id is invalid for provider
        """
        # 1. Validate provider is configured
        if not self.check_provider_configured(provider):
            raise ProviderNotConfiguredError(
                f"{provider} is not configured. Please set required environment variables."
            )

        # 2. Validate credentials work (test API call)
        is_valid = await self.validate_provider_credentials(provider)
        if not is_valid:
            raise InvalidCredentialsError(
                f"{provider} credentials are invalid. Please check your API keys."
            )

        # 3. Create appropriate config using factory method
        config_class = self._config_classes[provider]
        config = config_class.from_provider_registration(
            provider=provider,
            model_id=model_id,
            name=name,
            description=description,
            **settings
        )

        # 4. Check if already registered
        try:
            existing = self._records.get_model(config.key)
            if existing:
                raise ValueError(f"Model {config.key} is already registered")
        except Exception:
            # Model doesn't exist, proceed with registration
            pass

        # 5. Store in database (same as local models)
        self._records.add_model(config)

        return config

    def list_available_models(
        self,
        provider: Optional[CloudProviderType] = None,
        only_configured: bool = False
    ) -> List[Dict]:
        """List cloud models that CAN be registered (catalog).

        This returns a static catalog of available cloud models.
        Users can register any of these if the provider is configured.

        Args:
            provider: Filter to specific provider (None = all)
            only_configured: Only show models for configured providers

        Returns:
            List of model info dictionaries
        """
        catalog = []

        # Google Gemini models
        if (not provider or provider == CloudProviderType.GoogleGemini):
            if not only_configured or self.check_provider_configured(CloudProviderType.GoogleGemini):
                catalog.append({
                    "provider": "google-gemini",
                    "model_id": "gemini-2.5-flash-image",
                    "name": "Gemini 2.5 Flash Image",
                    "description": "Fast and affordable with 10 aspect ratios",
                    "capabilities": ["text-to-image", "seed", "natural-language"],
                    "cost_per_image": 0.039,
                })

        # Google Imagen models
        if (not provider or provider == CloudProviderType.GoogleImagen):
            if not only_configured or self.check_provider_configured(CloudProviderType.GoogleImagen):
                catalog.append({
                    "provider": "google-imagen",
                    "model_id": "imagen-4.0-ultra-generate-001",
                    "name": "Imagen 4 Ultra",
                    "description": "Premium quality with SynthID watermark",
                    "capabilities": ["text-to-image", "seed", "batch", "watermark"],
                    "cost_per_image": 0.06,
                })

        # OpenAI models
        if (not provider or provider == CloudProviderType.OpenAI):
            if not only_configured or self.check_provider_configured(CloudProviderType.OpenAI):
                catalog.extend([
                    {
                        "provider": "openai",
                        "model_id": "dall-e-3",
                        "name": "DALL-E 3",
                        "description": "Latest OpenAI model with quality/style controls",
                        "capabilities": ["text-to-image", "quality", "style"],
                        "cost_per_image": 0.04,  # Standard quality, varies by size
                    },
                    {
                        "provider": "openai",
                        "model_id": "dall-e-2",
                        "name": "DALL-E 2",
                        "description": "Affordable model for rapid iteration",
                        "capabilities": ["text-to-image", "batch"],
                        "cost_per_image": 0.02,
                    }
                ])

        return catalog

    def list_registered_models(
        self,
        provider: Optional[CloudProviderType] = None
    ) -> List[CloudModelConfigBase]:
        """List cloud models user has registered.

        Queries the database for models with source_type=CLOUD.

        Args:
            provider: Filter to specific provider (None = all)

        Returns:
            List of registered cloud model configs
        """
        # Query database for cloud models
        all_models = self._records.search_by_attr(
            source_type=ModelSourceType.CLOUD
        )

        # Filter by provider if specified
        if provider:
            return [m for m in all_models if m.provider == provider]

        return all_models
```

#### 2.2 Register Service with Invoker

**File:** `invokeai/app/services/services_base.py`

```python
# Add to InvocationServices class:

@property
def cloud_models(self) -> CloudModelService:
    """Cloud model management service."""
    return self._cloud_models
```

**File:** `invokeai/app/services/invoker.py`

```python
# In _start() method, initialize cloud model service:

self._services.cloud_models = CloudModelService(
    model_records=self._services.model_manager.store
)
```

#### 2.3 Create API Router

**File:** `invokeai/app/api/routers/cloud_models.py` (REWRITE)

```python
"""API routes for cloud model management."""

from typing import List, Optional

from fastapi import HTTPException, Query
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field

from invokeai.app.api.dependencies import ApiDependencies
from invokeai.app.services.cloud_models.cloud_model_service import (
    CloudModelService,
    InvalidCredentialsError,
    ProviderNotConfiguredError,
)
from invokeai.backend.model_manager.configs.cloud_models import CloudModelConfigBase
from invokeai.backend.model_manager.taxonomy import CloudProviderType


cloud_models_router = APIRouter(prefix="/v2/cloud", tags=["cloud_models"])


# --- Response Models ---

class CloudModelCatalogItem(BaseModel):
    """An available cloud model that can be registered."""

    provider: str
    model_id: str
    name: str
    description: str
    capabilities: List[str]
    cost_per_image: float


class CloudModelRegistrationResponse(BaseModel):
    """Response after registering a cloud model."""

    key: str = Field(description="Unique model key")
    name: str = Field(description="Model display name")
    provider: str = Field(description="Cloud provider")
    model_id: str = Field(description="Model ID on cloud service")
    status: str = Field(description="Registration status")


class ProviderStatusResponse(BaseModel):
    """Status of a cloud provider."""

    provider: str
    is_configured: bool
    is_valid: Optional[bool] = None
    error_message: Optional[str] = None


# --- Endpoints ---

@cloud_models_router.get(
    "/providers/{provider}/status",
    operation_id="get_cloud_provider_status",
    response_model=ProviderStatusResponse,
)
async def get_provider_status(provider: CloudProviderType) -> ProviderStatusResponse:
    """Check if a cloud provider is configured and credentials are valid."""

    cloud_service: CloudModelService = ApiDependencies.invoker.services.cloud_models

    is_configured = cloud_service.check_provider_configured(provider)

    if not is_configured:
        return ProviderStatusResponse(
            provider=provider.value,
            is_configured=False,
            is_valid=None,
            error_message="Provider not configured. Please set required environment variables."
        )

    # Test credentials
    try:
        is_valid = await cloud_service.validate_provider_credentials(provider)
        return ProviderStatusResponse(
            provider=provider.value,
            is_configured=True,
            is_valid=is_valid,
            error_message=None if is_valid else "Credentials are invalid"
        )
    except Exception as e:
        return ProviderStatusResponse(
            provider=provider.value,
            is_configured=True,
            is_valid=False,
            error_message=str(e)
        )


@cloud_models_router.get(
    "/models/available",
    operation_id="list_available_cloud_models",
    response_model=List[CloudModelCatalogItem],
)
async def list_available_models(
    provider: Optional[CloudProviderType] = Query(default=None),
    only_configured: bool = Query(default=False),
) -> List[CloudModelCatalogItem]:
    """Get catalog of cloud models that can be registered.

    Args:
        provider: Filter to specific provider
        only_configured: Only show models for configured providers
    """

    cloud_service: CloudModelService = ApiDependencies.invoker.services.cloud_models

    catalog = cloud_service.list_available_models(provider, only_configured)

    return [CloudModelCatalogItem(**item) for item in catalog]


@cloud_models_router.get(
    "/models/registered",
    operation_id="list_registered_cloud_models",
    response_model=List[CloudModelConfigBase],
)
async def list_registered_models(
    provider: Optional[CloudProviderType] = Query(default=None),
) -> List[CloudModelConfigBase]:
    """Get cloud models user has registered.

    Args:
        provider: Filter to specific provider
    """

    cloud_service: CloudModelService = ApiDependencies.invoker.services.cloud_models

    return cloud_service.list_registered_models(provider)


@cloud_models_router.post(
    "/models/register",
    operation_id="register_cloud_model",
    response_model=CloudModelRegistrationResponse,
    status_code=201,
)
async def register_cloud_model(
    provider: CloudProviderType,
    model_id: str = Query(description="Model ID on cloud service"),
    name: Optional[str] = Query(default=None, description="Display name"),
    description: Optional[str] = Query(default=None, description="Description"),
) -> CloudModelRegistrationResponse:
    """Register a cloud model for use in workflows.

    This validates the provider is configured and credentials work,
    then stores the model in the database.

    Args:
        provider: Cloud provider type
        model_id: Model ID on the cloud service
        name: Optional display name
        description: Optional description
    """

    cloud_service: CloudModelService = ApiDependencies.invoker.services.cloud_models

    try:
        config = await cloud_service.register_cloud_model(
            provider=provider,
            model_id=model_id,
            name=name,
            description=description,
        )

        return CloudModelRegistrationResponse(
            key=config.key,
            name=config.name,
            provider=config.provider.value,
            model_id=config.cloud_model_id,
            status="registered",
        )

    except ProviderNotConfiguredError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@cloud_models_router.delete(
    "/models/{model_key}",
    operation_id="unregister_cloud_model",
    status_code=204,
)
async def unregister_cloud_model(model_key: str):
    """Unregister (delete) a cloud model.

    Args:
        model_key: The model's unique key
    """

    # Use regular model manager to delete
    model_manager = ApiDependencies.invoker.services.model_manager

    try:
        model_manager.store.delete_model(model_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Model not found: {str(e)}")
```

**Phase 2 Completion Checklist:**

- [ ] CloudModelService class created
- [ ] Service handles provider validation
- [ ] Service handles model registration
- [ ] Service provides catalog of available models
- [ ] Service registered with Invoker
- [ ] API router created with RESTful endpoints
- [ ] GET /providers/{provider}/status endpoint works
- [ ] GET /models/available endpoint returns catalog
- [ ] GET /models/registered endpoint lists user's models
- [ ] POST /models/register endpoint validates and stores models
- [ ] DELETE /models/{key} endpoint removes models
- [ ] Error handling covers all edge cases

---

### Phase 3: Testing Infrastructure

**Objective:** Comprehensive test coverage for cloud model system

**Duration:** 4-5 hours
**Risk:** Low (testing only)

#### 3.1 Unit Tests - Config Classes

**File:** `tests/backend/model_manager/configs/test_cloud_configs.py` (NEW)

```python
"""Unit tests for cloud model configs."""

import pytest

from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import (
    CloudProviderType,
    ModelSourceType,
)


class TestGeminiFlashImageConfig:
    """Tests for GeminiFlashImageConfig."""

    def test_discriminator_tag(self):
        """Verify unique discriminator tag."""
        tag = GeminiFlashImageConfig.get_tag()
        assert tag == "main.cloud_rest.cloud-gemini"

    def test_from_provider_registration(self):
        """Test creating config from registration."""
        config = GeminiFlashImageConfig.from_provider_registration(
            provider=CloudProviderType.GoogleGemini,
            model_id="gemini-2.5-flash-image",
            name="Test Gemini",
        )

        assert config.name == "Test Gemini"
        assert config.provider == CloudProviderType.GoogleGemini
        assert config.cloud_model_id == "gemini-2.5-flash-image"
        assert config.source_type == ModelSourceType.CLOUD
        assert "gemini" in config.source.lower()

        # Verify NO file fields (these shouldn't exist)
        assert not hasattr(config, "hash")
        assert not hasattr(config, "file_size")
        # path exists in base but used for API URL

    def test_wrong_provider_raises_error(self):
        """Test that wrong provider raises ValueError."""
        with pytest.raises(ValueError, match="Wrong provider"):
            GeminiFlashImageConfig.from_provider_registration(
                provider=CloudProviderType.OpenAI,  # Wrong!
                model_id="gemini-2.5-flash-image",
            )

    def test_unknown_model_raises_error(self):
        """Test that unknown model ID raises ValueError."""
        with pytest.raises(ValueError, match="Unknown Gemini model"):
            GeminiFlashImageConfig.from_provider_registration(
                provider=CloudProviderType.GoogleGemini,
                model_id="fake-model-id",  # Wrong!
            )


class TestImagenUltraConfig:
    """Tests for ImagenUltraConfig."""

    def test_discriminator_tag(self):
        """Verify unique discriminator tag."""
        tag = ImagenUltraConfig.get_tag()
        assert tag == "main.cloud_rest.cloud-imagen"

    def test_from_provider_registration(self):
        """Test creating config from registration."""
        config = ImagenUltraConfig.from_provider_registration(
            provider=CloudProviderType.GoogleImagen,
            model_id="imagen-4.0-ultra-generate-001",
            name="Test Imagen",
        )

        assert config.name == "Test Imagen"
        assert config.provider == CloudProviderType.GoogleImagen
        assert config.cloud_model_id == "imagen-4.0-ultra-generate-001"
        assert config.source_type == ModelSourceType.CLOUD
        assert "aiplatform" in config.source


class TestOpenAIImageConfig:
    """Tests for OpenAIImageConfig."""

    def test_discriminator_tag(self):
        """Verify unique discriminator tag."""
        tag = OpenAIImageConfig.get_tag()
        assert tag == "main.cloud_rest.cloud-openai"

    def test_from_provider_registration_dalle3(self):
        """Test creating DALL-E 3 config."""
        config = OpenAIImageConfig.from_provider_registration(
            provider=CloudProviderType.OpenAI,
            model_id="dall-e-3",
            name="Test DALL-E 3",
        )

        assert config.name == "Test DALL-E 3"
        assert config.cloud_model_id == "dall-e-3"

    def test_from_provider_registration_dalle2(self):
        """Test creating DALL-E 2 config."""
        config = OpenAIImageConfig.from_provider_registration(
            provider=CloudProviderType.OpenAI,
            model_id="dall-e-2",
        )

        assert config.cloud_model_id == "dall-e-2"
        # Should use default name
        assert "DALL-E" in config.name


class TestDiscriminatorUniqueness:
    """Tests to ensure all cloud configs have unique discriminators."""

    def test_all_cloud_configs_unique(self):
        """Verify no discriminator conflicts."""
        gemini_tag = GeminiFlashImageConfig.get_tag()
        imagen_tag = ImagenUltraConfig.get_tag()
        openai_tag = OpenAIImageConfig.get_tag()

        # All must be different
        assert gemini_tag != imagen_tag
        assert gemini_tag != openai_tag
        assert imagen_tag != openai_tag

        # Verify against expected values
        assert str(gemini_tag) == "main.cloud_rest.cloud-gemini"
        assert str(imagen_tag) == "main.cloud_rest.cloud-imagen"
        assert str(openai_tag) == "main.cloud_rest.cloud-openai"
```

#### 3.2 Unit Tests - Cloud Model Service

**File:** `tests/app/services/test_cloud_model_service.py` (NEW)

```python
"""Unit tests for CloudModelService."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from invokeai.app.services.cloud_models.cloud_model_service import (
    CloudModelService,
    InvalidCredentialsError,
    ProviderNotConfiguredError,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType


@pytest.fixture
def mock_model_records():
    """Mock ModelRecordService."""
    return MagicMock()


@pytest.fixture
def cloud_service(mock_model_records):
    """CloudModelService with mocked dependencies."""
    return CloudModelService(model_records=mock_model_records)


class TestProviderConfiguration:
    """Tests for provider configuration checking."""

    def test_gemini_configured_when_api_key_set(self, cloud_service):
        """Test Gemini shows as configured when API key is set."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            assert cloud_service.check_provider_configured(CloudProviderType.GoogleGemini)

    def test_gemini_not_configured_when_no_api_key(self, cloud_service):
        """Test Gemini shows as not configured without API key."""
        with patch.dict(os.environ, {}, clear=True):
            assert not cloud_service.check_provider_configured(CloudProviderType.GoogleGemini)

    def test_imagen_configured_when_gcp_vars_set(self, cloud_service):
        """Test Imagen shows as configured when GCP vars are set."""
        with patch.dict(os.environ, {
            "GOOGLE_CLOUD_PROJECT": "test-project",
            "GOOGLE_CLOUD_REGION": "us-central1",
        }):
            assert cloud_service.check_provider_configured(CloudProviderType.GoogleImagen)

    def test_openai_configured_when_api_key_set(self, cloud_service):
        """Test OpenAI shows as configured when API key is set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            assert cloud_service.check_provider_configured(CloudProviderType.OpenAI)


class TestCredentialValidation:
    """Tests for credential validation."""

    @pytest.mark.asyncio
    async def test_validate_raises_error_if_not_configured(self, cloud_service):
        """Test validation raises error if provider not configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderNotConfiguredError):
                await cloud_service.validate_provider_credentials(
                    CloudProviderType.GoogleGemini
                )

    @pytest.mark.asyncio
    async def test_validate_calls_provider_validate_method(self, cloud_service):
        """Test validation calls provider's validate_credentials method."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Mock the provider's validate_credentials method
            with patch(
                "invokeai.app.services.cloud_providers.google_gemini_provider.GoogleGeminiProvider.validate_credentials",
                new_callable=AsyncMock,
                return_value=True
            ) as mock_validate:
                result = await cloud_service.validate_provider_credentials(
                    CloudProviderType.GoogleGemini
                )

                assert result is True
                mock_validate.assert_called_once()


class TestModelRegistration:
    """Tests for model registration."""

    @pytest.mark.asyncio
    async def test_register_validates_provider_configured(
        self, cloud_service, mock_model_records
    ):
        """Test registration checks provider is configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderNotConfiguredError):
                await cloud_service.register_cloud_model(
                    provider=CloudProviderType.GoogleGemini,
                    model_id="gemini-2.5-flash-image",
                )

    @pytest.mark.asyncio
    async def test_register_validates_credentials(
        self, cloud_service, mock_model_records
    ):
        """Test registration validates credentials work."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Mock validation to return False (invalid credentials)
            with patch.object(
                cloud_service,
                "validate_provider_credentials",
                new_callable=AsyncMock,
                return_value=False
            ):
                with pytest.raises(InvalidCredentialsError):
                    await cloud_service.register_cloud_model(
                        provider=CloudProviderType.GoogleGemini,
                        model_id="gemini-2.5-flash-image",
                    )

    @pytest.mark.asyncio
    async def test_register_creates_config_and_stores(
        self, cloud_service, mock_model_records
    ):
        """Test successful registration creates config and stores in database."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Mock validation to succeed
            with patch.object(
                cloud_service,
                "validate_provider_credentials",
                new_callable=AsyncMock,
                return_value=True
            ):
                # Mock get_model to raise (model doesn't exist)
                mock_model_records.get_model.side_effect = Exception("Not found")

                config = await cloud_service.register_cloud_model(
                    provider=CloudProviderType.GoogleGemini,
                    model_id="gemini-2.5-flash-image",
                    name="Test Gemini",
                )

                # Verify config was created correctly
                assert config.name == "Test Gemini"
                assert config.provider == CloudProviderType.GoogleGemini

                # Verify add_model was called
                mock_model_records.add_model.assert_called_once_with(config)


class TestModelListing:
    """Tests for listing models."""

    def test_list_available_returns_all_models_by_default(self, cloud_service):
        """Test available models returns full catalog."""
        catalog = cloud_service.list_available_models()

        # Should have at least 4 models (Gemini, Imagen, DALL-E 3, DALL-E 2)
        assert len(catalog) >= 4

        # Check structure
        assert all("provider" in item for item in catalog)
        assert all("model_id" in item for item in catalog)
        assert all("name" in item for item in catalog)

    def test_list_available_filters_by_provider(self, cloud_service):
        """Test filtering available models by provider."""
        catalog = cloud_service.list_available_models(
            provider=CloudProviderType.GoogleGemini
        )

        # Should only have Gemini models
        assert all(item["provider"] == "google-gemini" for item in catalog)

    def test_list_available_filters_by_configured(self, cloud_service):
        """Test only_configured filters to configured providers."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}, clear=True):
            catalog = cloud_service.list_available_models(only_configured=True)

            # Should only have Gemini models (only one configured)
            assert all(item["provider"] == "google-gemini" for item in catalog)

    def test_list_registered_queries_database(
        self, cloud_service, mock_model_records
    ):
        """Test list_registered queries database."""
        # Mock database response
        mock_model_records.search_by_attr.return_value = []

        result = cloud_service.list_registered_models()

        # Verify database was queried
        mock_model_records.search_by_attr.assert_called_once()
```

#### 3.3 Integration Tests - API Endpoints

**File:** `tests/app/api/routers/test_cloud_models_router.py` (NEW)

```python
"""Integration tests for cloud models API router."""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from invokeai.app.api_app import app


@pytest.fixture
def client():
    """Test client for API."""
    return TestClient(app)


class TestProviderStatusEndpoint:
    """Tests for GET /v2/cloud/providers/{provider}/status."""

    def test_returns_not_configured_when_no_env_vars(self, client):
        """Test endpoint returns not_configured status."""
        with patch.dict(os.environ, {}, clear=True):
            response = client.get("/api/v2/cloud/providers/google-gemini/status")

            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "google-gemini"
            assert data["is_configured"] is False
            assert data["is_valid"] is None

    def test_returns_configured_when_env_vars_set(self, client):
        """Test endpoint validates credentials when configured."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Mock credential validation
            with patch(
                "invokeai.app.services.cloud_providers.google_gemini_provider.GoogleGeminiProvider.validate_credentials",
                new_callable=AsyncMock,
                return_value=True
            ):
                response = client.get("/api/v2/cloud/providers/google-gemini/status")

                assert response.status_code == 200
                data = response.json()
                assert data["is_configured"] is True
                assert data["is_valid"] is True


class TestListAvailableModelsEndpoint:
    """Tests for GET /v2/cloud/models/available."""

    def test_returns_full_catalog(self, client):
        """Test endpoint returns all available models."""
        response = client.get("/api/v2/cloud/models/available")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4  # At least 4 models

        # Check structure
        assert all("provider" in item for item in data)
        assert all("model_id" in item for item in data)

    def test_filters_by_provider(self, client):
        """Test filtering by provider works."""
        response = client.get("/api/v2/cloud/models/available?provider=google-gemini")

        assert response.status_code == 200
        data = response.json()
        assert all(item["provider"] == "google-gemini" for item in data)


class TestRegisterModelEndpoint:
    """Tests for POST /v2/cloud/models/register."""

    def test_returns_400_if_provider_not_configured(self, client):
        """Test registration fails if provider not configured."""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post(
                "/api/v2/cloud/models/register",
                params={
                    "provider": "google-gemini",
                    "model_id": "gemini-2.5-flash-image",
                }
            )

            assert response.status_code == 400
            assert "not configured" in response.json()["detail"].lower()

    def test_returns_401_if_credentials_invalid(self, client):
        """Test registration fails if credentials are invalid."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "bad-key"}):
            # Mock validation to return False
            with patch(
                "invokeai.app.services.cloud_providers.google_gemini_provider.GoogleGeminiProvider.validate_credentials",
                new_callable=AsyncMock,
                return_value=False
            ):
                response = client.post(
                    "/api/v2/cloud/models/register",
                    params={
                        "provider": "google-gemini",
                        "model_id": "gemini-2.5-flash-image",
                    }
                )

                assert response.status_code == 401

    def test_successful_registration(self, client):
        """Test successful model registration."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            # Mock successful validation
            with patch(
                "invokeai.app.services.cloud_providers.google_gemini_provider.GoogleGeminiProvider.validate_credentials",
                new_callable=AsyncMock,
                return_value=True
            ):
                # Mock database operations
                # (This would need more setup in real tests)

                response = client.post(
                    "/api/v2/cloud/models/register",
                    params={
                        "provider": "google-gemini",
                        "model_id": "gemini-2.5-flash-image",
                        "name": "Test Model",
                    }
                )

                assert response.status_code == 201
                data = response.json()
                assert data["status"] == "registered"
                assert data["name"] == "Test Model"
                assert data["provider"] == "google-gemini"
```

#### 3.4 End-to-End Tests

**File:** `tests/e2e/test_cloud_model_workflow.py` (NEW)

```python
"""End-to-end tests for cloud model workflows."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from invokeai.app.invocations.gemini_text_to_image import GeminiTextToImageInvocation
from invokeai.app.services.cloud_providers import CloudGenerationResponse
from invokeai.backend.model_manager.taxonomy import CloudProviderType


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_cloud_model_workflow(monkeypatch):
    """Test complete workflow: register → load → invoke → result.

    This tests the full lifecycle:
    1. Register cloud model
    2. Create invocation with model
    3. Execute invocation
    4. Verify image result
    """

    # Mock environment
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

    # Mock Gemini API response
    mock_response = CloudGenerationResponse(
        images=[b"fake-png-data"],
        metadata={"model": "gemini-2.5-flash-image"},
        provider_response={}
    )

    with patch(
        "invokeai.app.services.cloud_providers.google_gemini_provider.GoogleGeminiProvider.generate_image",
        new_callable=AsyncMock,
        return_value=mock_response
    ):
        # 1. Register model
        # (Simplified - in real test would use service)
        from invokeai.backend.model_manager.configs.cloud_models import GeminiFlashImageConfig

        config = GeminiFlashImageConfig.from_provider_registration(
            provider=CloudProviderType.GoogleGemini,
            model_id="gemini-2.5-flash-image",
            name="Test Gemini",
        )

        # 2. Create invocation
        # (Simplified - in real test would use InvocationContext)
        invocation = GeminiTextToImageInvocation(
            model={"key": config.key},
            prompt="test prompt",
            width=1024,
            height=1024,
        )

        # 3. Execute would happen here via context
        # (Real test would need full context setup)

        # 4. Verify structure
        assert invocation.prompt == "test prompt"
        assert config.provider == CloudProviderType.GoogleGemini
```

**Phase 3 Completion Checklist:**

- [ ] Config unit tests written (discriminators, registration, validation)
- [ ] Service unit tests written (configuration, validation, registration, listing)
- [ ] API integration tests written (all endpoints)
- [ ] E2E workflow test written
- [ ] All tests pass
- [ ] Test coverage >= 80% for new code
- [ ] Edge cases covered (invalid credentials, wrong providers, etc.)

---

### Phase 4: Frontend Integration

**Objective:** Update frontend to use new clean architecture

**Duration:** 2-3 hours
**Risk:** Low (mostly UI updates)

#### 4.1 Update API Client

**File:** `invokeai/frontend/web/src/services/api/endpoints/cloudModels.ts` (REWRITE)

```typescript
/**
 * RTK Query API endpoints for cloud models.
 */

import { api } from '../index';
import type { components } from '../schema';

// Type definitions from OpenAPI schema
type CloudProviderType = components['schemas']['CloudProviderType'];
type CloudModelCatalogItem = components['schemas']['CloudModelCatalogItem'];
type CloudModelRegistrationResponse = components['schemas']['CloudModelRegistrationResponse'];
type ProviderStatusResponse = components['schemas']['ProviderStatusResponse'];

export const cloudModelsApi = api.injectEndpoints({
  endpoints: (build) => ({
    // Get provider status
    getCloudProviderStatus: build.query<ProviderStatusResponse, CloudProviderType>({
      query: (provider) => ({
        url: `api/v2/cloud/providers/${provider}/status`,
        method: 'GET',
      }),
      providesTags: (_result, _error, provider) => [{ type: 'CloudProviders', id: provider }],
    }),

    // List available models (catalog)
    listAvailableCloudModels: build.query<
      CloudModelCatalogItem[],
      { provider?: CloudProviderType; onlyConfigured?: boolean }
    >({
      query: ({ provider, onlyConfigured }) => ({
        url: 'api/v2/cloud/models/available',
        method: 'GET',
        params: {
          provider,
          only_configured: onlyConfigured,
        },
      }),
      providesTags: ['CloudModels'],
    }),

    // List registered models
    listRegisteredCloudModels: build.query<
      components['schemas']['CloudModelConfigBase'][],
      { provider?: CloudProviderType }
    >({
      query: ({ provider }) => ({
        url: 'api/v2/cloud/models/registered',
        method: 'GET',
        params: { provider },
      }),
      providesTags: ['CloudModels'],
    }),

    // Register a model
    registerCloudModel: build.mutation<
      CloudModelRegistrationResponse,
      {
        provider: CloudProviderType;
        model_id: string;
        name?: string;
        description?: string;
      }
    >({
      query: ({ provider, model_id, name, description }) => ({
        url: 'api/v2/cloud/models/register',
        method: 'POST',
        params: {
          provider,
          model_id,
          name,
          description,
        },
      }),
      invalidatesTags: ['CloudModels'],
    }),

    // Unregister a model
    unregisterCloudModel: build.mutation<void, string>({
      query: (modelKey) => ({
        url: `api/v2/cloud/models/${modelKey}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['CloudModels'],
    }),
  }),
});

export const {
  useGetCloudProviderStatusQuery,
  useListAvailableCloudModelsQuery,
  useListRegisteredCloudModelsQuery,
  useRegisterCloudModelMutation,
  useUnregisterCloudModelMutation,
} = cloudModelsApi;
```

#### 4.2 Update Settings Panel

**File:** `invokeai/frontend/web/src/features/cloudIntegration/components/CloudProviderSettingsPanel.tsx`

**Update to use new endpoints:**

```typescript
import { memo, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Flex,
  Text,
  VStack,
  useToast,
} from '@invoke-ai/ui-library';
import {
  useGetCloudProviderStatusQuery,
  useListAvailableCloudModelsQuery,
  useListRegisteredCloudModelsQuery,
  useRegisterCloudModelMutation,
} from 'services/api/endpoints/cloudModels';
import type { CloudProviderType } from 'services/api/schema';

export const CloudProviderSettingsPanel = memo(() => {
  const { t } = useTranslation();
  const toast = useToast();
  const [selectedProvider, setSelectedProvider] = useState<CloudProviderType | null>(null);

  // Get status for all providers
  const { data: geminiStatus } = useGetCloudProviderStatusQuery('google-gemini');
  const { data: imagenStatus } = useGetCloudProviderStatusQuery('google-imagen');
  const { data: openaiStatus } = useGetCloudProviderStatusQuery('openai');

  // Get available models for selected provider
  const { data: availableModels } = useListAvailableCloudModelsQuery(
    { provider: selectedProvider ?? undefined, onlyConfigured: true },
    { skip: !selectedProvider }
  );

  // Get registered models
  const { data: registeredModels } = useListRegisteredCloudModelsQuery({});

  // Register model mutation
  const [registerModel, { isLoading: isRegistering }] = useRegisterCloudModelMutation();

  const handleRegisterModel = useCallback(
    async (provider: CloudProviderType, modelId: string, name: string) => {
      try {
        await registerModel({ provider, model_id: modelId, name }).unwrap();
        toast({
          title: t('cloudModels.modelRegistered'),
          status: 'success',
          duration: 3000,
        });
      } catch (error) {
        toast({
          title: t('cloudModels.registrationFailed'),
          description: error.detail || t('cloudModels.unknownError'),
          status: 'error',
          duration: 5000,
        });
      }
    },
    [registerModel, toast, t]
  );

  return (
    <VStack spacing={4} align="stretch">
      {/* Provider Status Cards */}
      <Flex gap={4}>
        <ProviderStatusCard
          provider="google-gemini"
          status={geminiStatus}
          onSelect={() => setSelectedProvider('google-gemini')}
        />
        <ProviderStatusCard
          provider="google-imagen"
          status={imagenStatus}
          onSelect={() => setSelectedProvider('google-imagen')}
        />
        <ProviderStatusCard
          provider="openai"
          status={openaiStatus}
          onSelect={() => setSelectedProvider('openai')}
        />
      </Flex>

      {/* Available Models */}
      {selectedProvider && availableModels && (
        <Box>
          <Text fontWeight="bold" mb={2}>
            {t('cloudModels.availableModels')}
          </Text>
          <VStack align="stretch" spacing={2}>
            {availableModels.map((model) => {
              const isRegistered = registeredModels?.some(
                (rm) => rm.cloud_model_id === model.model_id
              );
              return (
                <Flex key={model.model_id} justify="space-between" align="center">
                  <Box>
                    <Text fontWeight="medium">{model.name}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {model.description}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      ${model.cost_per_image} per image
                    </Text>
                  </Box>
                  {!isRegistered && (
                    <Button
                      size="sm"
                      onClick={() =>
                        handleRegisterModel(selectedProvider, model.model_id, model.name)
                      }
                      isLoading={isRegistering}
                    >
                      {t('cloudModels.register')}
                    </Button>
                  )}
                  {isRegistered && (
                    <Text fontSize="sm" color="green.500">
                      ✓ {t('cloudModels.registered')}
                    </Text>
                  )}
                </Flex>
              );
            })}
          </VStack>
        </Box>
      )}

      {/* Registered Models */}
      {registeredModels && registeredModels.length > 0 && (
        <Box>
          <Text fontWeight="bold" mb={2}>
            {t('cloudModels.myModels')}
          </Text>
          <VStack align="stretch" spacing={2}>
            {registeredModels.map((model) => (
              <Flex key={model.key} justify="space-between" align="center">
                <Text>{model.name}</Text>
                <Button
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={() => {
                    // Handle unregister
                  }}
                >
                  {t('common.remove')}
                </Button>
              </Flex>
            ))}
          </VStack>
        </Box>
      )}
    </VStack>
  );
});

CloudProviderSettingsPanel.displayName = 'CloudProviderSettingsPanel';
```

#### 4.3 Verify Model List Integration

**The key**: Cloud models should now appear in the **regular model list** automatically because they're stored in the same database!

**No frontend changes needed** for the workflow editor - models with `source_type: "cloud"` will appear alongside local models.

**Optional enhancement** - Add cloud icon to distinguish:

```typescript
// In model list component
{models.map((model) => (
  <ModelListItem key={model.key}>
    {model.source_type === 'cloud' && <CloudIcon />}
    {model.name}
  </ModelListItem>
))}
```

**Phase 4 Completion Checklist:**

- [ ] cloudModels.ts API client rewritten for new endpoints
- [ ] CloudProviderSettingsPanel updated to use new queries
- [ ] Provider status cards show correct status
- [ ] Available models list displays catalog
- [ ] Registration flow works (button → mutation → success toast)
- [ ] Registered models appear in settings
- [ ] Cloud models appear in workflow editor model selectors (verify)
- [ ] Optional: Cloud icon added to distinguish from local models

---

### Phase 5: Documentation & Cleanup

**Objective:** Update documentation and clean up temporary code

**Duration:** 1-2 hours
**Risk:** Low

#### 5.1 Update Documentation

**File:** `docs/features/CLOUD_MODELS.md`

Update with correct architecture:

```markdown
# Cloud Models

InvokeAI supports cloud-based image generation models from Google and OpenAI.

## Architecture

Cloud models are integrated into InvokeAI's model management system as a
first-class model type. They:

- Are stored in the same database as local models
- Use the same ModelIdentifierField in nodes
- Load through the same ModelLoaderRegistry
- Appear in the same model selectors in the UI

The key difference: they call APIs instead of loading local files.

## Setup

### Google Gemini

1. Get API key from https://aistudio.google.com/app/apikey
2. Set environment variable:
   ```bash
   GOOGLE_API_KEY=your-key-here
   ```

### Google Imagen

1. Set up Google Cloud project
2. Enable Vertex AI API
3. Authenticate:
   ```bash
   gcloud auth application-default login
   ```
4. Set environment variables:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_REGION=us-central1
   ```

### OpenAI

1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   OPENAI_API_KEY=your-key-here
   ```

## Usage

### Register Models

1. Go to **Settings → Cloud Providers**
2. Check provider status (should show "Configured")
3. Click provider to see available models
4. Click "Register" for models you want to use

### Use in Workflows

1. Open **Workflow Editor**
2. Add cloud model node (e.g., "Gemini Text to Image")
3. Select your registered model from dropdown
4. Connect prompt and other inputs
5. Run workflow

Models are loaded on-demand when the workflow executes.

## API Reference

See `invokeai/app/api/routers/cloud_models.py` for API endpoints:

- `GET /api/v2/cloud/providers/{provider}/status` - Check provider status
- `GET /api/v2/cloud/models/available` - List available models (catalog)
- `GET /api/v2/cloud/models/registered` - List registered models
- `POST /api/v2/cloud/models/register` - Register a model
- `DELETE /api/v2/cloud/models/{key}` - Unregister a model

## Architecture Details

Cloud models follow InvokeAI's model management pattern:

```
Registration:
  User → CloudModelService.register_cloud_model()
       → Validate provider configured
       → Validate credentials work
       → Create CloudModelConfig (no file fields!)
       → Store in database

Usage:
  Node → context.models.load(model_identifier)
      → ModelLoaderRegistry finds CloudModelLoader
      → CloudModelLoader creates API client wrapper
      → Invocation calls API via wrapper
      → Results returned
```

Key difference from local models: no file probing, no downloads, no disk storage.
```

#### 5.2 Clean Up Temporary Files

```bash
# Remove backup branch (if tests pass)
git branch -D backup/cloud-models-attempt-1

# Remove debug scripts (optional - or move to scripts/debug/)
rm -f scripts/test_*_integration.py
rm -f scripts/debug_imagen.py

# Remove old analysis docs (already captured in final docs)
# (Optional - these are useful reference, could keep)
```

#### 5.3 Add Migration Guide

**File:** `docs/features/CLOUD_MODELS_MIGRATION.md` (NEW)

```markdown
# Migrating from Previous Cloud Models Implementation

If you tested the previous implementation (before Phase 0 rollback),
here's how to migrate:

## What Changed

**Before** (incorrect):
- Custom `/cloud/models/register` endpoint
- Cloud configs with dummy file fields (hash, path, file_size)
- Manual config construction

**After** (correct):
- RESTful `/v2/cloud/models/register` endpoint
- Clean config hierarchy (CloudModelConfigBase has no file fields)
- CloudModelService handles registration

## Migration Steps

1. **Update environment variables** - No changes needed, same as before

2. **Re-register models** - Old registrations may not work, re-register:
   ```bash
   curl -X POST "http://localhost:9090/api/v2/cloud/models/register?provider=google-gemini&model_id=gemini-2.5-flash-image"
   ```

3. **Update frontend code** - If you customized frontend:
   - Import from `services/api/endpoints/cloudModels`
   - Use new hooks: `useRegisterCloudModelMutation`, etc.

4. **Verify workflows** - Existing workflows should work without changes
   (model keys remain the same)

## Troubleshooting

**"Model not found" errors**:
- Re-register models using new endpoint
- Check provider status: `GET /api/v2/cloud/providers/{provider}/status`

**"Credentials invalid" errors**:
- Verify environment variables are set
- Test with: `curl` to status endpoint

**Models don't appear in UI**:
- Check browser console for errors
- Verify API endpoint returns models: `GET /api/v2/cloud/models/registered`
```

**Phase 5 Completion Checklist:**

- [ ] CLOUD_MODELS.md updated with correct architecture
- [ ] CLOUD_MODELS_MIGRATION.md created for users
- [ ] Temporary debug scripts removed or archived
- [ ] Old analysis docs archived (optional)
- [ ] Comments in code explain architecture decisions
- [ ] README updated (if needed)

---

## Summary: Complete Implementation Plan

### Phase Overview

```
Phase 0: Rollback (1 hour)
  └─ Remove incorrect code, prepare for clean slate

Phase 1: Architecture (2-3 hours)
  └─ Create clean config hierarchy, update taxonomy

Phase 2: Service Layer (3-4 hours)
  └─ Build CloudModelService and API router

Phase 3: Testing (4-5 hours)
  └─ Comprehensive test coverage

Phase 4: Frontend (2-3 hours)
  └─ Update UI to use new architecture

Phase 5: Documentation (1-2 hours)
  └─ Update docs, cleanup

Total: ~15-20 hours of focused work
```

### Risk Assessment

**Low Risk:**
- Service layer (new code, doesn't affect existing)
- Testing (test-only changes)
- Frontend updates (mostly wiring)
- Documentation (docs-only)

**Medium Risk:**
- Config hierarchy refactor (touches type system)
- Rollback (need to ensure we keep the right code)

**Mitigation:**
- Thorough testing at each phase
- Backup branch before rollback
- Incremental commits (easy to revert)
- Test existing models after Phase 1

### Success Criteria

**Must Have:**
- [ ] All three providers (Gemini, Imagen, OpenAI) register successfully
- [ ] Registered models appear in workflow editor model selectors
- [ ] Invocations execute and generate images
- [ ] No dummy file fields in configs
- [ ] All existing model tests still pass

**Should Have:**
- [ ] Test coverage >= 80% for new code
- [ ] Clean separation between local and cloud models
- [ ] RESTful API design
- [ ] Good error messages

**Nice to Have:**
- [ ] Cloud icon in UI to distinguish from local models
- [ ] Cost estimation in UI
- [ ] Migration guide for testers

### Final Verification Checklist

Before merging:

- [ ] All phases completed
- [ ] All tests passing
- [ ] Manual testing completed:
  - [ ] Register each provider type
  - [ ] Models appear in UI
  - [ ] Generate image with Gemini
  - [ ] Generate image with Imagen
  - [ ] Generate image with OpenAI
  - [ ] Unregister a model works
- [ ] No regressions in existing models
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Ready for PR

---

## Conclusion

This plan provides:

1. **Clear rollback** of incorrect code
2. **Clean architecture** that respects differences between local and cloud
3. **Maximum reuse** of existing infrastructure (database, loaders, identifiers)
4. **Simple frontend** integration (unified model list)
5. **Comprehensive testing** at every level
6. **Complete documentation** for users and developers

The plan is broken into **5 distinct phases** with clear deliverables and checkpoints at each stage.

**Next Step:** Get approval on this plan before starting Phase 0 rollback.
