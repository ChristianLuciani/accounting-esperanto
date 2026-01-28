#!/usr/bin/env python3
"""
Kontablo AI Router - The Ultimate Free LLM Router

Routes requests to the best available free API based on:
- Task type (extraction, coding, research)
- Quota remaining
- Speed requirements
- Context length needs

Usage:
    from scripts.ai_router import router
    
    result = router.complete(
        prompt="Extract accounts from this text",
        task_type="extraction",
        priority="speed"  # or "quality", "cost"
    )
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Literal, Optional
import subprocess

# API clients (lazy loaded)
_clients = {}

def get_secret(key: str) -> Optional[str]:
    """Get secret from Infisical or environment."""
    try:
        result = subprocess.run(
            ['infisical', 'secrets', 'get', key, '--plain'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return os.getenv(key)

class APIProvider:
    """Base provider class."""
    
    def __init__(self, name: str, api_key_env: str):
        self.name = name
        self.api_key = get_secret(api_key_env)
        self.usage_file = Path(f'.cache/usage_{name.lower()}.json')
        self.usage_file.parent.mkdir(exist_ok=True)
    
    def get_usage(self) -> dict:
        """Load today's usage."""
        if not self.usage_file.exists():
            return {"date": str(datetime.now().date()), "requests": 0, "tokens": 0}
        
        with open(self.usage_file) as f:
            data = json.load(f)
        
        # Reset if different day
        if data.get("date") != str(datetime.now().date()):
            data = {"date": str(datetime.now().date()), "requests": 0, "tokens": 0}
            self.save_usage(data)
        
        return data
    
    def save_usage(self, usage: dict):
        """Save usage data."""
        with open(self.usage_file, 'w') as f:
            json.dump(usage, f, indent=2)
    
    def increment_usage(self, tokens: int):
        """Increment usage counters."""
        usage = self.get_usage()
        usage["requests"] += 1
        usage["tokens"] += tokens
        self.save_usage(usage)
    
    def quota_remaining(self) -> dict:
        """Check remaining quota."""
        raise NotImplementedError

class GroqProvider(APIProvider):
    """Groq - Ultra fast, 14.4K req/day."""
    
    DAILY_REQUESTS = 14400
    DAILY_TOKENS = 500000
    
    def __init__(self):
        super().__init__("Groq", "GROQ_API_KEY")
        self.models = {
            "fast": "llama-3.3-70b-versatile",
            "quality": "llama-3.1-70b-versatile",
            "small": "llama-3.1-8b-instant"
        }
    
    def quota_remaining(self) -> dict:
        usage = self.get_usage()
        return {
            "requests": self.DAILY_REQUESTS - usage["requests"],
            "tokens": self.DAILY_TOKENS - usage["tokens"],
            "percentage": ((self.DAILY_REQUESTS - usage["requests"]) / self.DAILY_REQUESTS) * 100
        }
    
    def complete(self, prompt: str, model_tier: str = "fast", max_tokens: int = 4000) -> dict:
        """Send request to Groq."""
        if not self.api_key:
            raise ValueError("Groq API key not set")
        
        # Check quota
        quota = self.quota_remaining()
        if quota["requests"] <= 0:
            raise Exception("Groq daily quota exceeded")
        
        # Use OpenAI-compatible SDK
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key
        )
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=self.models.get(model_tier, self.models["fast"]),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1
        )
        elapsed = time.time() - start_time
        
        result = {
            "provider": "Groq",
            "model": response.model,
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "latency": elapsed,
            "cost": 0  # Free
        }
        
        # Track usage
        self.increment_usage(response.usage.total_tokens)
        
        return result

class CerebrasProvider(APIProvider):
    """Cerebras - Fastest, 1M tokens/day."""
    
    DAILY_TOKENS = 1000000
    
    def __init__(self):
        super().__init__("Cerebras", "CEREBRAS_API_KEY")
        self.models = {
            "fast": "llama-4-scout",
            "quality": "llama-3.3-70b",
            "large": "qwen-3-235b-instruct"
        }
    
    def quota_remaining(self) -> dict:
        usage = self.get_usage()
        return {
            "tokens": self.DAILY_TOKENS - usage["tokens"],
            "percentage": ((self.DAILY_TOKENS - usage["tokens"]) / self.DAILY_TOKENS) * 100
        }
    
    def complete(self, prompt: str, model_tier: str = "fast", max_tokens: int = 8000) -> dict:
        """Send request to Cerebras."""
        if not self.api_key:
            raise ValueError("Cerebras API key not set")
        
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=self.api_key
        )
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=self.models.get(model_tier, self.models["fast"]),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1
        )
        elapsed = time.time() - start_time
        
        result = {
            "provider": "Cerebras",
            "model": response.model,
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "latency": elapsed,
            "cost": 0
        }
        
        self.increment_usage(response.usage.total_tokens)
        return result

