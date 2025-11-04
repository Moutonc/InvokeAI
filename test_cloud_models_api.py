#!/usr/bin/env python3
"""
Manual test script for cloud model API endpoints.

Usage:
    python test_cloud_models_api.py

Prerequisites:
    - InvokeAI server running on localhost:9090
    - At least one API key configured (GOOGLE_API_KEY, GOOGLE_CLOUD_PROJECT, or OPENAI_API_KEY)
"""

import sys
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:9090/api/v1/models/cloud"

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_registration(name: str, provider: str, model_id: str, source: str) -> Optional[str]:
    """Test POST /api/v1/models/cloud - Register a model."""
    print_section(f"Test 1: Register Model ({provider})")

    data = {
        "name": name,
        "provider": provider,
        "cloud_model_id": model_id,
        "source": source,
        "description": "Test model created by test script"
    }

    try:
        response = requests.post(BASE_URL, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json().get("key")
        else:
            print(f"❌ Registration failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to InvokeAI server")
        print("   Make sure the server is running: python scripts/invokeai-web.py")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_list_models():
    """Test GET /api/v1/models/cloud - List all models."""
    print_section("Test 2: List All Models")

    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Found {len(models)} cloud models:")
            for model in models:
                print(f"  - {model.get('name')} ({model.get('provider')}) [key: {model.get('key')}]")
            print("✅ List successful!")
        else:
            print(f"❌ List failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_get_model(key: str):
    """Test GET /api/v1/models/cloud/{key} - Get specific model."""
    print_section("Test 3: Get Specific Model")

    try:
        response = requests.get(f"{BASE_URL}/{key}", timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            model = response.json()
            print(f"Model Details:")
            print(f"  Name: {model.get('name')}")
            print(f"  Provider: {model.get('provider')}")
            print(f"  Model ID: {model.get('cloud_model_id')}")
            print(f"  Description: {model.get('description')}")
            print("✅ Get successful!")
        else:
            print(f"❌ Get failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_validate_provider(provider: str):
    """Test GET /api/v1/models/cloud/validate/{provider} - Validate API key."""
    print_section(f"Test 4: Validate Provider ({provider})")

    try:
        response = requests.get(f"{BASE_URL}/validate/{provider}", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            result = response.json()
            if result.get("valid"):
                print("✅ API key is valid!")
            else:
                print(f"❌ API key is invalid: {result.get('message')}")
        else:
            print(f"❌ Validation failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_delete_model(key: str):
    """Test DELETE /api/v1/models/cloud/{key} - Delete model."""
    print_section("Test 5: Delete Model")

    response = input(f"Are you sure you want to delete model {key}? (y/N): ")
    if response.lower() != 'y':
        print("Skipping deletion test.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/{key}", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("✅ Deletion successful!")
        else:
            print(f"❌ Deletion failed: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Cloud Model API Test Script")
    print("="*60)
    print("\nThis script will test the Phase 4 cloud model API endpoints.")
    print("Make sure InvokeAI server is running on localhost:9090")
    print("\nWhich provider would you like to test?")
    print("  1. Google Gemini (requires GOOGLE_API_KEY)")
    print("  2. Google Imagen (requires GOOGLE_CLOUD_PROJECT)")
    print("  3. OpenAI (requires OPENAI_API_KEY)")
    print("  4. Skip to list existing models")

    choice = input("\nEnter choice (1-4): ").strip()

    model_key = None

    if choice == "1":
        model_key = test_registration(
            name="Test Gemini Model",
            provider="google-gemini",
            model_id="gemini-2.5-flash-image",
            source="https://ai.google.dev/"
        )
        test_validate_provider("google-gemini")
    elif choice == "2":
        model_key = test_registration(
            name="Test Imagen Model",
            provider="google-imagen",
            model_id="imagen-4.0-ultra-generate-001",
            source="https://cloud.google.com/vertex-ai/"
        )
        test_validate_provider("google-imagen")
    elif choice == "3":
        model_key = test_registration(
            name="Test DALL-E 3 Model",
            provider="openai",
            model_id="dall-e-3",
            source="https://platform.openai.com/docs/guides/images"
        )
        test_validate_provider("openai")

    # Always test list
    test_list_models()

    # If we successfully registered, test get and optionally delete
    if model_key:
        test_get_model(model_key)
        test_delete_model(model_key)

    print_section("Test Summary")
    print("All tests completed!")
    print("\nNext steps:")
    print("  1. Check the results above")
    print("  2. Test the frontend UI manually")
    print("  3. See PHASE4_TESTING_GUIDE.md for detailed testing instructions")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
