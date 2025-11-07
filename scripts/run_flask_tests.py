#!/usr/bin/env python3
"""Run quick internal tests using Flask test client (no network required).

This imports the app object from backend.app and calls endpoints directly.
"""
import os
import json
import sys

# ensure we can import backend as a package (repo root should be in sys.path)
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from backend import app as backend_module

app = backend_module.app

def run():
    print("Running Flask internal tests...")
    with app.test_client() as c:
        r = c.get('/health')
        print('/health ->', r.status_code, r.get_json())

        # Test legacy structured /ask endpoint with known teams
        payload = {"message": "Who scored in Alpha FC vs Beta United?"}
        r = c.post('/ask', json=payload)
        print('/ask ->', r.status_code, r.get_json())

        # Test conversational /chat endpoint with same question
        payload = {"message": "Who scored in Alpha FC vs Beta United?", "history": []}
        r = c.post('/chat', json=payload)
        print('/chat ->', r.status_code, r.get_json())

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print('ERROR during tests:', e)
        raise
