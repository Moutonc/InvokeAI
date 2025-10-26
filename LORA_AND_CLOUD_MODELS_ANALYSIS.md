# LoRA Models Architecture & Cloud Models Implementation Pattern

## Executive Summary

This document provides a comprehensive analysis of how LoRA (Low-Rank Adaptation) models work in InvokeAI, with a focus on the architectural patterns that should be followed for implementing cloud models. LoRA represents an excellent reference implementation because:

1. **Modular Design**: Clear separation between config, loader, and invocation
2. **Type-Safe Integration**: Uses discriminated unions and proper typing
3. **Lifecycle Pattern**: Follows a consistent flow from registration to execution
4. **Extensible**: Supports multiple formats and base models

Cloud models will follow the same architectural pattern but with different implementation details (API calls instead of file loading).

---

## 1. LoRA Config Class Structure

**Location**: `/invokeai/backend/model_manager/configs/lora.py`

### 1.1 Config Hierarchy

```
Config_Base (abstract base)
    ├── LoRA_Config_Base (abstract)
    │   ├── LoRA_OMI_Config_Base
    │   │   ├── LoRA_OMI_SDXL_Config
    │   │   └── LoRA_OMI_FLUX_Config
    │   ├── LoRA_LyCORIS_Config_Base
    │   │   ├── LoRA_LyCORIS_SD1_Config
    │   │   ├── LoRA_LyCORIS_SD2_Config
    │   │   ├── LoRA_LyCORIS_SDXL_Config
    │   │   └── LoRA_LyCORIS_FLUX_Config
    │   └── LoRA_Diffusers_Config_Base
    │       ├── LoRA_Diffusers_SD1_Config
    │       ├── LoRA_Diffusers_SD2_Config
    │       ├── LoRA_Diffusers_SDXL_Config
    │       └── LoRA_Diffusers_FLUX_Config
    └── ControlLoRA_LyCORIS_FLUX_Config
```

### 1.2 Base LoRA Config Fields

```python
class LoRA_Config_Base(ABC, BaseModel):
    """Base class for LoRA models."""
    
    type: Literal[ModelType.LoRA] = Field(default=ModelType.LoRA)
    
    trigger_phrases: set[str] | None = Field(
        default=None,
        description="Set of trigger phrases for this model",
    )
    
    default_settings: LoraModelDefaultSettings | None = Field(
        default=None,
        description="Default settings for this model",
    )
```

### 1.3 LoRA Model Default Settings

```python
class LoraModelDefaultSettings(BaseModel):
    weight: float | None = Field(
        default=None, 
        ge=-1, 
        le=2, 
        description="Default weight for this model"
    )
    model_config = ConfigDict(extra="forbid")
```

### 1.4 Format-Specific Implementations

Each format (OMI, LyCORIS, Diffusers) implements:
- `from_model_on_disk()`: Creates config from a model file on disk
- `_validate_base()`: Validates that the model matches the expected base
- `_validate_looks_like_*()`: Format-specific detection heuristics
- `_get_base_or_raise()`: Determines base model type from state dict

**Key Pattern**: Each config validates at construction time that:
1. The file exists and is readable
2. The model state dict looks like a LoRA
3. The model's base type matches the config class

### 1.5 Model Identification Strategy

LoRA models are identified by examining the state dict keys:

```python
# LyCORIS format looks for these prefixes/suffixes:
has_key_with_lora_prefix = state_dict_has_any_keys_starting_with(
    mod.load_state_dict(),
    {
        "lora_te_",      # Text encoder
        "lora_unet_",    # UNet
        "lora_te1_",     # SDXL text encoder 1
        "lora_te2_",     # SDXL text encoder 2
        "lora_transformer_",  # Flux transformer
    },
)

has_key_with_lora_suffix = state_dict_has_any_keys_ending_with(
    mod.load_state_dict(),
    {
        "to_k_lora.up.weight",
        "to_q_lora.down.weight",
        "lora_A.weight",
        "lora_B.weight",
    },
)
```

---

## 2. LoRA Loader Implementation

**Location**: `/invokeai/backend/model_manager/load/model_loaders/lora.py`

### 2.1 Loader Registration

