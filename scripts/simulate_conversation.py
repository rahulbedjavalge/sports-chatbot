#!/usr/bin/env python3
"""Simulate a short conversation with the chatbot using Flask test client.
No network required. Prints each user message and assistant reply.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from backend import app as backend_module

app = backend_module.app

conversation = [
    "Who scored in Alpha FC vs Beta United?",  # Should use structured DB response
    "score Alpha FC vs Beta United",           # Should use structured DB response  
    "What stadium Alpha FC vs Beta United?",   # Should use structured DB response
    "Hello, how are you today?",               # Should fall back to LLM
    "Tell me about football in general",       # Should fall back to LLM
]

def run():
    print("Simulating conversation:\n")
    with app.test_client() as c:
        history = []
        for msg in conversation:
            payload = {"message": msg, "history": history}
            r = c.post('/chat', json=payload)
            try:
                data = r.get_json()
            except Exception:
                data = {'raw': r.data.decode('utf-8')}
            print(f"USER: {msg}")
            print(f"BOT : {data.get('answer')}")
            print(f"(intent: {data.get('intent')}, confidence: {data.get('confidence')})\n")
            # update history for LLM fallback simulation
            history.append({"role":"user","content": msg})
            history.append({"role":"assistant","content": data.get('answer') or ''})

if __name__ == '__main__':
    run()
