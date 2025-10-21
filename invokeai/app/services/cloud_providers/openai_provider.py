"""OpenAI DALL-E 3 / GPT Image 1 provider implementation.

Official API Documentation:
https://platform.openai.com/docs/guides/images/introduction

API Specification:
- Models: dall-e-3, dall-e-2, gpt-image-1 (limited access)
- Endpoint: https://api.openai.com/v1/images/generations
- Authentication: API key via Authorization header (Bearer token)
- Pricing: DALL-E 3 - $0.04-$0.12 per image depending on quality/size
- Status: Generally Available (DALL-E 3), Limited Access (gpt-image-1)
"""

from typing import Dict, Literal, Optional, Tuple

import httpx

from .provider_base import CloudGenerationRequest, CloudGenerationResponse, CloudModelProviderBase


class OpenAIProvider(CloudModelProviderBase):
    """OpenAI DALL-E 3 / GPT Image 1 provider - 100% API-accurate implementation.

    OpenAI offers multiple image generation models:
    - DALL-E 3: Latest model with HD quality, style control, and better prompt following
    - DALL-E 2: Previous generation, supports batch generation
    - GPT Image 1: Newest model (limited access) with advanced capabilities

    This implementation follows the exact OpenAI API specification.
    """

    BASE_URL = "https://api.openai.com/v1"

    # Model specifications per OpenAI documentation
    MODEL_SPECS: Dict[str, Dict] = {
        "dall-e-3": {
            "sizes": ["1024x1024", "1792x1024", "1024x1792"],
            "max_images": 1,  # DALL-E 3 generates one image at a time
            "supports_quality": True,
            "supports_style": True,
            "supports_revised_prompt": True,
        },
        "dall-e-2": {
            "sizes": ["256x256", "512x512", "1024x1024"],
            "max_images": 10,  # DALL-E 2 can generate up to 10 images
            "supports_quality": False,
            "supports_style": False,
            "supports_revised_prompt": False,
        },
        "gpt-image-1": {
            "sizes": ["1024x1024", "1792x1024", "1024x1792", "2048x2048"],  # Estimated
            "max_images": 1,
            "supports_quality": True,
            "supports_style": True,
            "supports_revised_prompt": True,
        },
    }

    def __init__(self, api_key: str, config: dict):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (starts with sk-...)
            config: Provider configuration with optional settings:
                - model_id: Model to use (default: "dall-e-3")
                - quality: Image quality "standard" or "hd" (DALL-E 3 only)
                - style: Image style "vivid" or "natural" (DALL-E 3 only)
        """
        super().__init__(api_key, config)

        # Model selection
        self.model_id = config.get("model_id", "dall-e-3")

        # Validate model
        if self.model_id not in self.MODEL_SPECS:
            raise ValueError(
                f"Unknown model: {self.model_id}. "
                f"Supported models: {list(self.MODEL_SPECS.keys())}"
            )

        # DALL-E 3 specific settings
        self.quality = config.get("quality", "standard")  # "standard" or "hd"
        self.style = config.get("style", "vivid")  # "vivid" or "natural"

        # Get model specs
        self.specs = self.MODEL_SPECS[self.model_id]

    def _get_size_string(self, width: int, height: int) -> str:
        """Convert width/height to OpenAI size string.

        Args:
            width: Desired image width
            height: Desired image height

        Returns:
            Size string in format "WIDTHxHEIGHT" (e.g., "1024x1024")
        """
        size_str = f"{width}x{height}"
        supported_sizes = self.specs["sizes"]

        # Check if requested size is supported
        if size_str in supported_sizes:
            return size_str

        # Default to first supported size (usually 1024x1024)
        return supported_sizes[0]

    async def generate_image(self, request: CloudGenerationRequest) -> CloudGenerationResponse:
        """Generate image using OpenAI API.

        Implements the exact API specification from:
        https://platform.openai.com/docs/guides/images/introduction

        Args:
            request: CloudGenerationRequest with prompt and parameters

        Returns:
            CloudGenerationResponse with generated image(s)

        Raises:
            Exception: If API call fails with detailed error message
        """
        # Determine size
        size_str = self._get_size_string(request.width, request.height)

        # Build request payload per official OpenAI spec
        payload = {
            "model": self.model_id,
            "prompt": request.prompt,
            "n": min(request.num_images, self.specs["max_images"]),
            "size": size_str,
            "response_format": "url",  # Get URLs to download images
        }

        # Add DALL-E 3 specific parameters
        if self.specs["supports_quality"]:
            payload["quality"] = self.quality

        if self.specs["supports_style"]:
            payload["style"] = self.style

        # Make API call
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            # Handle API errors
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                error_type = error_data.get("error", {}).get("type", "unknown")
                error_code = error_data.get("error", {}).get("code", "unknown")

                # Provide helpful error messages for common issues
                if response.status_code == 401:
                    raise Exception(
                        f"OpenAI API authentication failed (HTTP 401): {error_message}\n\n"
                        "Please check:\n"
                        "1. OPENAI_API_KEY is set correctly in .env\n"
                        "2. Your API key is valid and not revoked\n"
                        "3. API key starts with 'sk-'\n\n"
                        "Get your API key from: https://platform.openai.com/api-keys"
                    )
                elif response.status_code == 429:
                    raise Exception(
                        f"OpenAI API rate limit exceeded (HTTP 429): {error_message}\n\n"
                        "You've hit your rate limit or quota. Please:\n"
                        "1. Wait a few minutes before retrying\n"
                        "2. Check your usage: https://platform.openai.com/usage\n"
                        "3. Upgrade your plan if needed"
                    )
                elif response.status_code == 400 and "billing" in error_message.lower():
                    raise Exception(
                        f"OpenAI API billing error (HTTP 400): {error_message}\n\n"
                        "Please ensure:\n"
                        "1. You have added payment method to your OpenAI account\n"
                        "2. Your payment method is valid\n"
                        "3. You have available credits\n\n"
                        "Manage billing: https://platform.openai.com/account/billing"
                    )
                elif error_code == "model_not_found":
                    raise Exception(
                        f"OpenAI model not found: {error_message}\n\n"
                        f"Model '{self.model_id}' may require special access.\n"
                        "For gpt-image-1, apply for access: https://openai.com/form/gpt-image-early-access"
                    )
                else:
                    raise Exception(
                        f"OpenAI API error (HTTP {response.status_code}): {error_message}\n"
                        f"Error type: {error_type}\n"
                        f"Error code: {error_code}\n"
                        f"Full response: {error_data}"
                    )

            data = response.json()

            # Extract image URLs from response
            # Response structure per API spec:
            # {
            #   "created": 1234567890,
            #   "data": [
            #     {
            #       "url": "https://...",
            #       "revised_prompt": "..." (DALL-E 3 only)
            #     }
            #   ]
            # }

            image_data_list = data.get("data", [])
            if not image_data_list:
                raise Exception(f"No images generated by OpenAI API. Response: {data}")

            # Download images from URLs
            images = []
            revised_prompts = []

            for img_data in image_data_list:
                img_url = img_data.get("url")
                if not img_url:
                    continue

                # Download image
                try:
                    img_response = await client.get(img_url, timeout=30.0)
                    img_response.raise_for_status()
                    images.append(img_response.content)
                except Exception as e:
                    raise Exception(f"Failed to download image from OpenAI URL: {e}")

                # Extract revised prompt (DALL-E 3 feature)
                if self.specs["supports_revised_prompt"]:
                    revised_prompt = img_data.get("revised_prompt")
                    if revised_prompt:
                        revised_prompts.append(revised_prompt)

            if not images:
                raise Exception(f"Failed to download any images. Response: {data}")

            # Build response
            metadata = {
                "model": self.model_id,
                "provider": "openai",
                "size": size_str,
                "num_images": len(images),
                "prompt": request.prompt,
                "created": data.get("created"),
            }

            # Add model-specific metadata
            if self.specs["supports_quality"]:
                metadata["quality"] = self.quality

            if self.specs["supports_style"]:
                metadata["style"] = self.style

            if revised_prompts:
                metadata["revised_prompts"] = revised_prompts
                metadata["revised_prompt"] = revised_prompts[0]  # First one for convenience

            return CloudGenerationResponse(
                images=images,
                metadata=metadata,
                provider_response=data,
            )

    async def validate_credentials(self) -> bool:
        """Validate OpenAI API key by checking models endpoint.

        Returns:
            True if API key is valid and working, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return response.status_code == 200
        except Exception:
            return False