```python
@ModelLoaderRegistry.register(base=BaseModelType.Flux, type=ModelType.LoRA, format=ModelFormat.OMI)
@ModelLoaderRegistry.register(base=BaseModelType.StableDiffusionXL, type=ModelType.LoRA, format=ModelFormat.OMI)
@ModelLoaderRegistry.register(base=BaseModelType.Any, type=ModelType.LoRA, format=ModelFormat.Diffusers)
@ModelLoaderRegistry.register(base=BaseModelType.Any, type=ModelType.LoRA, format=ModelFormat.LyCORIS)
@ModelLoaderRegistry.register(base=BaseModelType.Flux, type=ModelType.ControlLoRa, format=ModelFormat.LyCORIS)
@ModelLoaderRegistry.register(base=BaseModelType.Flux, type=ModelType.ControlLoRa, format=ModelFormat.Diffusers)
class LoRALoader(ModelLoader):
    """Class to load LoRA models."""
```

**Key Insight**: Each loader class is registered with specific combinations of:
- `base`: The base model type (Flux, SDXL, SD1, SD2, Any)
- `type`: The model type (LoRA, ControlLoRA)
- `format`: The format (OMI, LyCORIS, Diffusers)

### 2.2 Loader Initialization

```python
def __init__(
    self,
    app_config: InvokeAIAppConfig,
    logger: Logger,
    ram_cache: ModelCache,
):
    super().__init__(app_config, logger, ram_cache)
    self._model_base: Optional[BaseModelType] = None
```

The `_model_base` is stored because it's determined during `_get_model_path()` and needed in `_load_model()`.

### 2.3 Model Path Resolution

```python
def _get_model_path(self, config: AnyModelConfig) -> Path:
    # Store base for later use
    self._model_base = config.base
    
    model_base_path = self._app_config.models_path
    model_path = model_base_path / config.path
    
    # For Diffusers format, find the actual weights file
    if config.format == ModelFormat.Diffusers:
        for ext in ["safetensors", "bin"]:
            path = model_base_path / config.path / f"pytorch_lora_weights.{ext}"
            if path.exists():
                model_path = path
                break
    
    return model_path.resolve()
```

**Note**: Diffusers LoRAs are directories containing `pytorch_lora_weights.*` files.

### 2.4 Model Loading Pipeline

```python
def _load_model(
    self,
    config: AnyModelConfig,
    submodel_type: Optional[SubModelType] = None,
) -> AnyModel:
    
    # 1. Load state dict from file
    if model_path.suffix == ".safetensors":
        state_dict = load_file(model_path.absolute().as_posix(), device="cpu")
    else:
        state_dict = torch.load(model_path, map_location="cpu")
    
    # 2. Clean up unused keys
    state_dict = {k: v for k, v in state_dict.items() 
                  if not k.startswith("bundle_emb")}
    
    # 3. Convert format if needed (OMI -> internal format)
    if config.format == ModelFormat.OMI and self._model_base in [
        BaseModelType.StableDiffusionXL,
        BaseModelType.Flux,
    ]:
        state_dict = convert_from_omi(state_dict, config.base)
    
    # 4. Convert keys if needed (SDXL-specific)
    if self._model_base == BaseModelType.StableDiffusionXL:
        state_dict = convert_sdxl_keys_to_diffusers_format(state_dict)
        model = lora_model_from_sd_state_dict(state_dict=state_dict)
    
    # 5. Detect and convert Flux format
    elif self._model_base == BaseModelType.Flux:
        if config.format is ModelFormat.OMI:
            model = lora_model_from_flux_diffusers_state_dict(
                state_dict=state_dict, 
                alpha=None
            )
        elif config.format is ModelFormat.LyCORIS:
            # Detect sub-format and convert accordingly
            if is_state_dict_likely_in_flux_diffusers_format(state_dict):
                model = lora_model_from_flux_diffusers_state_dict(...)
            elif is_state_dict_likely_in_flux_kohya_format(state_dict):
                model = lora_model_from_flux_kohya_state_dict(state_dict)
            elif is_state_dict_likely_in_flux_onetrainer_format(state_dict):
                model = lora_model_from_flux_onetrainer_state_dict(state_dict)
            elif is_state_dict_likely_flux_control(state_dict):
                model = lora_model_from_flux_control_state_dict(state_dict)
            elif is_state_dict_likely_in_flux_aitoolkit_format(state_dict):
                model = lora_model_from_flux_aitoolkit_state_dict(state_dict)
    
    # 6. Convert to target dtype
    model.to(dtype=self._torch_dtype)
    return model
```

