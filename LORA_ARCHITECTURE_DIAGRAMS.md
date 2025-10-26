# LoRA Architecture - Visual Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    InvokeAI Model System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                   MODEL DISCOVERY & REGISTRATION                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model File on Disk                                             │
│         │                                                        │
│         v                                                        │
│  ModelInstallService.register_path()                            │
│         │                                                        │
│         v                                                        │
│  ModelConfigFactory.from_model_on_disk()                        │
│    ├─ Try LoRA_LyCORIS_FLUX_Config                              │
│    ├─ Try LoRA_LyCORIS_SDXL_Config                              │
│    ├─ Try LoRA_Diffusers_Config                                 │
│    ├─ Try ... (all config types)                                │
│    └─ Return matching config or Unknown_Config                  │
│         │                                                        │
│         v                                                        │
│  ModelRecordService.add_model(config)                           │
│    └─ Store in database with key, hash, path, etc.              │
│         │                                                        │
│         v                                                        │
│  Model available in system via key                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    WORKFLOW COMPOSITION                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User selects model from UI                                     │
│    ├─ Model config loaded from database                         │
│    └─ ModelIdentifierField created:                             │
│       ├─ key: "flux-lora-001"                                   │
│       ├─ hash: "abc123..."                                      │
│       ├─ name: "Flux LoRA Style"                                │
│       ├─ base: BaseModelType.Flux                               │
│       └─ type: ModelType.LoRA                                   │
│         │                                                        │
│         v                                                        │
│  User creates "Apply LoRA - FLUX" invocation                    │
│    ├─ Input: ModelIdentifierField (the LoRA)                    │
│    ├─ Input: weight (default 0.75)                              │
│    └─ Input: transformer/clip/t5_encoder fields                 │
│         │                                                        │
│         v                                                        │
│  FluxLoRALoaderInvocation.invoke()                              │
│    ├─ Validate LoRA exists: context.models.exists(key)          │
│    └─ Append LoRAField to output:                               │
│       ├─ lora: ModelIdentifierField                             │
│       └─ weight: float                                          │
│         │                                                        │
│         v                                                        │
│  Output: TransformerField with .loras list populated            │
│    └─ Passed to next invocation (e.g., FLUX generation)         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                   INFERENCE & EXECUTION                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FLUX Generation Invocation receives TransformerField           │
│    └─ TransformerField.loras: [LoRAField, LoRAField, ...]       │
│         │                                                        │
│         v                                                        │
│  For each LoRA in loras list:                                   │
│    │                                                             │
│    ├─ context.models.load(lora.lora.key)                        │
│    │   ├─ Lookup config in database                             │
│    │   ├─ ModelLoaderRegistry.get_implementation()              │
│    │   │   └─ Registry key: flux-lora-lycorIs                   │
│    │   │   └─ Returns LoRALoader class                          │
│    │   └─ LoRALoader(config).load_model(config)                 │
│    │       │                                                    │
│    │       ├─ _get_model_path(): Resolve file path              │
│    │       │   └─ Store base type for later use                 │
│    │       │                                                    │
│    │       ├─ _load_model():                                    │
│    │       │   ├─ Load state dict from .safetensors file        │
│    │       │   ├─ Detect format (Kohya? Diffusers? Toolkit?)    │
│    │       │   ├─ Convert format to internal representation     │
│    │       │   └─ Convert to target dtype (fp16)                │
│    │       │                                                    │
│    │       └─ Cache in ModelCache                               │
│    │         └─ Key: (lora.key, submodel_type)                  │
│    │                                                             │
│    └─ LoRA model now ready for use                              │
│         │                                                        │
│         v                                                        │
│  Apply LoRAs to transformer layers:                             │
│    ├─ LoRAExt.patch_unet()                                      │
│    ├─ Load LoRA model from cache                                │
│    ├─ LayerPatcher.apply_smart_model_patch()                    │
│    │   ├─ Find matching layers (prefix: "lora_transformer_")    │
│    │   ├─ Calculate weight: scale = alpha / rank                │
│    │   └─ Apply LoRA weights: W' = W + weight * LoRA            │
│    └─ Repeat for next LoRA                                      │
│         │                                                        │
│         v                                                        │
│  Generate image with patched transformer                        │
│         │                                                        │
│         v                                                        │
│  Release LoRA models from cache                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Config Hierarchy

