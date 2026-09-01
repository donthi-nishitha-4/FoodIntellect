import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def query_llm_with_provider(messages, temperature=0.1, max_retries=2, timeout=15.0):
    """
    Query LLM with sequential fallback providers.
    Handles timeouts, retries, rate limits, and sequential failover across Google Gemini, Groq, and OpenRouter.
    """
    providers = [
        {
            "name": "google",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "models": ["gemini-3.6-flash"]
        },
        {
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
            "models": ["groq/compound", "groq/compound-mini", "qwen/qwen3.6-27b", "openai/gpt-oss-20b"]
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "models": [
                "liquid/lfm-2.5-2.6b:free",
                "nvidia/nemotron-3.5-lightning:free",
                "inclusionai/ling-3.0-flash-fin:free",
                "poolside/laguna-s-2.1:free",
                "minimax/minimax-m3:free"
            ]
        }
    ]
    
    for p in providers:
        if not p.get("api_key"):
            continue
            
        client = OpenAI(
            base_url=p["base_url"],
            api_key=p["api_key"],
            timeout=timeout
        )
        
        for model in p["models"]:
            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature
                    )
                    print(f"[INFO] Successfully used LLM provider: {p['name']} ({model})", flush=True)
                    return response.choices[0].message.content, f"{p['name']} ({model})"
                except Exception as e:
                    err_str = str(e)
                    print(f"[WARN] {p['name']} ({model}) attempt {attempt + 1} failed: {err_str[:120]}...", flush=True)
                    if "429" in err_str or "404" in err_str:
                        # Fail over immediately on rate limits, quota exhaustion, or 404s
                        break
                    time.sleep(0.5)
        
        print(f"[WARN] Provider {p['name']} exhausted. Failing over...", flush=True)
        
    return "[ERROR] All LLM providers unavailable", "none"

def query_llm(messages, temperature=0.1, max_retries=2, timeout=15.0):
    return query_llm_with_provider(messages, temperature, max_retries, timeout)