**Key Insight**: The loader:
1. Loads raw state dict from disk
2. Applies format conversions
3. Converts to internal model representation
4. Returns model ready for use

---

## 3. Model Registration System

**Location**: `/invokeai/app/services/model_install/` and `/invokeai/app/services/model_records/`

### 3.1 Registration Flow Overview

```
File on Disk
    ↓
Model Discovery (_probe)
    ↓
Model Identification (ModelConfigFactory)
    ↓
Configuration Creation (specific config class)
    ↓
Database Storage (ModelRecordService.add_model)
    ↓
Available in System (ModelIdentifierField references)
```

### 3.2 Model Installation/Registration API

**API Endpoint**: `POST /v2/models/install`

```python
@model_manager_router.post(
    "/install",
    operation_id="install_model",
)
async def install_model(
    source: str = Query(description="Local path, repo_id, or URL"),
    inplace: Optional[bool] = Query(default=False),
    config: ModelRecordChanges = Body(
        description="Override fields like name, description"
    ),
) -> ModelInstallJob:
    """Install a model from source"""
```

**Parameters**:
- `source`: Path, HuggingFace repo ID, or URL
- `inplace`: Whether to register path in-place (for local models)
- `config`: Overrides for auto-detected values

### 3.3 Model Probing Process

```python
def _probe(self, model_path: Path, config: Optional[ModelRecordChanges] = None):
    """Identify model type from disk"""
    hash_algo = self._app_config.hashing_algorithm
    fields = config.model_dump()

    result = ModelConfigFactory.from_model_on_disk(
        mod=model_path,
        override_fields=deepcopy(fields),
        hash_algo=hash_algo,
        allow_unknown=self.app_config.allow_unknown_models,
    )

    if result.config is None:
        raise InvalidModelConfigException(
            f"Could not identify model for {model_path}"
        )
    
    return result.config
```

### 3.4 Model Registration to Database

```python
def _register(
    self, 
    model_path: Path, 
    config: Optional[ModelRecordChanges] = None,
    info: Optional[AnyModelConfig] = None
) -> str:
    """Register model in database"""
    
    # Probe if config not provided
    info = info or self._probe(model_path, config)
    
    # Apply LoRA metadata if applicable
    apply_lora_metadata(info, model_path.resolve(), model_images_path)
    
    # Add to database
    added_config = self.record_store.add_model(info)
    
    return added_config.key
```

### 3.5 ModelConfigFactory Pattern

**Location**: `/invokeai/backend/model_manager/configs/factory.py`

The factory uses a discriminated union with all possible config types:

```python
AnyModelConfig = Annotated[
    Union[
        Annotated[Main_Diffusers_SD1_Config, Main_Diffusers_SD1_Config.get_tag()],
        Annotated[LoRA_LyCORIS_FLUX_Config, LoRA_LyCORIS_FLUX_Config.get_tag()],
        Annotated[LoRA_OMI_SDXL_Config, LoRA_OMI_SDXL_Config.get_tag()],
        # ... many more types ...
        Annotated[CloudModelConfig, CloudModelConfig.get_tag()],
        Annotated[Unknown_Config, Unknown_Config.get_tag()],
    ],
    Discriminator(Config_Base.get_model_discriminator_value),
]

AnyModelConfigValidator = TypeAdapter[AnyModelConfig](AnyModelConfig)
```

**Key Pattern**: `ModelConfigFactory.from_model_on_disk()` tries all config classes in order until one succeeds (via `from_model_on_disk()` method).

---

## 4. LoRA Invocations (Using Models in Workflows)

**Location**: `/invokeai/app/invocations/flux_lora_loader.py` (and others)

### 4.1 Model Field Data Structures

```python
class ModelIdentifierField(BaseModel):
    key: str                      # Unique model ID
    hash: str                     # BLAKE3 hash
    name: str                     # Model name
    base: BaseModelType           # sd-1, sd-2, sdxl, flux, etc.
    type: ModelType               # main, lora, controlnet, etc.
    submodel_type: SubModelType | None  # For main models: unet, text_encoder, vae
```

```python
class LoRAField(BaseModel):
    lora: ModelIdentifierField = Field(description="Info to load lora model")
    weight: float = Field(description="Weight to apply to lora model")
```

### 4.2 Single LoRA Loader Invocation

