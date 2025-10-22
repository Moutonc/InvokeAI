"""Google Imagen 4 Ultra text-to-image invocation."""

import asyncio
from io import BytesIO
from typing import Literal, Optional

from PIL import Image

from invokeai.app.invocations.baseinvocation import BaseInvocation, invocation, InvocationContext
from invokeai.app.invocations.fields import ImageField, InputField, OutputField
from invokeai.app.invocations.model import ModelIdentifierField
from invokeai.app.invocations.primitives import ImageOutput
from invokeai.app.services.cloud_providers.provider_base import CloudGenerationRequest
from invokeai.app.services.images.images_common import ImageCategory


@invocation(
    "imagen_text_to_image",
    title="Imagen 4 Ultra - Text to Image",
    tags=["image", "cloud", "imagen", "google", "text2img"],
    category="image",
    version="1.0.0",
)
class ImagenTextToImageInvocation(BaseInvocation):
    """Generate images using Google Imagen 4 Ultra.

    Google Imagen 4 Ultra is a premium cloud-based image generation model offering:
    - High alignment with text prompts
    - Up to 2K resolution (2048×2048)
    - Batch generation (1-4 images per request)
    - SynthID watermark for image authenticity
    - LLM-based prompt enhancement
    - Configurable safety filters

    Official Documentation: https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview
    Pricing: $0.06 per image
    """

    # Model selection
    model: ModelIdentifierField = InputField(
        description="Imagen 4 Ultra model to use",
    )

    # Core parameters (exact API spec)
    prompt: str = InputField(
        description="Text description of the image to generate (up to 480 tokens)",
    )

    width: int = InputField(
        default=1024,
        ge=256,
        le=2048,
        multiple_of=64,
        description="Image width in pixels (will be adjusted to nearest supported aspect ratio)",
    )

    height: int = InputField(
        default=1024,
        ge=256,
        le=2048,
        multiple_of=64,
        description="Image height in pixels (will be adjusted to nearest supported aspect ratio)",
    )

    seed: Optional[int] = InputField(
        default=None,
        description="Random seed for deterministic generation (optional)",
    )

    # Batch generation (Imagen-specific)
    num_images: int = InputField(
        default=1,
        ge=1,
        le=4,
        description="Number of images to generate (1-4)",
    )

    # Aspect ratio helper (Imagen supports 5 ratios)
    aspect_ratio: Optional[Literal["1:1", "3:4", "4:3", "9:16", "16:9"]] = InputField(
        default=None,
        description="Preset aspect ratio (overrides width/height if set)",
    )

    # Imagen-specific features
    safety_setting: Literal["block_low_and_above", "block_medium_and_above", "block_only_high"] = InputField(
        default="block_medium_and_above",
        description="Safety filter level - controls content filtering",
    )

    enhance_prompt: bool = InputField(
        default=True,
        description="Enable LLM-based prompt enhancement for better quality",
    )

    add_watermark: bool = InputField(
        default=True,
        description="Add SynthID watermark (recommended for authenticity)",
    )

    def invoke(self, context: InvocationContext) -> ImageOutput:
        """Execute Imagen image generation.

        Args:
            context: Invocation context with access to services

        Returns:
            ImageOutput with the first generated image

        Note:
            If num_images > 1, additional images are saved as intermediate outputs.
            Only the first image is returned as the primary output.
        """
        # Apply aspect ratio preset if specified
        if self.aspect_ratio:
            # Official aspect ratio dimensions from Imagen API spec
            dimensions = {
                "1:1": (1024, 1024),
                "3:4": (768, 1024),
                "4:3": (1024, 768),
                "9:16": (576, 1024),
                "16:9": (1024, 576),
            }
            width, height = dimensions[self.aspect_ratio]
        else:
            width, height = self.width, self.height

        # Load cloud model (gets CloudModelWrapper with Imagen provider)
        loaded_model = context.models.load(self.model)

        with loaded_model as cloud_model:
            # Update provider-specific settings
            cloud_model.provider.safety_setting = self.safety_setting
            cloud_model.provider.enhance_prompt = self.enhance_prompt
            cloud_model.provider.add_watermark = self.add_watermark

            # Build request
            request = CloudGenerationRequest(
                prompt=self.prompt, width=width, height=height, seed=self.seed, num_images=self.num_images
            )

            # Emit progress event (cloud generation is single-step)
            context.util.events.emit_generator_progress(
                graph_execution_state_id=context.graph_execution_state_id,
                node_id=self.id,
                source_node_id=self.id,
                step=0,
                total_steps=1,
                order=0,
                progress_image=None,
            )

            # Call cloud API (async to sync conversion)
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(cloud_model.generate(request))
            finally:
                loop.close()

            # Process all generated images
            image_dtos = []
            for i, image_bytes in enumerate(response.images):
                # Convert bytes to PIL Image
                pil_image = Image.open(BytesIO(image_bytes))

                # Determine if this is the primary image or intermediate
                is_primary = i == 0
                is_intermediate = self.is_intermediate or (not is_primary)

                # Save to InvokeAI image storage
                image_dto = context.images.create(
                    image=pil_image,
                    image_category=ImageCategory.GENERAL,
                    node_id=self.id,
                    session_id=context.graph_execution_state_id,
                    is_intermediate=is_intermediate,
                    metadata={
                        "prompt": self.prompt,
                        "model": "imagen-4.0-ultra-generate-001",
                        "provider": "google-imagen",
                        "width": width,
                        "height": height,
                        "seed": self.seed,
                        "aspect_ratio": self.aspect_ratio,
                        "safety_setting": self.safety_setting,
                        "prompt_enhanced": self.enhance_prompt,
                        "synthid_watermark": self.add_watermark,
                        "image_index": i,
                        "total_images": len(response.images),
                        **response.metadata,
                    },
                )

                image_dtos.append(image_dto)

            # Return the first image as primary output
            # Additional images are saved as intermediates and can be accessed via metadata
            return ImageOutput.build(image_dto=image_dtos[0])
