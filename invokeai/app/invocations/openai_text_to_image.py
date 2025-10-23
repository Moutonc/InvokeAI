"""OpenAI DALL-E 3 / GPT Image 1 text-to-image invocation."""

import asyncio
from io import BytesIO
from typing import Literal, Optional

from PIL import Image

from invokeai.app.invocations.baseinvocation import BaseInvocation, invocation, InvocationContext
from invokeai.app.invocations.fields import ImageField, InputField, OutputField
from invokeai.app.invocations.model import ModelIdentifierField
from invokeai.app.invocations.primitives import ImageOutput
from invokeai.app.services.cloud_providers.provider_base import CloudGenerationRequest
from invokeai.app.services.image_records.image_records_common import ImageCategory


@invocation(
    "openai_text_to_image",
    title="DALL-E 3 - Text to Image",
    tags=["image", "cloud", "openai", "dalle", "text2img"],
    category="image",
    version="1.0.0",
)
class OpenAITextToImageInvocation(BaseInvocation):
    """Generate images using OpenAI DALL-E 3 / GPT Image 1.

    DALL-E 3 is OpenAI's latest image generation model offering:
    - Superior prompt following and image quality
    - HD quality option for detailed images
    - Style control (vivid or natural)
    - Revised prompt feature (GPT-4 enhanced prompts)
    - Three size options: 1024×1024, 1792×1024, 1024×1792

    Official Documentation: https://platform.openai.com/docs/guides/images
    Pricing:
    - Standard 1024×1024: $0.040 per image
    - Standard 1792×1024 or 1024×1792: $0.080 per image
    - HD 1024×1024: $0.080 per image
    - HD 1792×1024 or 1024×1792: $0.120 per image
    """

    # Model selection
    model: ModelIdentifierField = InputField(
        description="OpenAI model to use (DALL-E 3, DALL-E 2, or GPT Image 1)",
    )

    # Core parameters (exact API spec)
    prompt: str = InputField(
        description="Text description of the image to generate (up to 4000 characters)",
    )

    # Size selection (DALL-E 3 specific sizes)
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = InputField(
        default="1024x1024",
        description="Image size - different sizes have different pricing",
    )

    # DALL-E 3 specific features
    quality: Literal["standard", "hd"] = InputField(
        default="standard",
        description="Image quality - 'hd' creates more detailed images (higher cost)",
    )

    style: Literal["vivid", "natural"] = InputField(
        default="vivid",
        description="Image style - 'vivid' is hyper-real and dramatic, 'natural' is more subtle",
    )

    # Note: DALL-E 3 does not support seeds, negative prompts, or batch generation (n>1)
    # These limitations are per OpenAI's API specification

    def invoke(self, context: InvocationContext) -> ImageOutput:
        """Execute OpenAI image generation.

        Args:
            context: Invocation context with access to services

        Returns:
            ImageOutput with the generated image

        Note:
            DALL-E 3 generates one image at a time. The API may return a "revised_prompt"
            which is GPT-4's interpretation of your prompt, saved in metadata.
        """
        # Parse size string to width/height
        size_parts = self.size.split("x")
        width = int(size_parts[0])
        height = int(size_parts[1])

        # Load cloud model (gets CloudModelWrapper with OpenAI provider)
        loaded_model = context.models.load(self.model)

        with loaded_model as cloud_model:
            # Update provider-specific settings
            cloud_model.provider.quality = self.quality
            cloud_model.provider.style = self.style

            # Build request
            request = CloudGenerationRequest(
                prompt=self.prompt,
                width=width,
                height=height,
                seed=None,  # DALL-E 3 doesn't support seeds
                num_images=1,  # DALL-E 3 only generates one image at a time
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

            # Convert bytes to PIL Image
            image_bytes = response.images[0]
            pil_image = Image.open(BytesIO(image_bytes))

            # Build metadata
            metadata = {
                "prompt": self.prompt,
                "model": cloud_model.provider.model_id,
                "provider": "openai",
                "size": self.size,
                "quality": self.quality,
                "style": self.style,
                **response.metadata,
            }

            # Add revised prompt if available (DALL-E 3 feature)
            if "revised_prompt" in response.metadata:
                metadata["revised_prompt"] = response.metadata["revised_prompt"]
                metadata["note"] = (
                    "DALL-E 3 may revise prompts for safety and quality. "
                    "See 'revised_prompt' in metadata for the actual prompt used."
                )

            # Save to InvokeAI image storage
            image_dto = context.images.create(
                image=pil_image,
                image_category=ImageCategory.GENERAL,
                node_id=self.id,
                session_id=context.graph_execution_state_id,
                is_intermediate=self.is_intermediate,
                metadata=metadata,
            )

            # Return image output
            return ImageOutput.build(image_dto=image_dto)


@invocation(
    "dalle2_text_to_image",
    title="DALL-E 2 - Text to Image",
    tags=["image", "cloud", "openai", "dalle", "text2img"],
    category="image",
    version="1.0.0",
)
class DallE2TextToImageInvocation(BaseInvocation):
    """Generate images using OpenAI DALL-E 2.

    DALL-E 2 is OpenAI's previous generation model. It supports:
    - Batch generation (up to 10 images)
    - Three size options: 256×256, 512×512, 1024×1024
    - Lower cost than DALL-E 3

    Use DALL-E 2 when you need:
    - Multiple variations at once
    - Lower cost per image
    - Smaller image sizes

    Official Documentation: https://platform.openai.com/docs/guides/images
    Pricing:
    - 1024×1024: $0.020 per image
    - 512×512: $0.018 per image
    - 256×256: $0.016 per image
    """

    # Model selection
    model: ModelIdentifierField = InputField(
        description="OpenAI DALL-E 2 model",
    )

    # Core parameters
    prompt: str = InputField(
        description="Text description of the image to generate (up to 1000 characters)",
    )

    # DALL-E 2 size options
    size: Literal["256x256", "512x512", "1024x1024"] = InputField(
        default="1024x1024",
        description="Image size",
    )

    # Batch generation (DALL-E 2 feature)
    num_images: int = InputField(
        default=1,
        ge=1,
        le=10,
        description="Number of images to generate (1-10)",
    )

    def invoke(self, context: InvocationContext) -> ImageOutput:
        """Execute DALL-E 2 image generation.

        Args:
            context: Invocation context with access to services

        Returns:
            ImageOutput with the first generated image

        Note:
            If num_images > 1, additional images are saved as intermediate outputs.
        """
        # Parse size string to width/height
        size_parts = self.size.split("x")
        width = int(size_parts[0])
        height = int(size_parts[1])

        # Load cloud model
        loaded_model = context.models.load(self.model)

        with loaded_model as cloud_model:
            # Build request
            request = CloudGenerationRequest(
                prompt=self.prompt, width=width, height=height, seed=None, num_images=self.num_images
            )

            # Emit progress event
            context.util.events.emit_generator_progress(
                graph_execution_state_id=context.graph_execution_state_id,
                node_id=self.id,
                source_node_id=self.id,
                step=0,
                total_steps=1,
                order=0,
                progress_image=None,
            )

            # Call cloud API
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(cloud_model.generate(request))
            finally:
                loop.close()

            # Process all generated images
            image_dtos = []
            for i, image_bytes in enumerate(response.images):
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
                        "model": cloud_model.provider.model_id,
                        "provider": "openai",
                        "size": self.size,
                        "image_index": i,
                        "total_images": len(response.images),
                        **response.metadata,
                    },
                )

                image_dtos.append(image_dto)

            # Return the first image as primary output
            return ImageOutput.build(image_dto=image_dtos[0])