```python
@invocation(
    "flux_lora_loader",
    title="Apply LoRA - FLUX",
    tags=["lora", "model", "flux"],
    category="model",
    version="1.2.1",
)
class FluxLoRALoaderInvocation(BaseInvocation):
    """Apply a LoRA model to a FLUX transformer and/or text encoder."""

    lora: ModelIdentifierField = InputField(
        description=FieldDescriptions.lora_model,
        title="LoRA",
        ui_model_base=BaseModelType.Flux,
        ui_model_type=ModelType.LoRA,
    )
    weight: float = InputField(default=0.75, description=FieldDescriptions.lora_weight)
    transformer: TransformerField | None = InputField(default=None, ...)
    clip: CLIPField | None = InputField(default=None, ...)
    t5_encoder: T5EncoderField | None = InputField(default=None, ...)

    def invoke(self, context: InvocationContext) -> FluxLoRALoaderOutput:
        lora_key = self.lora.key
        
        # Verify model exists
        if not context.models.exists(lora_key):
            raise ValueError(f"Unknown lora: {lora_key}!")
        
        # Check for duplicate applications
        if self.transformer and any(lora.lora.key == lora_key for lora in self.transformer.loras):
            raise ValueError(f'LoRA "{lora_key}" already applied to transformer.')
        
        # Create output by appending LoRA to model fields
        output = FluxLoRALoaderOutput()
        
        if self.transformer is not None:
            output.transformer = self.transformer.model_copy(deep=True)
            output.transformer.loras.append(
                LoRAField(
                    lora=self.lora,
                    weight=self.weight,
                )
            )
        
        if self.clip is not None:
            output.clip = self.clip.model_copy(deep=True)
            output.clip.loras.append(
                LoRAField(
                    lora=self.lora,
                    weight=self.weight,
                )
            )
        
        if self.t5_encoder is not None:
            output.t5_encoder = self.t5_encoder.model_copy(deep=True)
            output.t5_encoder.loras.append(
                LoRAField(
                    lora=self.lora,
                    weight=self.weight,
                )
            )
        
        return output
```

### 4.3 Collection LoRA Loader Invocation

```python
@invocation(
    "flux_lora_collection_loader",
    title="Apply LoRA Collection - FLUX",
)
class FLUXLoRACollectionLoader(BaseInvocation):
    """Applies a collection of LoRAs to a FLUX transformer."""

    loras: Optional[LoRAField | list[LoRAField]] = InputField(
        default=None, 
        description="LoRA models and weights. May be a single LoRA or collection.",
    )
    # ... model inputs ...

    def invoke(self, context: InvocationContext) -> FluxLoRALoaderOutput:
        output = FluxLoRALoaderOutput()
        loras = self.loras if isinstance(self.loras, list) else [self.loras]
        added_loras: list[str] = []

        for lora in loras:
            if lora is None or lora.lora.key in added_loras:
                continue
            
            if not context.models.exists(lora.lora.key):
                raise Exception(f"Unknown lora: {lora.lora.key}!")
            
            added_loras.append(lora.lora.key)
            
            # Append to all applicable outputs
            if self.transformer is not None and output.transformer is not None:
                output.transformer.loras.append(lora)
            # ... similarly for clip and t5_encoder ...
        
        return output
```

### 4.4 Key Invocation Patterns

1. **Model Loading is Lazy**: Models are NOT loaded in the invocation. Only LoRAField objects are appended.
2. **Accumulation**: Multiple LoRA invocations can be chained to accumulate LoRAs.
3. **Weight Control**: Each LoRA has its own weight parameter.
4. **Duplicate Prevention**: Prevents same LoRA from being applied twice.
5. **Validation**: Verifies LoRA exists in model manager before allowing application.

---

## 5. Complete LoRA Lifecycle

### 5.1 Phase 1: Preparation (Registration)

**Timeline**: Admin setup or model discovery

```
1. User adds LoRA file to models directory
   ↓
2. ModelInstallService.register_path() called
   (or automatic discovery during startup)
   ↓
3. ModelConfigFactory.from_model_on_disk() 
   attempts config classes in order
   ↓
4. LoRA_LyCORIS_FLUX_Config.from_model_on_disk():
   - Validates file is readable
   - Loads state dict
   - Checks for LoRA-like keys
   - Determines base model type
   - Creates config instance
   ↓
5. ModelRecordService.add_model(config)
   stores config in database
   ↓
6. Model is now available via API/UI
```

