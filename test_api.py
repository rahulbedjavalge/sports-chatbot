# Test script for Vercel API
import requests
import json

def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test chat endpoint
    try:
        data = {"message": "What was the score of Alpha FC vs Beta United?"}
        response = requests.post(f"{base_url}/api/chat", json=data)
        print(f"\n✅ Chat test: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Chat test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Vercel API endpoints...")
    test_api()