```
Config_Base (Abstract Base)
│
├── LoRA_Config_Base (Abstract)
│   ├─ type: ModelType.LoRA
│   ├─ trigger_phrases: set[str] | None
│   └─ default_settings: LoraModelDefaultSettings
│
│   ├── LoRA_OMI_Config_Base
│   │   ├── LoRA_OMI_SDXL_Config (base=SDXL)
│   │   └── LoRA_OMI_FLUX_Config (base=Flux)
│   │
│   ├── LoRA_LyCORIS_Config_Base
│   │   ├── LoRA_LyCORIS_SD1_Config (base=SD1)
│   │   ├── LoRA_LyCORIS_SD2_Config (base=SD2)
│   │   ├── LoRA_LyCORIS_SDXL_Config (base=SDXL)
│   │   └── LoRA_LyCORIS_FLUX_Config (base=Flux)
│   │
│   └── LoRA_Diffusers_Config_Base
│       ├── LoRA_Diffusers_SD1_Config (base=SD1)
│       ├── LoRA_Diffusers_SD2_Config (base=SD2)
│       ├── LoRA_Diffusers_SDXL_Config (base=SDXL)
│       └── LoRA_Diffusers_FLUX_Config (base=Flux)
│
├── ControlLoRA_LyCORIS_FLUX_Config
│   ├─ type: ModelType.ControlLoRA
│   └─ base: BaseModelType.Flux
│
└── CloudModelConfig (Cloud-based models)
    ├─ type: ModelType.Main
    ├─ base: BaseModelType.CloudAPI
    ├─ format: ModelFormat.CloudREST
    ├─ provider: CloudProviderType
    ├─ cloud_model_id: str
    └─ provider_settings: Dict[str, Any]
```

---

## 3. Model Loader Registry Pattern

```
ModelLoaderRegistry
│
├─ register(base, type, format) decorator
│   ├─ Creates registry key: f"{base.value}-{type.value}-{format.value}"
│   └─ Stores loader class in _registry dict
│
└─ get_implementation(config, submodel_type)
   ├─ Build key from config properties
   ├─ Try specific key: (config.base, config.type, config.format)
   ├─ Try wildcard key: (BaseModelType.Any, config.type, config.format)
   └─ Return loader class or raise NotImplementedError

REGISTRY ENTRIES:

Key: "flux-lora-omi"
└─ @ModelLoaderRegistry.register(base=Flux, type=LoRA, format=OMI)
   └─ class LoRALoader

Key: "sdxl-lora-omi"
└─ @ModelLoaderRegistry.register(base=SDXL, type=LoRA, format=OMI)
   └─ class LoRALoader

Key: "any-lora-diffusers"
└─ @ModelLoaderRegistry.register(base=Any, type=LoRA, format=Diffusers)
   └─ class LoRALoader

Key: "cloudapi-main-cloudrest"
└─ @ModelLoaderRegistry.register(base=CloudAPI, type=Main, format=CloudREST)
   └─ class CloudModelLoader
```

---

## 4. Config Factory Pattern (Discriminated Union)

