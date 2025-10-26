"""FastAPI router for cloud model management."""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Query
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from invokeai.app.api.dependencies import ApiDependencies
from invokeai.app.services.cloud_providers import (
    GoogleGeminiProvider,
    GoogleImagenProvider,
    OpenAIProvider,
)
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType

# Load .env file from project root
# Walk up the directory tree to find the project root with .env file
current_dir = Path(__file__).resolve().parent
print(f"[CLOUD DEBUG] Starting .env search from: {current_dir}")
while current_dir != current_dir.parent:
    env_file = current_dir / ".env"
    print(f"[CLOUD DEBUG] Checking for .env at: {env_file}")
    if env_file.exists():
        print(f"[CLOUD DEBUG] Found .env file at: {env_file}")
        load_dotenv(env_file)
        # Print what keys we found
        print(f"[CLOUD DEBUG] GOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
        print(f"[CLOUD DEBUG] GOOGLE_CLOUD_PROJECT set: {bool(os.getenv('GOOGLE_CLOUD_PROJECT'))}")
        print(f"[CLOUD DEBUG] OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")
        break
    current_dir = current_dir.parent
else:
    # Fallback: try loading from current working directory
    print(f"[CLOUD DEBUG] No .env found in parent dirs, trying cwd")
    load_dotenv()

cloud_models_router = APIRouter(prefix="/v2/cloud", tags=["cloud_models"])


class ProviderStatus(str, Enum):
    """Status of a cloud provider."""

    CONFIGURED = "configured"  # API key is set
    NOT_CONFIGURED = "not_configured"  # No API key found
    VALID = "valid"  # API key is set and working
    INVALID = "invalid"  # API key is set but not working
    ERROR = "error"  # Error checking status


class CloudProviderInfo(BaseModel):
    """Information about a cloud provider."""

    provider: CloudProviderType
    name: str
    status: ProviderStatus
    is_configured: bool = Field(description="Whether API credentials are configured")
    is_valid: Optional[bool] = Field(default=None, description="Whether credentials are valid (null if not checked)")
    supported_models: List[str]
    error_message: Optional[str] = None


class CloudModelInfo(BaseModel):
    """Information about a cloud model."""

    key: str
    provider: CloudProviderType
    model_id: str
    name: str
    description: str
    supported_sizes: List[str]
    cost_per_image: Dict[str, float]  # size -> cost mapping
    features: List[str]


class CostEstimate(BaseModel):
    """Cost estimate for a generation request."""

    provider: CloudProviderType
    model_id: str
    num_images: int
    size: str
    quality: Optional[str] = None
    estimated_cost: float
    currency: str = "USD"


def _check_api_key_configured(provider: CloudProviderType) -> bool:
    """Check if API key is configured for a provider (without exposing the key)."""
    if provider == CloudProviderType.GoogleGemini:
        return bool(os.getenv("GOOGLE_API_KEY"))
    elif provider == CloudProviderType.GoogleImagen:
        return bool(os.getenv("GOOGLE_CLOUD_PROJECT")) and bool(os.getenv("GOOGLE_CLOUD_REGION"))
    elif provider == CloudProviderType.OpenAI:
        return bool(os.getenv("OPENAI_API_KEY"))
    return False


async def _check_provider_status(provider: CloudProviderType) -> tuple[ProviderStatus, Optional[str]]:
    """Check the status of a provider's credentials."""
    is_configured = _check_api_key_configured(provider)

    if not is_configured:
        return ProviderStatus.NOT_CONFIGURED, None

    # Try to validate credentials
    try:
        if provider == CloudProviderType.GoogleGemini:
            provider_instance = GoogleGeminiProvider(
                api_key=os.getenv("GOOGLE_API_KEY", ""),
                config={}
            )
            is_valid = await provider_instance.validate_credentials()
        elif provider == CloudProviderType.GoogleImagen:
            # GoogleImagenProvider gets project_id/region from environment variables
            provider_instance = GoogleImagenProvider(
                api_key="",  # Not used by Imagen (uses Google Cloud credentials)
                config={}
            )
            is_valid = await provider_instance.validate_credentials()
        elif provider == CloudProviderType.OpenAI:
            provider_instance = OpenAIProvider(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                config={}
            )
            is_valid = await provider_instance.validate_credentials()
        else:
            return ProviderStatus.ERROR, f"Unknown provider: {provider}"

        return ProviderStatus.VALID if is_valid else ProviderStatus.INVALID, None

    except Exception as e:
        return ProviderStatus.ERROR, str(e)


@cloud_models_router.get(
    "/providers",
    operation_id="list_cloud_providers",
    responses={200: {"description": "List of cloud providers"}},
)
async def list_cloud_providers(
    check_credentials: bool = Query(
        default=False, description="Whether to validate credentials (slower but shows if keys work)"
    )
) -> List[CloudProviderInfo]:
    """Get list of all cloud providers with their status."""
    providers_info = []

    # Google Gemini
    gemini_configured = _check_api_key_configured(CloudProviderType.GoogleGemini)
    if check_credentials and gemini_configured:
        gemini_status, error = await _check_provider_status(CloudProviderType.GoogleGemini)
        is_valid = gemini_status == ProviderStatus.VALID
    else:
        gemini_status = ProviderStatus.CONFIGURED if gemini_configured else ProviderStatus.NOT_CONFIGURED
        is_valid = None
        error = None

    providers_info.append(
        CloudProviderInfo(
            provider=CloudProviderType.GoogleGemini,
            name="Google Gemini 2.5 Flash",
            status=gemini_status,
            is_configured=gemini_configured,
            is_valid=is_valid,
            supported_models=["gemini-2.5-flash-image"],
            error_message=error,
        )
    )

    # Google Imagen
    imagen_configured = _check_api_key_configured(CloudProviderType.GoogleImagen)
    if check_credentials and imagen_configured:
        imagen_status, error = await _check_provider_status(CloudProviderType.GoogleImagen)
        is_valid = imagen_status == ProviderStatus.VALID
    else:
        imagen_status = ProviderStatus.CONFIGURED if imagen_configured else ProviderStatus.NOT_CONFIGURED
        is_valid = None
        error = None

    providers_info.append(
        CloudProviderInfo(
            provider=CloudProviderType.GoogleImagen,
            name="Google Imagen 4 Ultra",
            status=imagen_status,
            is_configured=imagen_configured,
            is_valid=is_valid,
            supported_models=["imagen-4.0-ultra-generate-001"],
            error_message=error,
        )
    )

    # OpenAI
    openai_configured = _check_api_key_configured(CloudProviderType.OpenAI)
    if check_credentials and openai_configured:
        openai_status, error = await _check_provider_status(CloudProviderType.OpenAI)
        is_valid = openai_status == ProviderStatus.VALID
    else:
        openai_status = ProviderStatus.CONFIGURED if openai_configured else ProviderStatus.NOT_CONFIGURED
        is_valid = None
        error = None

    providers_info.append(
        CloudProviderInfo(
            provider=CloudProviderType.OpenAI,
            name="OpenAI DALL-E",
            status=openai_status,
            is_configured=openai_configured,
            is_valid=is_valid,
            supported_models=["dall-e-3", "dall-e-2"],
            error_message=error,
        )
    )

    return providers_info


@cloud_models_router.get(
    "/providers/{provider}/status",
    operation_id="get_cloud_provider_status",
    responses={
        200: {"description": "Provider status retrieved successfully"},
        404: {"description": "Provider not found"},
    },
)
async def get_cloud_provider_status(provider: CloudProviderType) -> CloudProviderInfo:
    """Get status of a specific cloud provider."""
    providers = await list_cloud_providers(check_credentials=True)
    for p in providers:
        if p.provider == provider:
            return p
    raise HTTPException(status_code=404, detail=f"Provider {provider} not found")


@cloud_models_router.get(
    "/models",
    operation_id="list_cloud_models",
    responses={200: {"description": "List of available cloud models"}},
)
async def list_cloud_models(
    provider: Optional[CloudProviderType] = Query(default=None, description="Filter by provider"),
    only_configured: bool = Query(default=False, description="Only show models for configured providers"),
) -> List[CloudModelInfo]:
    """Get list of available cloud models."""
    models = []

    # Check provider configuration status
    gemini_configured = _check_api_key_configured(CloudProviderType.GoogleGemini)
    imagen_configured = _check_api_key_configured(CloudProviderType.GoogleImagen)
    openai_configured = _check_api_key_configured(CloudProviderType.OpenAI)

    # Google Gemini 2.5 Flash
    if (not provider or provider == CloudProviderType.GoogleGemini) and (
        not only_configured or gemini_configured
    ):
        models.append(
            CloudModelInfo(
                key="gemini-2.5-flash",
                provider=CloudProviderType.GoogleGemini,
                model_id="gemini-2.5-flash-image",
                name="Gemini 2.5 Flash Image",
                description="Google's fast and affordable image generation model with 10 aspect ratios",
                supported_sizes=["1024x1024", "1536x1024", "1024x1536", "1152x1536", "1536x1152"],
                cost_per_image={"default": 0.039},
                features=["seed", "10_aspect_ratios", "natural_language"],
            )
        )

    # Google Imagen 4 Ultra
    if (not provider or provider == CloudProviderType.GoogleImagen) and (
        not only_configured or imagen_configured
    ):
        models.append(
            CloudModelInfo(
                key="imagen-4-ultra",
                provider=CloudProviderType.GoogleImagen,
                model_id="imagen-4.0-ultra-generate-001",
                name="Imagen 4 Ultra",
                description="Google's premium image generation with SynthID watermark and safety filters",
                supported_sizes=["1024x1024", "768x1024", "1024x768", "576x1024", "1024x576"],
                cost_per_image={"default": 0.06},
                features=["batch_generation", "synthid_watermark", "safety_filters", "prompt_enhancement"],
            )
        )

    # OpenAI DALL-E 3
    if (not provider or provider == CloudProviderType.OpenAI) and (not only_configured or openai_configured):
        models.append(
            CloudModelInfo(
                key="dall-e-3",
                provider=CloudProviderType.OpenAI,
                model_id="dall-e-3",
                name="DALL-E 3",
                description="OpenAI's latest image generation with quality and style controls",
                supported_sizes=["1024x1024", "1792x1024", "1024x1792"],
                cost_per_image={
                    "1024x1024_standard": 0.04,
                    "1024x1024_hd": 0.08,
                    "1792x1024_standard": 0.08,
                    "1792x1024_hd": 0.12,
                    "1024x1792_standard": 0.08,
                    "1024x1792_hd": 0.12,
                },
                features=["quality_control", "style_selection", "revised_prompts"],
            )
        )

        # OpenAI DALL-E 2
        models.append(
            CloudModelInfo(
                key="dall-e-2",
                provider=CloudProviderType.OpenAI,
                model_id="dall-e-2",
                name="DALL-E 2",
                description="OpenAI's affordable model for rapid iteration",
                supported_sizes=["1024x1024", "512x512", "256x256"],
                cost_per_image={"1024x1024": 0.02, "512x512": 0.018, "256x256": 0.016},
                features=["batch_generation"],
            )
        )

    return models


@cloud_models_router.post(
    "/estimate_cost",
    operation_id="estimate_cloud_generation_cost",
    responses={
        200: {"description": "Cost estimated successfully"},
        400: {"description": "Invalid parameters"},
    },
)
async def estimate_cloud_generation_cost(
    provider: CloudProviderType,
    model_id: str,
    num_images: int = 1,
    width: int = 1024,
    height: int = 1024,
    quality: Optional[str] = None,
) -> CostEstimate:
    """Estimate the cost of a cloud generation request."""
    size = f"{width}x{height}"

    # Calculate cost based on provider and model
    if provider == CloudProviderType.GoogleGemini and model_id == "gemini-2.5-flash-image":
        cost_per_image = 0.039
    elif provider == CloudProviderType.GoogleImagen and model_id == "imagen-4.0-ultra-generate-001":
        cost_per_image = 0.06
    elif provider == CloudProviderType.OpenAI and model_id == "dall-e-3":
        # DALL-E 3 pricing varies by size and quality
        quality = quality or "standard"
        if size == "1024x1024":
            cost_per_image = 0.04 if quality == "standard" else 0.08
        else:  # 1792x1024 or 1024x1792
            cost_per_image = 0.08 if quality == "standard" else 0.12
    elif provider == CloudProviderType.OpenAI and model_id == "dall-e-2":
        # DALL-E 2 pricing varies by size
        if size == "1024x1024":
            cost_per_image = 0.02
        elif size == "512x512":
            cost_per_image = 0.018
        elif size == "256x256":
            cost_per_image = 0.016
        else:
            cost_per_image = 0.02  # Default to 1024x1024 pricing
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {provider}/{model_id}")

    estimated_cost = cost_per_image * num_images

    return CostEstimate(
        provider=provider,
        model_id=model_id,
        num_images=num_images,
        size=size,
        quality=quality,
        estimated_cost=round(estimated_cost, 4),
    )


@cloud_models_router.post(
    "/models/register",
    operation_id="register_cloud_model",
    responses={
        201: {"description": "Cloud model registered successfully"},
        400: {"description": "Invalid parameters"},
        409: {"description": "Model already registered"},
    },
    status_code=201,
)
async def register_cloud_model(
    provider: CloudProviderType,
    model_id: str = Query(description="Cloud model ID (e.g., 'gemini-2.5-flash-image')"),
    name: Optional[str] = Query(default=None, description="Display name for the model"),
    description: Optional[str] = Query(default=None, description="Model description"),
) -> dict:
    """Register a cloud model with the model manager.

    This endpoint creates a cloud model configuration and registers it with InvokeAI's
    model manager, making it available for use in workflows.

    Args:
        provider: Cloud provider type
        model_id: Model ID on the cloud service
        name: Optional display name (defaults to model_id)
        description: Optional description

    Returns:
        dict with model key and registration status
    """
    from invokeai.backend.model_manager.configs.cloud_models import (
        GeminiFlashImageConfig,
        ImagenUltraConfig,
        OpenAIImageConfig,
    )

    # Check if provider is configured
    if not _check_api_key_configured(provider):
        raise HTTPException(
            status_code=400,
            detail=f"{provider} is not configured. Please set required API keys in .env file.",
        )

    # Create appropriate config based on provider and model
    try:
        from invokeai.backend.model_manager.taxonomy import ModelSourceType

        # Cloud models don't exist on disk, so we provide dummy values for file-based fields
        cloud_model_key = f"cloud/{provider}/{model_id}"

        if provider == CloudProviderType.GoogleGemini and model_id == "gemini-2.5-flash-image":
            config = GeminiFlashImageConfig(
                key=cloud_model_key,
                hash="cloud-model",  # Cloud models don't have file hashes
                path=cloud_model_key,  # Use key as virtual path
                file_size=0,  # Cloud models have no file size
                source=f"https://ai.google.dev/gemini-api/docs/image-generation",
                source_type=ModelSourceType.CLOUD,
                name=name or "Gemini 2.5 Flash Image",
                description=description or "Google's fast and affordable image generation model",
                provider=provider,
                cloud_model_id=model_id,
            )
        elif provider == CloudProviderType.GoogleImagen and model_id == "imagen-4.0-ultra-generate-001":
            config = ImagenUltraConfig(
                key=cloud_model_key,
                hash="cloud-model",
                path=cloud_model_key,
                file_size=0,
                source=f"https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api",
                source_type=ModelSourceType.CLOUD,
                name=name or "Imagen 4 Ultra",
                description=description or "Google's premium image generation with SynthID watermark",
                provider=provider,
                cloud_model_id=model_id,
            )
        elif provider == CloudProviderType.OpenAI and model_id in ["dall-e-3", "dall-e-2"]:
            config = OpenAIImageConfig(
                key=cloud_model_key,
                hash="cloud-model",
                path=cloud_model_key,
                file_size=0,
                source=f"https://platform.openai.com/docs/guides/image-generation",
                source_type=ModelSourceType.CLOUD,
                name=name or f"DALL-E {model_id.split('-')[-1].upper()}",
                description=description or "OpenAI's image generation model",
                provider=provider,
                cloud_model_id=model_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model: {provider}/{model_id}",
            )

        # Register with model manager
        model_manager = ApiDependencies.invoker.services.model_manager.store

        # Check if already registered
        try:
            existing = model_manager.get_model(config.key)
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Model {config.key} is already registered",
                )
        except Exception:
            # Model doesn't exist, proceed with registration
            pass

        # Add to model manager
        model_manager.add_model(config.key, config)

        return {
            "key": config.key,
            "name": config.name,
            "provider": str(provider),
            "model_id": model_id,
            "status": "registered",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register cloud model: {str(e)}",
        )
