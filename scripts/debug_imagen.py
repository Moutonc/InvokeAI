#!/usr/bin/env python3
"""Debug script for Imagen credentials."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import httpx
from google.auth import default
from google.auth.transport.requests import Request

async def main():
    print("=" * 80)
    print("Imagen Credentials Debug")
    print("=" * 80)
    print()

    # Load environment
    env_file = project_root / ".env"
    load_dotenv(env_file)

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print()

    # Try to get credentials
    print("Getting Google Cloud credentials...")
    try:
        credentials, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        print(f"✓ Got credentials")
        print(f"  Credentials type: {type(credentials).__name__}")
        print(f"  Project from credentials: {project}")
        print(f"  Valid: {credentials.valid}")
        print()
    except Exception as e:
        print(f"✗ Failed to get credentials: {e}")
        return

    # Refresh if needed
    if not credentials.valid:
        print("Refreshing credentials...")
        try:
            credentials.refresh(Request())
            print(f"✓ Refreshed credentials")
            print(f"  Valid: {credentials.valid}")
            print(f"  Token: {credentials.token[:20]}..." if credentials.token else "  Token: None")
            print()
        except Exception as e:
            print(f"✗ Failed to refresh: {e}")
            return
    else:
        print(f"Credentials already valid")
        print(f"  Token: {credentials.token[:20]}..." if credentials.token else "  Token: None")
        print()

    # Try to access Vertex AI API
    endpoint = (
        f"https://{region}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{region}/publishers/google/models"
    )

    print(f"Testing Vertex AI API access...")
    print(f"Endpoint: {endpoint}")
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                endpoint,
                headers={
                    "Authorization": f"Bearer {credentials.token}",
                },
            )

            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                print("✓ Successfully accessed Vertex AI API")
                data = response.json()
                models = data.get("models", [])
                print(f"  Found {len(models)} models")
                if models:
                    print("\nAvailable models:")
                    for model in models[:5]:  # Show first 5
                        model_name = model.get("name", "").split("/")[-1]
                        print(f"    - {model_name}")
            else:
                print(f"✗ Failed to access Vertex AI API")
                print(f"\nResponse headers:")
                for key, value in response.headers.items():
                    print(f"  {key}: {value}")
                print(f"\nResponse body:")
                try:
                    error_data = response.json()
                    import json
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text)

        except Exception as e:
            print(f"✗ Exception during API call: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
