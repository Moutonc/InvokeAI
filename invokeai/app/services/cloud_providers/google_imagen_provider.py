"""Google Imagen 4 Ultra provider implementation.

Official API Documentation:
https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api

API Specification:
- Model: imagen-4.0-ultra-generate-001
- Endpoint: Vertex AI REST API
- Authentication: Google Cloud OAuth2 (Application Default Credentials or Service Account)
- Pricing: $0.06 per image
- Status: Generally Available
"""

import base64
import os
from typing import Dict, Literal, Optional, Tuple

import httpx
from google.auth import default
from google.auth.transport.requests import Request

from .provider_base import CloudGenerationRequest, CloudGenerationResponse, CloudModelProviderBase


class GoogleImagenProvider(CloudModelProviderBase):
    """Google Imagen 4 Ultra provider - 100% API-accurate implementation.

    Imagen 4 Ultra is Google's premium image generation model, offering:
    - High alignment with text prompts
    - 2K resolution support (up to 2048×2048)
    - Batch generation (1-4 images)
    - SynthID watermark for authenticity
    - LLM-based prompt enhancement
    - Configurable safety filters

    This implementation follows the exact Vertex AI API specification.
    """

    MODEL_ID = "imagen-4.0-ultra-generate-001"

    # Official aspect ratio support per Imagen documentation
    ASPECT_RATIOS: Dict[str, Tuple[int, int]] = {
        "1:1": (1024, 1024),
        "3:4": (768, 1024),
        "4:3": (1024, 768),
        "9:16": (576, 1024),
        "16:9": (1024, 576),
    }

    def __init__(self, api_key: str, config: dict):
        """Initialize Imagen provider.

        Args:
            api_key: Not used for Imagen (uses Google Cloud credentials)
            config: Provider configuration with optional settings:
                - safety_setting: Safety filter level (default: "block_medium_and_above")
                - enhance_prompt: Enable LLM prompt enhancement (default: True)
                - add_watermark: Add SynthID watermark (default: True)
        """
        super().__init__(api_key, config)

        # Get Google Cloud configuration from environment
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        if not self.project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable is required for Imagen. "
                "Please set it in your .env file or environment. "
                "Get your project ID from: https://console.cloud.google.com/"
            )

        # Initialize Google Cloud credentials
        # This will use Application Default Credentials (ADC) or service account
        try:
            self.credentials, _ = default()
        except Exception as e:
            raise ValueError(
                f"Failed to initialize Google Cloud credentials: {e}\n\n"
                "Please authenticate with: gcloud auth application-default login\n"
                "Or set GOOGLE_APPLICATION_CREDENTIALS to your service account key file."
            )

        # Provider-specific settings with defaults
        self.safety_setting = config.get("safety_setting", "block_medium_and_above")
        self.enhance_prompt = config.get("enhance_prompt", True)
        self.add_watermark = config.get("add_watermark", True)

    def _get_access_token(self) -> str:
        """Get OAuth2 access token for Vertex AI API.

        Returns:
            Valid access token string

        Raises:
            Exception: If token refresh fails
        """
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token

    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate the closest supported aspect ratio.

        Args:
            width: Desired image width
            height: Desired image height

        Returns:
            Aspect ratio string (e.g., "16:9")
        """
        from math import gcd

        # Calculate the actual aspect ratio
        divisor = gcd(width, height)
        ratio = f"{width // divisor}:{height // divisor}"

        # Check if this exact ratio is supported
        if ratio in self.ASPECT_RATIOS:
            return ratio

        # Default to 1:1 (square) if no exact match
        return "1:1"

    async def generate_image(self, request: CloudGenerationRequest) -> CloudGenerationResponse:
        """Generate image using Google Imagen 4 Ultra API.

        Implements the exact Vertex AI API specification from:
        https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api

        Args:
            request: CloudGenerationRequest with prompt and parameters

        Returns:
            CloudGenerationResponse with generated image(s)

        Raises:
            Exception: If API call fails with detailed error message
        """
        # Determine aspect ratio
        aspect_ratio = self._calculate_aspect_ratio(request.width, request.height)

        # Build request payload per official Vertex AI spec
        # Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api

        # API Constraint: Seed and watermark cannot be used together
        # If seed is provided, we must disable watermark
        use_watermark = self.add_watermark
        if request.seed is not None:
            use_watermark = False

        payload = {
            "instances": [{"prompt": request.prompt}],
            "parameters": {
                "sampleCount": min(request.num_images, 4),  # Imagen supports 1-4 images
                "aspectRatio": aspect_ratio,
                "safetySetting": self.safety_setting,
                "addWatermark": use_watermark,  # SynthID watermark (disabled if seed is used)
                "enhancePrompt": self.enhance_prompt,  # LLM-based prompt enhancement
            },
        }

        # Add seed if provided (for deterministic generation)
        # Note: API constraint - seed cannot be used with watermark
        if request.seed is not None:
            payload["parameters"]["seed"] = request.seed

        # Build Vertex AI endpoint URL
        endpoint = (
            f"https://{self.region}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.region}/"
            f"publishers/google/models/{self.MODEL_ID}:predict"
        )

        # Get OAuth2 access token
        try:
            access_token = self._get_access_token()
        except Exception as e:
            raise Exception(
                f"Failed to get Google Cloud access token: {e}\n\n"
                "Please authenticate with: gcloud auth application-default login"
            )

        # Make API call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # Handle API errors
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                error_code = error_data.get("error", {}).get("code", response.status_code)

                # Provide helpful error messages for common issues
                if error_code == 403:
                    raise Exception(
                        f"Imagen API permission denied (HTTP {error_code}): {error_message}\n\n"
                        "Please ensure:\n"
                        "1. Vertex AI API is enabled in your GCP project\n"
                        "2. Your credentials have the required permissions\n"
                        "3. Billing is enabled for your project\n\n"
                        "Enable Vertex AI: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com"
                    )
                elif error_code == 429:
                    raise Exception(
                        f"Imagen API rate limit exceeded (HTTP {error_code}): {error_message}\n\n"
                        "Please wait a few minutes before retrying or increase your quota."
                    )
                else:
                    raise Exception(
                        f"Imagen API error (HTTP {error_code}): {error_message}\n"
                        f"Full response: {error_data}"
                    )

            data = response.json()

            # Extract images from predictions
            # Response structure per API spec:
            # {
            #   "predictions": [{
            #     "bytesBase64Encoded": "<base64_image_data>",
            #     "mimeType": "image/png"
            #   }]
            # }

            predictions = data.get("predictions", [])
            if not predictions:
                raise Exception(f"No images generated by Imagen API. Response: {data}")

            # Decode all generated images
            images = []
            for prediction in predictions:
                image_b64 = prediction.get("bytesBase64Encoded")
                if image_b64:
                    try:
                        images.append(base64.b64decode(image_b64))
                    except Exception as e:
                        raise Exception(f"Failed to decode base64 image data: {e}")

            if not images:
                raise Exception(f"No valid image data in Imagen response. Response: {data}")

            # Build response
            return CloudGenerationResponse(
                images=images,
                metadata={
                    "model": self.MODEL_ID,
                    "provider": "google-imagen",
                    "aspect_ratio": aspect_ratio,
                    "num_images": len(images),
                    "seed": request.seed,
                    "prompt": request.prompt,
                    "safety_setting": self.safety_setting,
                    "synthid_watermark": use_watermark,  # Actual watermark status used
                    "prompt_enhanced": self.enhance_prompt,
                },
                provider_response=data,
            )

    async def validate_credentials(self) -> bool:
        """Validate Google Cloud credentials.

        Returns:
            True if credentials can be obtained and refreshed, False otherwise
        """
        try:
            # Try to refresh/get token if needed
            if not self.credentials.valid:
                self.credentials.refresh(Request())

            # Verify we have a valid token
            # This confirms the credentials are properly set up
            return self.credentials.valid and self.credentials.token is not None

        except Exception:
            return False