```
AnyModelConfig = Union[
    Main_Diffusers_SD1_Config,
    Main_Diffusers_SD2_Config,
    Main_Diffusers_SDXL_Config,
    LoRA_LyCORIS_SD1_Config,
    LoRA_LyCORIS_SDXL_Config,
    LoRA_LyCORIS_FLUX_Config,
    LoRA_OMI_SDXL_Config,
    LoRA_OMI_FLUX_Config,
    LoRA_Diffusers_SDXL_Config,
    ControlLoRA_LyCORIS_FLUX_Config,
    CloudModelConfig,         <-- Cloud models included!
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
    Unknown_Config,
]

ModelConfigFactory.from_model_on_disk(path):
    result = try each config type:
        ├─ Main_Diffusers_SD1_Config.from_model_on_disk()
        │   └─ If valid (no exception) → return config
        ├─ LoRA_LyCORIS_FLUX_Config.from_model_on_disk()
        │   └─ If valid → return config
        ├─ LoRA_Diffusers_FLUX_Config.from_model_on_disk()
        │   └─ If valid → return config
        ├─ ... (try all types) ...
        └─ Unknown_Config.from_model_on_disk()
            └─ Always succeeds as fallback
    
    return result.config  # Type: AnyModelConfig (properly discriminated)
```

---

## 5. LoRA Invocation Flow

```
┌─────────────────────────────────────────────────┐
│  FluxLoRALoaderInvocation                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Inputs:                                        │
│  ├─ lora: ModelIdentifierField                  │
│  ├─ weight: float (0.75)                        │
│  ├─ transformer: TransformerField | None        │
│  ├─ clip: CLIPField | None                      │
│  └─ t5_encoder: T5EncoderField | None           │
│                                                 │
│  invoke(context):                               │
│  ├─ lora_key = self.lora.key                    │
│  ├─ Verify exists: context.models.exists(key)   │
│  ├─ Check no duplicates                         │
│  └─ Build output by appending LoRA:             │
│     ├─ output.transformer = ...                 │
│     ├─ output.transformer.loras.append(         │
│     │   LoRAField(                              │
│     │     lora=self.lora,                       │
│     │     weight=self.weight                    │
│     │   )                                       │
│     │ )                                         │
│     ├─ output.clip = ...                        │
│     ├─ output.clip.loras.append(...)            │
│     ├─ output.t5_encoder = ...                  │
│     └─ output.t5_encoder.loras.append(...)      │
│                                                 │
│  return FluxLoRALoaderOutput(                   │
│    transformer=output.transformer,              │
│    clip=output.clip,                            │
│    t5_encoder=output.t5_encoder                 │
│  )                                              │
│                                                 │
└─────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────┐
│  FLUX Generation Invocation                     │
│  (receives transformer with loras list)         │
└─────────────────────────────────────────────────┘
```

---

## 6. Model Loading Sequence

```
context.models.load(model_identifier_field)
    │
    ├─ Get config from database using key
    │   └─ config = ModelRecordService.get_model(key)
    │
    ├─ Determine loader class from config
    │   └─ loader_class = ModelLoaderRegistry.get_implementation(config, None)
    │
    ├─ Instantiate loader
    │   └─ loader = loader_class(app_config, logger, ram_cache)
    │
    └─ Load model
        └─ loader.load_model(config)
            │
            ├─ Call _get_model_path(config)
            │   ├─ Store config.base in self._model_base
            │   ├─ For Diffusers: find pytorch_lora_weights.safetensors
            │   └─ return resolved_path
            │
            ├─ Check model exists in cache
            │   └─ key = (config.key, submodel_type)
            │   └─ If in cache → return immediately
            │
            └─ Load model (if not in cache)
                ├─ Call _load_model(config)
                │   ├─ Load state dict from disk
                │   │   ├─ If .safetensors: load_file()
                │   │   └─ If .pt/.pth: torch.load()
                │   │
                │   ├─ Clean up unused keys
                │   │
                │   ├─ Convert format if needed
                │   │   └─ If OMI → convert_from_omi()
                │   │
                │   ├─ Detect specific format (Flux)
                │   │   ├─ If Kohya format → convert_kohya()
                │   │   ├─ If Diffusers format → convert_diffusers()
                │   │   ├─ If OneTrainer format → convert_onetrainer()
                │   │   ├─ If Control format → convert_control()
                │   │   └─ If AIToolkit format → convert_aitoolkit()
                │   │
                │   ├─ Convert to internal model representation
                │   │   └─ model = lora_model_from_*_state_dict()
                │   │
                │   └─ Convert dtype
                │       └─ model.to(dtype=self._torch_dtype)
                │
                ├─ Cache model
                │   └─ ram_cache.put(key, model)
                │
                └─ return LoadedModel(config, cache_record, cache)
```

