# Cloud Models Developer Integration Guide

**Complete technical reference for cloud model architecture and integration**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Diagram](#component-diagram)
3. [Adding New Cloud Providers](#adding-new-cloud-providers)
4. [Extending Functionality](#extending-functionality)
5. [Testing & Validation](#testing--validation)
6. [API Reference](#api-reference)
7. [Common Patterns](#common-patterns)

---

## Architecture Overview

### Design Philosophy

Cloud models are integrated as **first-class citizens** alongside local models, using a **parallel hierarchy** approach:

```
ModelConfigBase (abstract)
    ├── Config_Base (file-based models)
    │   ├── Main_Diffusers_SD1_Config
    │   ├── SDXL_Diffusers_Config
    │   └── ... (all local models)
    │
    └── CloudModelConfigBase (API-based models)
        ├── GeminiFlashImageConfig
        ├── ImagenUltraConfig
        └── OpenAIImageConfig
```

**Key Principle**: Cloud models don't pretend to be file-based. They have their own base class without file fields (hash, path, file_size).

### Integration Points

Cloud models integrate with InvokeAI at 5 key layers:

1. **Config Layer**: Model configuration and taxonomy
2. **Service Layer**: Business logic for registration/management
3. **API Layer**: REST endpoints for frontend
4. **Loader Layer**: Runtime model loading
5. **Invocation Layer**: Workflow nodes

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Settings UI                   Model List                        │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ Registration     │         │ Cloud Models     │             │
│  │ Panel            │         │ (☁️ icon)        │             │
│  └────────┬─────────┘         └────────┬─────────┘             │
│           │                             │                        │
│           │ RTK Query                   │                        │
│           └─────────────────────────────┘                        │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND API                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  FastAPI Router (cloud_models.py)                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ POST   /api/v1/models/cloud          (register)          │  │
│  │ GET    /api/v1/models/cloud          (list)              │  │
│  │ GET    /api/v1/models/cloud/{key}    (get)               │  │
│  │ DELETE /api/v1/models/cloud/{key}    (delete)            │  │
│  │ GET    /api/v1/models/cloud/validate/{provider}          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│                  CloudModelService                               │
│                  ┌────────────────┐                             │
│                  │ register_model │                             │
│                  │ list_models    │                             │
│                  │ get_model      │                             │
│                  │ delete_model   │                             │
│                  │ validate_key   │                             │
│                  └────────┬───────┘                             │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL RECORD SERVICE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ModelRecordServiceSQL                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Unified database for local + cloud models              │  │
│  │ • add_model(config)                                       │  │
│  │ • get_model(key)                                          │  │
│  │ • search_by_attr(source_type="cloud")                    │  │
│  │ • delete_model(key)                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Invocation Nodes              CloudModelLoader                 │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ GeminiTextToImage│──load──▶│ Returns          │             │
│  │ ImagenTextToImage│         │ CloudModelWrapper│             │
│  │ OpenAITextToImage│         └────────┬─────────┘             │
│  └──────────────────┘                  │                        │
│           │                             │                        │
│           │                             ▼                        │
│           │                   Cloud Provider Implementations     │
│           │                   ┌──────────────────┐             │
│           └──────────invoke──▶│ GoogleGemini     │             │
│                               │ GoogleImagen     │             │
│                               │ OpenAIProvider   │             │
│                               └────────┬─────────┘             │
│                                        │                        │
└────────────────────────────────────────┼──────────────────────┘
                                         │ HTTPS
                                         ▼
                                  Cloud Provider APIs
                                  (Google, OpenAI, etc.)
```

---

## Adding New Cloud Providers

### Step 1: Create Provider Configuration

**File**: `invokeai/backend/model_manager/configs/cloud_models.py`

```python
from typing import List, Literal
from pydantic import Field
from invokeai.backend.model_manager.configs.base import CloudModelConfigBase
from invokeai.backend.model_manager.taxonomy import (
    BaseModelType,
    CloudProviderType,
    ModelFormat,
    ModelType,
)

class NewProviderConfig(CloudModelConfigBase):
    """Configuration for New Provider."""

    # Taxonomy - must be unique
    type: Literal[ModelType.Main] = ModelType.Main
    base: Literal[BaseModelType.CloudNewProvider] = BaseModelType.CloudNewProvider
    format: Literal[ModelFormat.CloudREST] = ModelFormat.CloudREST

    # Provider identification
    provider: Literal[CloudProviderType.NewProvider] = CloudProviderType.NewProvider
    cloud_model_id: str = Field(description="Model ID on provider's service")

    # Provider-specific capabilities (optional)
    supported_sizes: List[str] = Field(default=["1024x1024"])
    max_resolution: int = Field(default=1024)
    supports_seed: bool = Field(default=False)

    @classmethod
    def from_provider_registration(
        cls,
        provider: CloudProviderType,
        model_id: str,
        name: str | None = None,
        **kwargs
    ) -> "NewProviderConfig":
        """Create config from registration request."""
        if provider != CloudProviderType.NewProvider:
            raise ValueError(f"Wrong provider: {provider}")

        return cls(
            name=name or f"New Provider {model_id}",
            source=f"https://api.newprovider.com/models/{model_id}",
            source_type=ModelSourceType.CLOUD,
            provider=provider,
            cloud_model_id=model_id,
            **kwargs
        )
```

### Step 2: Update Taxonomy

**File**: `invokeai/backend/model_manager/taxonomy.py`

```python
class BaseModelType(str, Enum):
    # ... existing types ...
    CloudNewProvider = "cloud-newprovider"  # Add this

class CloudProviderType(str, Enum):
    # ... existing providers ...
    NewProvider = "newprovider"  # Add this
```

### Step 3: Register in Factory

**File**: `invokeai/backend/model_manager/configs/factory.py`

```python
from invokeai.backend.model_manager.configs.cloud_models import (
    # ... existing imports ...
    NewProviderConfig,  # Add this
)

AnyModelConfig = Annotated[
    Union[
        # ... existing configs ...
        Annotated[NewProviderConfig, NewProviderConfig.get_tag()],  # Add this
        # Unknown fallback
        Annotated[Unknown_Config, Unknown_Config.get_tag()],
    ],
    Discriminator(Config_Base.get_model_discriminator_value),
]
```

### Step 4: Create Provider Implementation

**File**: `invokeai/app/services/cloud_providers/newprovider_provider.py`

```python
"""New Provider API implementation."""

import httpx
from typing import Any, Dict
from invokeai.app.services.cloud_providers.provider_base import (
    CloudGenerationRequest,
    CloudGenerationResponse,
    CloudModelProviderBase,
)

class NewProviderProvider(CloudModelProviderBase):
    """New Provider image generation provider."""

    def __init__(self, api_key: str, config: Dict[str, Any]):
        super().__init__(api_key, config)
        self.base_url = "https://api.newprovider.com/v1"

    async def validate_credentials(self) -> bool:
        """Validate API key works."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False

    async def generate_image(self, request: CloudGenerationRequest) -> CloudGenerationResponse:
        """Generate image using New Provider API."""
        async with httpx.AsyncClient() as client:
            payload = {
                "prompt": request.prompt,
                "width": request.width,
                "height": request.height,
                "num_images": request.num_images,
            }

            if request.seed is not None:
                payload["seed"] = request.seed

            response = await client.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()

            data = response.json()

            # Convert base64 images to bytes
            images = [self._base64_to_bytes(img) for img in data["images"]]

            return CloudGenerationResponse(
                images=images,
                metadata=data.get("metadata", {}),
                provider_response=data
            )
```

### Step 5: Update Service Layer

**File**: `invokeai/app/services/cloud_models/cloud_model_service.py`

Add to `__init__`:
```python
from invokeai.app.services.cloud_providers.newprovider_provider import NewProviderProvider

self._provider_classes = {
    # ... existing providers ...
    CloudProviderType.NewProvider: NewProviderProvider,
}

self._config_classes = {
    # ... existing configs ...
    CloudProviderType.NewProvider: NewProviderConfig,
}
```

Add to `check_provider_configured`:
```python
elif provider == CloudProviderType.NewProvider:
    return bool(os.getenv("NEWPROVIDER_API_KEY"))
```

### Step 6: Create Invocation Node

**File**: `invokeai/app/invocations/newprovider_text_to_image.py`

```python
"""New Provider text-to-image invocation."""

from invokeai.app.invocations.baseinvocation import BaseInvocation, invocation
from invokeai.app.invocations.fields import InputField, OutputField
from invokeai.app.invocations.model import ModelIdentifierField
from invokeai.app.services.shared.invocation_context import InvocationContext
from invokeai.backend.model_manager.configs.cloud_models import NewProviderConfig

@invocation(
    "newprovider_text_to_image",
    title="New Provider Text to Image",
    tags=["cloud", "newprovider", "text-to-image"],
    category="cloud",
    version="1.0.0",
)
class NewProviderTextToImageInvocation(BaseInvocation):
    """Generate images using New Provider API."""

    model: ModelIdentifierField = InputField(description="New Provider model")
    prompt: str = InputField(description="Text prompt")
    width: int = InputField(default=1024)
    height: int = InputField(default=1024)
    seed: int | None = InputField(default=None)

    async def invoke(self, context: InvocationContext) -> ImageOutput:
        # Load cloud model
        model_wrapper = context.models.load(self.model)

        # Generate image
        response = await model_wrapper.provider.generate_image(
            CloudGenerationRequest(
                prompt=self.prompt,
                width=self.width,
                height=self.height,
                seed=self.seed,
                num_images=1,
            )
        )

        # Save and return
        image_dto = context.images.save(image=response.images[0])
        return ImageOutput(
            image=ImageField(image_name=image_dto.image_name),
            width=image_dto.width,
            height=image_dto.height,
        )
```

### Step 7: Add Frontend Support

**File**: `invokeai/frontend/web/src/features/cloudIntegration/types/index.ts`

Update `PROVIDER_DISPLAY_INFO`:
```typescript
export const PROVIDER_DISPLAY_INFO: Record<CloudProviderType, ProviderDisplayInfo> = {
  // ... existing providers ...
  'newprovider': {
    provider: 'newprovider',
    displayName: 'New Provider',
    icon: '🆕',
    description: 'Description of new provider',
    docsUrl: 'https://docs.newprovider.com',
    setupInstructions: 'Get API key from https://newprovider.com/keys',
  },
};
```

Update `CloudModelRegistrationPanel.tsx` to add the model to `AVAILABLE_MODELS`.

---

## Extending Functionality

### Adding New Model Capabilities

Example: Add image-to-image support

1. **Update Config**:
```python
class GeminiFlashImageConfig(CloudModelConfigBase):
    # ... existing fields ...
    supports_image_to_image: bool = Field(default=True)  # Add this
```

2. **Update Provider**:
```python
async def generate_image_to_image(
    self,
    request: CloudGenerationRequest,
    init_image: bytes
) -> CloudGenerationResponse:
    # Implementation
```

3. **Create New Invocation**:
```python
@invocation("gemini_image_to_image", ...)
class GeminiImageToImageInvocation(BaseInvocation):
    init_image: ImageField = InputField(...)
    # ...
```

### Adding Provider-Specific Settings

Example: Add style parameter for a provider

1. **Update Config**:
```python
class NewProviderConfig(CloudModelConfigBase):
    available_styles: List[str] = Field(
        default=["realistic", "artistic", "anime"]
    )
```

2. **Update Invocation**:
```python
class NewProviderTextToImageInvocation(BaseInvocation):
    style: str = InputField(default="realistic")
    # ...
```

---

## Testing & Validation

### Unit Tests

```python
# tests/app/services/test_newprovider_service.py
import pytest
from unittest.mock import patch, AsyncMock

class TestNewProviderService:
    @patch.dict(os.environ, {"NEWPROVIDER_API_KEY": "test-key"})
    def test_provider_configured(self, cloud_service):
        assert cloud_service.check_provider_configured(
            CloudProviderType.NewProvider
        )

    @pytest.mark.asyncio
    async def test_register_model(self, cloud_service):
        with patch.object(
            cloud_service,
            "validate_provider_credentials",
            new_callable=AsyncMock,
            return_value=True
        ):
            config = await cloud_service.register_cloud_model(
                provider=CloudProviderType.NewProvider,
                model_id="test-model",
                name="Test Model"
            )
            assert config.name == "Test Model"
```

### Integration Tests

```python
# tests/backend/model_manager/test_newprovider_e2e.py
def test_newprovider_registration_workflow():
    # 1. Create config
    config = NewProviderConfig.from_provider_registration(
        provider=CloudProviderType.NewProvider,
        model_id="test-model",
        name="Test"
    )

    # 2. Verify structure
    assert config.provider == CloudProviderType.NewProvider
    assert config.source_type == ModelSourceType.CLOUD

    # 3. Verify discriminator
    tag = config.get_tag()
    assert tag.tag == "main.cloud_rest.cloud-newprovider"
```

---

## API Reference

### REST Endpoints

#### POST /api/v1/models/cloud
**Register a cloud model**

Request:
```json
{
  "name": "My Model",
  "provider": "google-gemini",
  "cloud_model_id": "gemini-2.5-flash-image",
  "source": "https://ai.google.dev/",
  "description": "Optional description"
}
```

Response (201):
```json
{
  "key": "abc123...",
  "name": "My Model",
  "provider": "google-gemini",
  "message": "Successfully registered..."
}
```

#### GET /api/v1/models/cloud
**List all cloud models**

Query params:
- `provider` (optional): Filter by provider

Response (200):
```json
{
  "models": [
    {
      "key": "abc123...",
      "name": "My Model",
      "provider": "google-gemini",
      "cloud_model_id": "gemini-2.5-flash-image",
      "source_type": "cloud",
      ...
    }
  ]
}
```

#### GET /api/v1/models/cloud/{key}
**Get specific model**

Response (200): Single model config

#### DELETE /api/v1/models/cloud/{key}
**Delete model**

Response (200):
```json
{
  "key": "abc123...",
  "message": "Model deleted successfully"
}
```

#### GET /api/v1/models/cloud/validate/{provider}
**Validate API key**

Response (200):
```json
{
  "provider": "google-gemini",
  "valid": true,
  "message": "API key is valid"
}
```

---

## Common Patterns

### Pattern 1: Discriminator Tags

Cloud models use unique base types for discrimination:

```python
# Each provider has unique base type
BaseModelType.CloudGemini = "cloud-gemini"
BaseModelType.CloudImagen = "cloud-imagen"
BaseModelType.CloudOpenAI = "cloud-openai"

# This creates unique tags:
# - "main.cloud_rest.cloud-gemini"
# - "main.cloud_rest.cloud-imagen"
# - "main.cloud_rest.cloud-openai"
```

### Pattern 2: Provider Factories

Use factory methods for config creation:

```python
@classmethod
def from_provider_registration(
    cls,
    provider: CloudProviderType,
    model_id: str,
    name: str | None = None,
    **kwargs
) -> Self:
    # Validate provider matches
    # Set defaults
    # Return configured instance
```

### Pattern 3: Lazy Loading

Models are loaded on-demand in workflows:

```python
# In invocation
model_wrapper = context.models.load(self.model)
provider = model_wrapper.provider  # CloudModelProviderBase
response = await provider.generate_image(request)
```

### Pattern 4: Unified Database

Cloud and local models share the same database:

```python
# Both use ModelRecordService
service.add_model(cloud_config)  # Same as local
service.get_model(key)  # Returns either type
service.search_by_attr(source_type="cloud")  # Filter
```

---

## Best Practices

### Configuration
- ✅ Use unique base types per provider
- ✅ Include provider-specific capabilities
- ✅ Document all fields
- ✅ Add validation in `from_provider_registration`

### API Design
- ✅ Follow RESTful conventions
- ✅ Use proper HTTP status codes (201, 404, 400)
- ✅ Return detailed error messages
- ✅ Include provider info in responses

### Error Handling
- ✅ Create specific exception types
- ✅ Validate API keys before operations
- ✅ Handle network errors gracefully
- ✅ Log errors for debugging

### Testing
- ✅ Write unit tests with mocks
- ✅ Create integration tests for workflows
- ✅ Test error cases
- ✅ Verify discriminator uniqueness

---

## Migration Guide

### From Pre-Phase 1

If you have old cloud model code:

1. **Update Configs**: Change from `Config_Base` to `CloudModelConfigBase`
2. **Remove File Fields**: Delete `hash`, `path`, `file_size`
3. **Add Base Type**: Create unique `BaseModelType` enum value
4. **Update Factory**: Re-add to `AnyModelConfig` union

### From Phase 1-3

Phase 4 added frontend. If extending:

1. **Use RTK Query**: Import from `services/api/endpoints/cloudModels`
2. **Follow UI Patterns**: Use `StandaloneAccordion`, etc.
3. **Add Translations**: Update `CLOUD_MODELS_TRANSLATION_KEYS.md`

---

## References

- **Phase Documentation**: See `CLOUD_MODELS_PROGRESS_SUMMARY.md`
- **User Guide**: See `CLOUD_MODELS_USER_GUIDE.md`
- **Testing**: See `PHASE4_TESTING_GUIDE.md`
- **Backend Source**: `invokeai/app/services/cloud_models/`
- **Frontend Source**: `invokeai/frontend/web/src/features/cloudIntegration/`

---

**Questions?** Check existing code patterns or ask in InvokeAI Discord!
