"""
Simple script to test backend connectivity.

Run this to verify the backend is running and accessible.
Usage: python test_backend.py
"""

import requests
from config.settings import API_HEALTH_URL, API_BASE_URL

def test_health_endpoint():
    """Test the health endpoint."""
    print(f"Testing health endpoint: {API_HEALTH_URL}")
    try:
        response = requests.get(API_HEALTH_URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed!")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print(f"✗ Health check failed with status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("✗ Cannot connect to backend. Is it running on http://localhost:8000?")
        print("  Start it with: python main.py")
        return False
    except requests.Timeout:
        print("✗ Health check timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print(f"\nTesting root endpoint: http://localhost:8000/")
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint accessible!")
            print(f"  Message: {data.get('message')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Docs: http://localhost:8000{data.get('docs')}")
            return True
        else:
            print(f"✗ Root endpoint failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Connectivity Test")
    print("=" * 60)

    health_ok = test_health_endpoint()
    root_ok = test_root_endpoint()

    print("\n" + "=" * 60)
    if health_ok and root_ok:
        print("✓ All tests passed! Backend is running correctly.")
        print("\nYou can now start the Streamlit frontend:")
        print("  streamlit run app.py")
    else:
        print("✗ Some tests failed. Please start the backend:")
        print("  cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent")
        print("  python main.py")
    print("=" * 60)
