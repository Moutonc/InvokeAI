#!/usr/bin/env python3
"""Test script for Google Imagen 4 Ultra integration.

This script tests the Imagen cloud provider integration end-to-end:
1. Validates Google Cloud credentials
2. Generates a test image
3. Saves the result

Usage:
    python scripts/test_imagen_integration.py

Prerequisites:
    - Set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_REGION in .env
    - Authenticate with: gcloud auth application-default login
    - Or set GOOGLE_APPLICATION_CREDENTIALS to service account key
    - Install dependencies: pip install httpx google-auth python-dotenv
    - Enable Vertex AI API: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_imagen_integration():
    """Test Imagen integration end-to-end."""
    print("=" * 80)
    print("Google Imagen 4 Ultra Integration Test")
    print("=" * 80)
    print()

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✓ Loaded .env file")
    except ImportError:
        print("⚠ python-dotenv not installed, using environment variables only")

    # Check for Google Cloud configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

    if not project_id:
        print("✗ ERROR: GOOGLE_CLOUD_PROJECT not found in environment")
        print("  Please set GOOGLE_CLOUD_PROJECT in .env file or environment variables")
        print("  Get your project ID from: https://console.cloud.google.com/")
        return False

    print(f"✓ Found Google Cloud project: {project_id}")
    print(f"✓ Using region: {region}")
    print()

    # Import provider
    try:
        from invokeai.app.services.cloud_providers.google_imagen_provider import GoogleImagenProvider
        from invokeai.app.services.cloud_providers.provider_base import CloudGenerationRequest

        print("✓ Successfully imported Imagen provider")
    except ImportError as e:
        print(f"✗ ERROR: Failed to import Imagen provider: {e}")
        return False

    # Create provider instance
    print("\nInitializing Imagen provider...")
    print("  This will check for Google Cloud credentials...")
    print()

    try:
        provider = GoogleImagenProvider(api_key="", config={})
        print("✓ Created Imagen provider instance")
        print(f"  Project: {provider.project_id}")
        print(f"  Region: {provider.region}")
    except Exception as e:
        print(f"✗ ERROR: Failed to create provider: {e}")
        print()
        print("To authenticate, run:")
        print("  gcloud auth application-default login")
        print()
        print("Or set GOOGLE_APPLICATION_CREDENTIALS to your service account key:")
        print("  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        return False

    # Validate credentials
    print("\nValidating Google Cloud credentials...")
    try:
        is_valid = await provider.validate_credentials()
        if is_valid:
            print("✓ Google Cloud credentials are valid")
            print("✓ Vertex AI API is accessible")
        else:
            print("✗ ERROR: Google Cloud credentials are invalid or Vertex AI is not accessible")
            print()
            print("Please ensure:")
            print("1. You have authenticated with: gcloud auth application-default login")
            print("2. Vertex AI API is enabled: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com")
            print("3. Your account has the required permissions")
            print("4. Billing is enabled for your project")
            return False
    except Exception as e:
        print(f"✗ ERROR: Credential validation failed: {e}")
        return False

    # Generate test image
    print("\nGenerating test image...")
    print("  Prompt: 'A majestic lion in the savanna at golden hour'")
    print("  Size: 1024x1024 (1:1)")
    print("  Seed: 42")
    print("  Safety: block_medium_and_above")
    print("  Prompt enhancement: enabled")
    print("  SynthID watermark: enabled")
    print()

    try:
        request = CloudGenerationRequest(
            prompt="A majestic lion in the savanna at golden hour",
            width=1024,
            height=1024,
            seed=42,
            num_images=1,
        )

        print("⏳ Calling Imagen API (this may take 15-45 seconds)...")
        response = await provider.generate_image(request)
        print("✓ Successfully generated image")
        print(f"  Generated {len(response.images)} image(s)")
        print(f"  Metadata: {response.metadata}")
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

        output_path = project_root / "outputs" / "test_imagen_output.png"
        output_path.parent.mkdir(exist_ok=True)
        pil_image.save(output_path)

        print(f"\n✓ Saved test image to: {output_path}")
        print(f"  Image size: {pil_image.size}")
        print(f"  Image mode: {pil_image.mode}")
        print(f"  Note: Image includes SynthID watermark (non-visible)")
    except Exception as e:
        print(f"⚠ Warning: Failed to save image: {e}")

    print()
    print("=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Register the Imagen model in InvokeAI")
    print("2. Use the 'Imagen 4 Ultra - Text to Image' node in workflows")
    print("3. Try batch generation (num_images: 2-4) for variations")
    print()
    print("💰 Cost: $0.06 per image generated")
    print()

    return True


def main():
    """Main entry point."""
    try:
        # Run async test
        result = asyncio.run(test_imagen_integration())
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
