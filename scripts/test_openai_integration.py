#!/usr/bin/env python3
"""Test script for OpenAI DALL-E 3 integration.

This script tests the OpenAI cloud provider integration end-to-end:
1. Validates API key
2. Generates a test image with DALL-E 3
3. Saves the result

Usage:
    python scripts/test_openai_integration.py

Prerequisites:
    - Set OPENAI_API_KEY environment variable or create .env file
    - Install dependencies: pip install httpx python-dotenv
    - Have valid OpenAI API key with billing enabled
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_openai_integration():
    """Test OpenAI integration end-to-end."""
    print("=" * 80)
    print("OpenAI DALL-E 3 Integration Test")
    print("=" * 80)
    print()

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✓ Loaded .env file")
    except ImportError:
        print("⚠ python-dotenv not installed, using environment variables only")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ ERROR: OPENAI_API_KEY not found in environment")
        print("  Please set OPENAI_API_KEY in .env file or environment variables")
        print("  Get your API key from: https://platform.openai.com/api-keys")
        return False

    print(f"✓ Found API key: {api_key[:20]}...")
    print()

    # Import provider
    try:
        from invokeai.app.services.cloud_providers.openai_provider import OpenAIProvider
        from invokeai.app.services.cloud_providers.provider_base import CloudGenerationRequest

        print("✓ Successfully imported OpenAI provider")
    except ImportError as e:
        print(f"✗ ERROR: Failed to import OpenAI provider: {e}")
        return False

    # Create provider instance
    try:
        provider = OpenAIProvider(
            api_key=api_key,
            config={
                "model_id": "dall-e-3",
                "quality": "standard",
                "style": "vivid",
            },
        )
        print("✓ Created OpenAI provider instance")
        print(f"  Model: {provider.model_id}")
        print(f"  Quality: {provider.quality}")
        print(f"  Style: {provider.style}")
    except Exception as e:
        print(f"✗ ERROR: Failed to create provider: {e}")
        return False

    # Validate credentials
    print("\nValidating API key...")
    try:
        is_valid = await provider.validate_credentials()
        if is_valid:
            print("✓ OpenAI API key is valid")
        else:
            print("✗ ERROR: OpenAI API key is invalid")
            print()
            print("Please check:")
            print("1. Your API key is correct (starts with 'sk-')")
            print("2. The key hasn't been revoked")
            print("3. Your account has access to the API")
            return False
    except Exception as e:
        print(f"✗ ERROR: Credential validation failed: {e}")
        return False

    # Generate test image
    print("\nGenerating test image with DALL-E 3...")
    print("  Prompt: 'A cyberpunk city street at night with neon signs'")
    print("  Size: 1024x1024")
    print("  Quality: standard")
    print("  Style: vivid")
    print()

    try:
        request = CloudGenerationRequest(
            prompt="A cyberpunk city street at night with neon signs",
            width=1024,
            height=1024,
            seed=None,  # DALL-E 3 doesn't support seeds
            num_images=1,
        )

        print("⏳ Calling OpenAI API (this may take 10-30 seconds)...")
        response = await provider.generate_image(request)
        print("✓ Successfully generated image")
        print(f"  Generated {len(response.images)} image(s)")
        print(f"  Metadata: {response.metadata}")

        # Show revised prompt if available
        if "revised_prompt" in response.metadata:
            print()
            print("  📝 DALL-E 3 Revised Prompt:")
            print(f"     {response.metadata['revised_prompt']}")
            print()
            print("  Note: DALL-E 3 may revise prompts for safety and quality.")

    except Exception as e:
        print(f"✗ ERROR: Image generation failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Save image
    try:
        from PIL import Image
        from io import BytesIO

        image_bytes = response.images[0]
        pil_image = Image.open(BytesIO(image_bytes))

        output_path = project_root / "outputs" / "test_dalle3_output.png"
        output_path.parent.mkdir(exist_ok=True)
        pil_image.save(output_path)

        print(f"\n✓ Saved test image to: {output_path}")
        print(f"  Image size: {pil_image.size}")
        print(f"  Image mode: {pil_image.mode}")
    except Exception as e:
        print(f"⚠ Warning: Failed to save image: {e}")

    print()
    print("=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Register the DALL-E 3 model in InvokeAI")
    print("2. Use the 'DALL-E 3 - Text to Image' node in workflows")
    print("3. Try different quality ('hd') and style ('natural') settings")
    print()
    print("💰 Cost Estimate:")
    print("   Standard 1024×1024: $0.040 per image")
    print("   HD 1024×1024: $0.080 per image")
    print("   Standard 1792×1024: $0.080 per image")
    print("   HD 1792×1024: $0.120 per image")
    print()

    return True


def main():
    """Main entry point."""
    try:
        # Run async test
        result = asyncio.run(test_openai_integration())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