**Database Storage**:
```
{
    "key": "flux-lora-style-01",
    "name": "Flux LoRA Style",
    "type": "lora",
    "base": "flux",
    "format": "lora",
    "path": "lora/flux-lora-style-01/pytorch_lora_weights.safetensors",
    "description": "...",
    "trigger_phrases": ["style:01"],
    "default_settings": {"weight": 0.75},
    "hash": "abc123...",
    ...
}
```

### 5.2 Phase 2: Composition (Building Workflow)

**Timeline**: User creates workflow

```
1. UI displays available LoRA models
   (from ModelRecordService list)
   ↓
2. User adds "Apply LoRA - FLUX" invocation
   ↓
3. User selects LoRA from dropdown
   (ModelIdentifierField created with:
    - key, hash, name, base, type
    - from selected model config)
   ↓
4. User sets weight parameter
   ↓
5. FluxLoRALoaderInvocation.invoke():
   - Validates LoRA exists via context.models.exists(key)
   - Creates LoRAField with (lora=model_id, weight)
   - Appends to transformer.loras list
   ↓
6. Output passed to next invocation
   (e.g., image generation invocation)
```

### 5.3 Phase 3: Execution (Running Workflow)

**Timeline**: User runs workflow

```
1. Workflow execution starts
   ↓
2. Image generation invocation receives
   TransformerField with .loras: List[LoRAField]
   ↓
3. For each LoRA in transformer.loras:
   - context.models.load(lora.lora.key)
   - ModelLoaderRegistry.get_implementation()
   - LoRALoader.load_model(config)
   ↓
4. LoRALoader._load_model():
   - Load state dict from file
   - Apply format conversions
   - Convert to internal model representation
   - Apply LoRA weight: scale = alpha / rank
   ↓
5. LoRAExt.patch_unet():
   - Load LoRA model from cache
   - LayerPatcher.apply_smart_model_patch()
   - Apply LoRA weights to unet layers
   ↓
6. Image generation proceeds with LoRA applied
   ↓
7. LoRA model released from cache after generation
```

### 5.4 Model Caching

```
LoRA models are cached in ModelCache:
- After loading from disk
- Remains in cache for reuse
- Evicted when cache space needed
- Cache key: (model.key, submodel_type)
```

---

## 6. CloudModelConfig Implementation Pattern

**Location**: `/invokeai/backend/model_manager/configs/cloud_models.py`

### 6.1 Base CloudModelConfig

```python
class CloudModelConfig(Config_Base):
    """Base configuration for cloud-based image generation models."""

    type: Literal[ModelType.Main] = ModelType.Main
    base: Literal[BaseModelType.CloudAPI] = BaseModelType.CloudAPI
    format: Literal[ModelFormat.CloudREST] = ModelFormat.CloudREST

    # Cloud-specific fields
    provider: CloudProviderType = Field(description="Cloud provider type")
    cloud_model_id: str = Field(description="Model ID on cloud service")

    # Provider-specific settings
    provider_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific configuration parameters",
    )

    @classmethod
    def from_model_on_disk(
        cls,
        mod: ModelOnDisk,
        override_fields: dict[str, Any],
    ) -> "CloudModelConfig":
        """
        Cloud models are not discovered from disk.
        They must be registered manually via API or UI.
        """
        raise NotACloudModelError(
            "Cloud models cannot be auto-discovered from disk. "
            "Please register them manually via API or UI."
        )
```

### 6.2 Provider-Specific Implementations

Examples in system:
- `GeminiFlashImageConfig`: Google Gemini 2.5 Flash Image
- `ImagenUltraConfig`: Google Imagen 4 Ultra
- `OpenAIImageConfig`: OpenAI DALL-E 3 / GPT Image 1

### 6.3 Implementation Steps for Cloud Models

#### Step 1: Create Config Class

```python
class MyCloudModelConfig(CloudModelConfig):
    """Configuration for MyCloud image generation."""
    
    provider: Literal[CloudProviderType.MyCloud] = CloudProviderType.MyCloud
    cloud_model_id: str = Field(default="my-model-v1")
    
    # Provider-specific fields
    api_base_url: str = Field(default="https://api.mycloud.com/v1")
    supports_seed: bool = Field(default=True)
    max_prompt_length: int = Field(default=4000)
    
    # Custom settings
    quality_options: List[str] = Field(default=["standard", "high"])
    provider_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="MyCloud-specific settings (auth tokens, etc)"
    )
```

#### Step 2: Create Loader Class