class GeminiProvider(APIProvider):
    """Google Gemini - Multimodal, Gemini 2.5 Flash."""
    
    DAILY_REQUESTS = 1500
    
    def __init__(self):
        super().__init__("Gemini", "GOOGLE_AI_API_KEY")
        self.model = "gemini-2.5-flash"
    
    def quota_remaining(self) -> dict:
        usage = self.get_usage()
        return {
            "requests": self.DAILY_REQUESTS - usage["requests"],
            "percentage": ((self.DAILY_REQUESTS - usage["requests"]) / self.DAILY_REQUESTS) * 100
        }
    
    def complete(self, prompt: str, max_tokens: int = 8000) -> dict:
        """Send request to Gemini."""
        if not self.api_key:
            raise ValueError("Gemini API key not set")
        
        import warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        
        start_time = time.time()
        try:
            response = model.generate_content(prompt)
            elapsed = time.time() - start_time
            
            try:
                input_tokens = model.count_tokens(prompt).total_tokens
                output_tokens = model.count_tokens(response.text).total_tokens
                tokens_used = input_tokens + output_tokens
            except:
                tokens_used = len(prompt.split()) + len(response.text.split())
            
            result = {
                "provider": "Gemini",
                "model": self.model,
                "content": response.text,
                "tokens_used": tokens_used,
                "latency": elapsed,
                "cost": 0
            }
            
            self.increment_usage(result["tokens_used"])
            return result
        except Exception as e:
            raise ValueError(f"Gemini API error: {e}")

class OpenRouterProvider(APIProvider):
    """OpenRouter - Aggregator with 30+ free models."""
    
    def __init__(self):
        super().__init__("OpenRouter", "OPENROUTER_API_KEY")
        self.free_models = [
            "meta-llama/llama-3.1-70b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemma-2-9b-it:free"
        ]
    
    def complete(self, prompt: str, max_tokens: int = 4000) -> dict:
        """Send to OpenRouter (free models)."""
        if not self.api_key:
            raise ValueError("OpenRouter API key not set")
        
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=self.free_models[0],  # Default to Llama 70B
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        elapsed = time.time() - start_time
        
        return {
            "provider": "OpenRouter",
            "model": response.model,
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "latency": elapsed,
            "cost": 0
        }

class AIRouter:
    """Intelligent router that selects best provider."""
    
    def __init__(self):
        self.providers = {
            "groq": GroqProvider(),
            "cerebras": CerebrasProvider(),
            "gemini": GeminiProvider(),
            "openrouter": OpenRouterProvider()
        }
    
    def get_status(self) -> dict:
        """Get quota status for all providers."""
        status = {}
        for name, provider in self.providers.items():
            try:
                status[name] = provider.quota_remaining()
            except:
                status[name] = {"error": "Not available"}
        return status
    
    def select_provider(
        self,
        task_type: Literal["extraction", "coding", "research", "multimodal"],
        priority: Literal["speed", "quality", "volume"] = "speed"
    ) -> APIProvider:
        """Select best provider based on task and priority."""
        
        status = self.get_status()
        
        # Task-specific routing
        if task_type == "multimodal":
            if status["gemini"].get("percentage", 0) > 5:
                return self.providers["gemini"]
        
        if task_type == "extraction" and priority == "volume":
            # Use Cerebras for bulk work
            if status["cerebras"].get("percentage", 0) > 20:
                return self.providers["cerebras"]
        
        # Try providers in order of reliability/availability
        if priority == "speed":
            # Prefer Groq but fallback to Gemini
            if status["groq"].get("percentage", 0) > 10 and self.providers["groq"].api_key:
                return self.providers["groq"]
            if status["gemini"].get("percentage", 0) > 5 and self.providers["gemini"].api_key:
                return self.providers["gemini"]
        
        # Fallback chain - check which ones have API keys
        for provider_name in ["gemini", "cerebras", "groq", "openrouter"]:
            provider = self.providers[provider_name]
            provider_status = status.get(provider_name, {})
            if provider_status.get("percentage", 0) > 5 and provider.api_key:
                return provider
        
        raise Exception("All providers exhausted or no API keys configured")
    
    def complete(
        self,
        prompt: str,
        task_type: Literal["extraction", "coding", "research", "multimodal"] = "research",
        priority: Literal["speed", "quality", "volume"] = "speed",
        max_tokens: int = 4000
    ) -> dict:
        """Route and execute request."""
        
        provider = self.select_provider(task_type, priority)
        
        print(f"🎯 Routing to: {provider.name}")
        
        try:
            result = provider.complete(prompt, max_tokens=max_tokens)
            print(f"✅ Success: {result['tokens_used']} tokens in {result['latency']:.2f}s")
            return result
        except Exception as e:
            print(f"❌ {provider.name} failed: {e}")
            # Try fallback
            print("🔄 Trying fallback provider...")
            fallback = self.providers["openrouter"]
            return fallback.complete(prompt, max_tokens=max_tokens)

# Global router instance
router = AIRouter()

if __name__ == "__main__":
    import sys
    
    print("🧪 Testing AI Router")
    print("=" * 50)
    
    # Check status
    print("\n📊 Provider Status:")
    status = router.get_status()
    for provider, info in status.items():
        if "error" in info:
            print(f"  ❌ {provider}: {info['error']}")
        else:
            pct = info.get('percentage', 0)
            print(f"  ✅ {provider}: {pct:.0f}% quota remaining")
    
    # Test request if a prompt is provided
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "What are the main financial statement elements in IFRS?"
    
    print(f"\n🚀 Test Request:")
    print(f"Prompt: {prompt[:100]}...")
    
    try:
        result = router.complete(
            prompt=prompt,
            task_type="research",
            priority="speed",
            max_tokens=500
        )
        
        print(f"\n✅ Result:")
        print(f"  Provider: {result['provider']}")
        print(f"  Model: {result['model']}")
        print(f"  Response: {result['content'][:200]}...")
        print(f"  Tokens: {result['tokens_used']}")
        print(f"  Latency: {result['latency']:.2f}s")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

