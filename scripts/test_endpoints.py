#!/usr/bin/env python3
import time
import requests

HEALTH = "http://127.0.0.1:5000/health"
LLM_TEST = "http://127.0.0.1:5000/llm_test"
CHAT = "http://127.0.0.1:5000/chat"

def wait_for(url, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            return r
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"{url} not reachable after {timeout}s")

if __name__ == '__main__':
    print("Checking health...")
    try:
        r = wait_for(HEALTH, timeout=10)
        print("Health OK:", r.text)
    except Exception as e:
        print("Health failed:", e)
        raise SystemExit(1)

    print("Checking LLM test (may fail if OPENROUTER_API_KEY not set)...")
    try:
        r = requests.get(LLM_TEST, timeout=10)
        print("LLM test response:", r.text)
    except Exception as e:
        print("LLM test failed:", e)

    print("Testing chat endpoint with demo question...")
    try:
        payload = {"message": "Who scored in Alpha FC vs Beta United?", "history": []}
        r = requests.post(CHAT, json=payload, timeout=10)
        print("Chat response:", r.text)
    except Exception as e:
        print("Chat request failed:", e)