```python
from invokeai.backend.model_manager.load.load_default import ModelLoader
from invokeai.backend.model_manager.load.model_loader_registry import ModelLoaderRegistry
from invokeai.backend.model_manager.taxonomy import BaseModelType, ModelFormat, ModelType

@ModelLoaderRegistry.register(
    base=BaseModelType.CloudAPI, 
    type=ModelType.Main, 
    format=ModelFormat.CloudREST
)
class CloudModelLoader(ModelLoader):
    """Loader for cloud-based models."""
    
    def _load_model(
        self,
        config: AnyModelConfig,
        submodel_type: Optional[SubModelType] = None,
    ) -> AnyModel:
        """Load cloud model - returns API client wrapper."""
        
        if submodel_type is not None:
            raise ValueError("Cloud models don't have submodels")
        
        from my_cloud_integration import MyCloudClient
        
        # Create API client
        client = MyCloudClient(
            api_base_url=config.api_base_url,
            provider_settings=config.provider_settings
        )
        
        # Return wrapped model
        return CloudModelWrapper(
            client=client,
            config=config,
            model_name=config.cloud_model_id
        )
    
    def _get_model_path(self, config: AnyModelConfig) -> Path:
        """Cloud models don't have file paths - return dummy path."""
        return Path(config.key)
```

#### Step 3: Create API Endpoint for Registration

```python
@model_manager_router.post(
    "/register_cloud_model",
    operation_id="register_cloud_model",
)
async def register_cloud_model(
    provider: CloudProviderType = Body(description="Cloud provider"),
    model_id: str = Body(description="Model ID on cloud service"),
    name: str = Body(description="Name for this model in InvokeAI"),
    provider_settings: Dict[str, Any] = Body(
        description="Provider-specific settings"
    ),
) -> AnyModelConfig:
    """Register a cloud model without file path."""
    
    # Create config based on provider
    if provider == CloudProviderType.MyCloud:
        config = MyCloudModelConfig(
            key=slugify(name),
            name=name,
            cloud_model_id=model_id,
            provider_settings=provider_settings,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
    
    # Add to database
    added_config = ApiDependencies.invoker.services.model_manager.store.add_model(config)
    
    return added_config
```

#### Step 4: Add to Config Factory

```python
# In /invokeai/backend/model_manager/configs/factory.py

AnyModelConfig = Annotated[
    Union[
        # ... existing configs ...
        Annotated[MyCloudModelConfig, MyCloudModelConfig.get_tag()],
        # ... other configs ...
    ],
    Discriminator(Config_Base.get_model_discriminator_value),
]
```

#### Step 5: Create Invocation

```python
@invocation(
    "my_cloud_image_generator",
    title="Generate Image - MyCloud",
    tags=["image", "generation", "mycloud"],
    category="image",
)
class MyCloudImageGeneratorInvocation(BaseInvocation):
    """Generate an image using MyCloud API."""
    
    model: ModelIdentifierField = InputField(
        description="Cloud model to use",
        ui_model_base=BaseModelType.CloudAPI,
        ui_model_type=ModelType.Main,
    )
    
    prompt: str = InputField(description="Image generation prompt")
    negative_prompt: Optional[str] = InputField(default=None)
    seed: Optional[int] = InputField(default=None)
    quality: str = InputField(default="standard")
    
    def invoke(self, context: InvocationContext) -> ImageOutput:
        """Generate image via cloud API."""
        
        # Verify model exists
        if not context.models.exists(self.model.key):
            raise ValueError(f"Unknown model: {self.model.key}")
        
        # Load cloud model (creates API client)
        loaded_model = context.models.load(self.model)
        cloud_model = loaded_model.model  # CloudModelWrapper
        
        # Call cloud API
        image_data = cloud_model.generate(
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            seed=self.seed,
            quality=self.quality,
        )
        
        # Save image
        image = Image.open(io.BytesIO(image_data))
        image_name = context.images.save(image)
        
        return ImageOutput(image=ImageField(image_name=image_name))
```

---

## 7. Key Architecture Patterns

### 7.1 Discriminated Union for Polymorphism

```python
AnyModelConfig = Annotated[
    Union[
        Annotated[Type1Config, Type1Config.get_tag()],
        Annotated[Type2Config, Type2Config.get_tag()],
        # ...
    ],
    Discriminator(Config_Base.get_model_discriminator_value),
]
```

**Benefit**: Type-safe polymorphism at runtime with Pydantic validation