---

## 7. Cloud Models Pattern (Same Architecture)

```
Cloud Model Registration (differs from LoRA):
    │
    ├─ User calls API endpoint (POST /v2/models/register_cloud_model)
    │   ├─ provider: CloudProviderType
    │   ├─ model_id: str
    │   ├─ name: str
    │   └─ provider_settings: Dict[str, Any]
    │
    ├─ Create CloudModelConfig instance
    │   ├─ type: ModelType.Main
    │   ├─ base: BaseModelType.CloudAPI
    │   ├─ format: ModelFormat.CloudREST
    │   ├─ provider: CloudProviderType.MyCloud
    │   ├─ cloud_model_id: str
    │   └─ provider_settings: Dict[str, Any]
    │
    └─ Add to database
        └─ ModelRecordService.add_model(config)

Cloud Model Loading (same pattern, different implementation):
    │
    ├─ loader_class = ModelLoaderRegistry.get_implementation()
    │   └─ Key: cloudapi-main-cloudrest
    │   └─ Returns CloudModelLoader
    │
    └─ loader._load_model(config)
        ├─ Create API client
        │   └─ client = MyCloudClient(
        │       api_base_url=config.api_base_url,
        │       auth=config.provider_settings.get("api_key")
        │   )
        │
        └─ Return wrapped model
            └─ CloudModelWrapper(client, config)

LoRA Loading:
    └─ loader._load_model(config)
        └─ Load state dict from file → return ModelPatch

Cloud Model Loading:
    └─ loader._load_model(config)
        └─ Create API client → return CloudModelWrapper

Invocation Usage (identical):
    ├─ LoRA: context.models.load(lora_key) → ModelPatch → patch layers
    └─ Cloud: context.models.load(model_key) → CloudWrapper → call API
```

---

## 8. Key Data Flow Diagram

```
User Interface
    │
    ├─ Model Selection
    │   └─ Dropdown shows all registered models
    │   └─ Each = ModelRecordService entry
    │
    └─ Workflow Creation
        │
        ├─ Add "Apply LoRA" invocation
        │   └─ Input: ModelIdentifierField (selected LoRA)
        │
        └─ Add "Generate Image" invocation
            └─ Input: TransformerField (contains .loras list)

Workflow Execution
    │
    ├─ FluxLoRALoaderInvocation
    │   └─ Output: TransformerField (with LoRA appended)
    │
    └─ FLUX Generation Invocation
        │
        ├─ Load transformer main model
        ├─ For each LoRA in transformer.loras:
        │   ├─ Load LoRA (ModelLoaderRegistry)
        │   └─ Patch transformer layers
        └─ Generate image

Output
    └─ Image file (with LoRA effects applied)
```

---

## Summary Table: LoRA vs Cloud Models

```
┌─────────────────┬────────────────────────┬──────────────────────┐
│ Aspect          │ LoRA Models            │ Cloud Models         │
├─────────────────┼────────────────────────┼──────────────────────┤
│ Config Class    │ LoRA_*_Config          │ CloudModelConfig     │
│ Config Source   │ from_model_on_disk()   │ Manual registration  │
│ Registration    │ Auto-discovery         │ API endpoint         │
│ Path            │ File system path       │ Dummy path (ignored) │
│ Loading         │ Load state dict        │ Create API client    │
│ Loader Registry │ @register(any, lora, *) │ @register(cloudapi, │
│                 │                        │   main, cloudrest)   │
│ Application     │ Layer patching         │ HTTP API calls       │
│ Caching         │ State dict tensors     │ API client instance  │
│ Performance     │ Local GPU inference    │ Remote cloud service │
│ Dependencies    │ PyTorch, safetensors   │ requests, aiohttp    │
└─────────────────┴────────────────────────┴──────────────────────┘
```

---

END OF DIAGRAMS
