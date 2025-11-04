"""FastAPI routes for cloud model management."""

from typing import List, Optional

from fastapi import Query
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from invokeai.app.api.dependencies import ApiDependencies
from invokeai.app.services.cloud_models import (
    APIKeyNotFoundException,
    CloudModelAlreadyExistsException,
    CloudModelNotFoundException,
    CloudModelRegistrationRequest,
    CloudModelService,
    InvalidCloudProviderException,
)
from invokeai.backend.model_manager.configs.cloud_models import (
    GeminiFlashImageConfig,
    ImagenUltraConfig,
    OpenAIImageConfig,
)
from invokeai.backend.model_manager.taxonomy import CloudProviderType

cloud_models_router = APIRouter(prefix="/v1/models/cloud", tags=["cloud_models"])


CloudModelConfigResponse = GeminiFlashImageConfig | ImagenUltraConfig | OpenAIImageConfig


class CloudModelsList(BaseModel):
    """List of cloud model configs."""

    models: List[CloudModelConfigResponse] = Field(description="List of cloud model configurations")


class CloudModelRegistrationResponse(BaseModel):
    """Response after registering a cloud model."""

    key: str = Field(description="Unique key for the registered model")
    name: str = Field(description="Model name")
    provider: CloudProviderType = Field(description="Cloud provider")
    message: str = Field(description="Success message")


class CloudModelDeleteResponse(BaseModel):
    """Response after deleting a cloud model."""

    key: str = Field(description="Key of the deleted model")
    message: str = Field(description="Success message")


class APIKeyValidationResponse(BaseModel):
    """Response from API key validation."""

    provider: CloudProviderType = Field(description="Cloud provider")
    valid: bool = Field(description="Whether API key is valid")
    message: str = Field(description="Validation message")


def get_cloud_model_service() -> CloudModelService:
    """Get the cloud model service from API dependencies."""
    model_record_service = ApiDependencies.invoker.services.model_manager.store
    return CloudModelService(model_record_service)


@cloud_models_router.post(
    "/",
    operation_id="register_cloud_model",
    response_model=CloudModelRegistrationResponse,
    status_code=201,
)
async def register_cloud_model(
    request: CloudModelRegistrationRequest,
) -> CloudModelRegistrationResponse:
    """
    Register a new cloud model.

    Registers a cloud-based image generation model (Google Gemini, Imagen, or OpenAI DALL-E)
    for use in InvokeAI workflows.

    Args:
        request: Registration request with provider and model details

    Returns:
        Registration response with model key

    Raises:
        400: If the model already exists or provider is invalid
        404: If API key is not configured for the provider
    """
    service = get_cloud_model_service()

    try:
        config = service.register_model(request)
        return CloudModelRegistrationResponse(
            key=config.key,
            name=config.name,
            provider=request.provider,
            message=f"Successfully registered {request.provider.value} model '{config.name}'",
        )
    except CloudModelAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidCloudProviderException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except APIKeyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@cloud_models_router.get(
    "/",
    operation_id="list_cloud_models",
    response_model=CloudModelsList,
)
async def list_cloud_models(
    provider: Optional[CloudProviderType] = Query(
        default=None, description="Filter by cloud provider"
    ),
) -> CloudModelsList:
    """
    List all registered cloud models.

    Returns a list of all cloud models, optionally filtered by provider.

    Args:
        provider: Optional provider filter (google-gemini, google-imagen, or openai)

    Returns:
        List of cloud model configurations
    """
    service = get_cloud_model_service()
    models = service.list_models(provider=provider)
    return CloudModelsList(models=models)


@cloud_models_router.get(
    "/{key}",
    operation_id="get_cloud_model",
    response_model=CloudModelConfigResponse,
)
async def get_cloud_model(key: str) -> CloudModelConfigResponse:
    """
    Get a cloud model by key.

    Args:
        key: Model key

    Returns:
        Cloud model configuration

    Raises:
        404: If the model is not found
    """
    service = get_cloud_model_service()

    try:
        return service.get_model(key)
    except CloudModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@cloud_models_router.delete(
    "/{key}",
    operation_id="delete_cloud_model",
    response_model=CloudModelDeleteResponse,
)
async def delete_cloud_model(key: str) -> CloudModelDeleteResponse:
    """
    Delete a cloud model.

    Removes a cloud model registration from InvokeAI.

    Args:
        key: Model key

    Returns:
        Deletion confirmation

    Raises:
        404: If the model is not found
    """
    service = get_cloud_model_service()

    try:
        service.delete_model(key)
        return CloudModelDeleteResponse(
            key=key,
            message=f"Successfully deleted cloud model with key '{key}'",
        )
    except CloudModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@cloud_models_router.get(
    "/validate/{provider}",
    operation_id="validate_api_key",
    response_model=APIKeyValidationResponse,
)
async def validate_api_key(provider: CloudProviderType) -> APIKeyValidationResponse:
    """
    Validate API key for a cloud provider.

    Checks if an API key is configured for the specified provider.

    Args:
        provider: Cloud provider to validate (google-gemini, google-imagen, or openai)

    Returns:
        Validation result

    Raises:
        404: If API key is not configured
    """
    service = get_cloud_model_service()

    try:
        service.validate_api_key(provider)
        return APIKeyValidationResponse(
            provider=provider,
            valid=True,
            message=f"API key configured for {provider.value}",
        )
    except APIKeyNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