### 7.2 Registry Pattern for Loaders

```python
@ModelLoaderRegistry.register(
    base=BaseModelType.Flux, 
    type=ModelType.LoRA, 
    format=ModelFormat.LyCORIS
)
class LoRALoader(ModelLoader):
    pass
```

**Benefit**: Automatic loader discovery without hard-coded conditionals

### 7.3 Config Factory Pattern

```python
result = ModelConfigFactory.from_model_on_disk(
    mod=model_path,
    override_fields=fields,
)
config = result.config  # Type: AnyModelConfig
```

**Benefit**: Automatic model type detection by trying all config types

### 7.4 Lazy Model Loading

```python
# In invocation: Just append LoRAField, don't load
output.transformer.loras.append(LoRAField(...))

# During inference: Load at point of use
for lora in loras:
    model = context.models.load(lora.lora.key)
```

**Benefit**: Defers expensive I/O until necessary

### 7.5 Separation of Concerns

```
Config (what the model is)
  ↓
Loader (how to load it)
  ↓
Invocation (how to use it)
  ↓
Infrastructure (model manager, caching, etc.)
```

**Benefit**: Each component has single responsibility

---

## 8. Implementation Checklist for Cloud Models

- [ ] Create config class extending `CloudModelConfig`
  - [ ] Define provider-specific fields
  - [ ] Implement `from_model_on_disk()` to raise `NotACloudModelError`

- [ ] Create loader class extending `ModelLoader`
  - [ ] Implement `_load_model()` to create API client wrapper
  - [ ] Implement `_get_model_path()` (return dummy path)
  - [ ] Register with `@ModelLoaderRegistry.register()`

- [ ] Create API endpoint for registration
  - [ ] Add POST endpoint to `model_manager_router`
  - [ ] Accept provider, model_id, name, settings
  - [ ] Call `model_manager.store.add_model()`

- [ ] Add config to factory discriminated union
  - [ ] Import config class
  - [ ] Add to AnyModelConfig Union

- [ ] Create invocation class
  - [ ] Accept ModelIdentifierField for cloud model
  - [ ] Implement `invoke()` method
  - [ ] Call `context.models.load()` to get API client
  - [ ] Execute API call
  - [ ] Save results (images, etc.)
  - [ ] Return appropriate output

- [ ] Add tests
  - [ ] Registration flow
  - [ ] Config validation
  - [ ] Loader integration
  - [ ] Invocation execution

---

## 9. Key Files Reference

### Core LoRA System
- `/invokeai/backend/model_manager/configs/lora.py` - LoRA config classes
- `/invokeai/backend/model_manager/load/model_loaders/lora.py` - LoRA loader
- `/invokeai/app/invocations/flux_lora_loader.py` - LoRA invocations

### Model Management
- `/invokeai/app/services/model_manager/` - Model manager service
- `/invokeai/app/services/model_records/` - Model database
- `/invokeai/app/services/model_install/` - Model installation
- `/invokeai/backend/model_manager/configs/factory.py` - Model config factory
- `/invokeai/backend/model_manager/load/model_loader_registry.py` - Loader registry

### Cloud Models
- `/invokeai/backend/model_manager/configs/cloud_models.py` - Cloud model configs

### API Routes
- `/invokeai/app/api/routers/model_manager.py` - Model management API

### Patching/Application
- `/invokeai/backend/patches/layers/lora_layer_base.py` - LoRA layer base
- `/invokeai/backend/stable_diffusion/extensions/lora.py` - LoRA extension

---

## 10. Summary

LoRA models in InvokeAI follow a clean, extensible architectural pattern:

1. **Config**: Type-safe model configuration with validation
2. **Loader**: Registry-based loader for flexible instantiation
3. **Registration**: Database-backed model management
4. **Invocation**: Workflow-aware model composition
5. **Execution**: Lazy loading and caching at point of use

Cloud models should follow the same pattern but replace file-based loading with API calls. The key differences:

| Aspect | LoRA | Cloud Models |
|--------|------|------------|
| Config Source | Disk file detection | Manual API registration |
| Loader Role | Load weights from file | Create API client |
| Path Resolution | File system path | Cloud provider endpoint |
| Execution | Weight patching | API HTTP calls |
| Caching | Cached state dict | Cached API client |

This pattern ensures that cloud models integrate seamlessly with existing InvokeAI workflows while maintaining clear separation of concerns.
