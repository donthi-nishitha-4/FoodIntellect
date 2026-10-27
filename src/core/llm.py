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
            "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        },
        {
            "name": "groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY"),
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        },
        {
            "name": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "models": [
                "openai/gpt-4o-mini",
                "meta-llama/llama-3.1-8b-instruct",
                "google/gemini-2.0-flash-001",
                "qwen/qwen3-235b-a22b"
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


def failover_llm_call(prompt: str) -> str:
    """Helper wrapper taking a string prompt and returning string response via failover LLM."""
    messages = [{"role": "user", "content": prompt}]
    content, _ = query_llm(messages)
    return content


class LLMClient:
    """Thin wrapper exposing a ``.complete`` method for the FastAPI chat endpoint.

    It leverages the existing fail‑over LLM call logic (Google Gemini → Groq → OpenRouter).
    """

    def __init__(self, temperature: float = 0.1, max_retries: int = 2, timeout: float = 15.0):
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        """Return the LLM response for the given ``prompt``."""
        messages = [{"role": "user", "content": prompt}]
        response, _ = query_llm_with_provider(
            messages,
            temperature=self.temperature,
            max_retries=self.max_retries,
            timeout=self.timeout,
        )
        return response

