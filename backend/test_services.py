"""
Test script to verify service connections
Run this before starting the server to ensure API keys are configured correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Check if required environment variables are set"""
    print("=" * 60)
    print("Testing Environment Variables")
    print("=" * 60)

    required_vars = ['APIFY_API_TOKEN', 'GOOGLE_API_KEY']
    all_set = True

    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"✗ {var}: NOT SET")
            all_set = False

    print()
    return all_set


def test_apify_service():
    """Test Apify service connection"""
    print("=" * 60)
    print("Testing Apify Service")
    print("=" * 60)

    try:
        from apify_service import ApifyService

        service = ApifyService()
        print("✓ Apify service initialized")

        if service.test_connection():
            print("✓ Apify connection successful")
            return True
        else:
            print("✗ Apify connection failed")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    finally:
        print()


def test_gemini_service():
    """Test Gemini service connection"""
    print("=" * 60)
    print("Testing Gemini Service")
    print("=" * 60)

    try:
        from gemini_service import GeminiService

        service = GeminiService()
        print("✓ Gemini service initialized")

        if service.test_connection():
            print("✓ Gemini connection successful")
            return True
        else:
            print("✗ Gemini connection failed")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    finally:
        print()


def main():
    """Run all tests"""
    print("\nYouTube Channel RAG Backend - Service Tests\n")

    # Test environment variables
    env_ok = test_environment_variables()

    if not env_ok:
        print("❌ Environment variables not set correctly")
        print("Please create a .env file with APIFY_API_TOKEN and GOOGLE_API_KEY")
        sys.exit(1)

    # Test services
    apify_ok = test_apify_service()
    gemini_ok = test_gemini_service()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Environment Variables: {'✓ PASS' if env_ok else '✗ FAIL'}")
    print(f"Apify Service: {'✓ PASS' if apify_ok else '✗ FAIL'}")
    print(f"Gemini Service: {'✓ PASS' if gemini_ok else '✗ FAIL'}")
    print()

    if all([env_ok, apify_ok, gemini_ok]):
        print("✓ All tests passed! You can now start the server.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please fix the issues before starting the server.")
        sys.exit(1)


if __name__ == '__main__':
    main()
