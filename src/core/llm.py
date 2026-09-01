import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def query_llm_with_provider(messages, temperature=0.1, max_retries=2, timeout=15.0):
    """
    Query LLM with sequential fallback providers.
    Handles timeouts, retries, and sequential failover (Gemini -> Groq -> OpenRouter).
    """
    providers = [
        {
            "name": "google",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-3.6-flash"
        },
        {
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
            "model": "llama-3.3-70b-versatile"
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "google/gemini-2.5-flash-lite:free"
        }
    ]
    
    for p in providers:
        if not p.get("api_key"):
            continue
            
        for attempt in range(max_retries):
            try:
                client = OpenAI(
                    base_url=p["base_url"],
                    api_key=p["api_key"],
                    timeout=timeout
                )
                response = client.chat.completions.create(
                    model=p["model"],
                    messages=messages,
                    temperature=temperature
                )
                print(f"[INFO] Successfully used LLM provider: {p['name']}", flush=True)
                return response.choices[0].message.content, p["name"]
            except Exception as e:
                print(f"[WARN] {p['name']} attempt {attempt + 1} failed: {str(e)[:100]}...", flush=True)
                time.sleep(1)
        
        print(f"[WARN] Provider {p['name']} exhausted. Failing over...", flush=True)
        
    return "[ERROR] All LLM providers unavailable", "none"

def query_llm(messages, temperature=0.1, max_retries=2, timeout=15.0):
    return query_llm_with_provider(messages, temperature, max_retries, timeout)
