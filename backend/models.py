# models.py
"""
Balanced LLM model router with graceful fallback.
Tries real APIs first, falls back to mock on rate limits or errors.
"""

import os
import time
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

from safety import safe_get

# API clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def call_mock(model_name, prompt):
    """Mock provider for testing and rate limit fallback - FAST VERSION."""
    time.sleep(0.3)  # Reduced from 1.5s to 0.3s for speed
    
    # Generate contextual mock response
    mock_text = f"""[MOCK RESPONSE from {model_name}]

**Action**: Processing request...

Here is the simulated output for the request. 
Since this is a mock mode (enabled due to API limits or verification testing), 
I am confirming that I received the context and am ready to proceed.

**Key Findings**:
1. Simulated Insight A: Data indicates strong growth potential.
2. Simulated Insight B: Technical feasibility is high.
3. Simulated Insight C: User adoption requires intuitive UI.

**Recommendation**:
Proceed with the proposed plan.
"""
    
    return mock_text, {
        "model": model_name,
        "provider": "mock",
        "latency": 0.3,
        "tokens": 64
    }


def call_openai(model_name, prompt, timeout=30):
    """Call OpenAI API with fallback to mock on error."""
    if not OPENAI_AVAILABLE:
        return call_mock(f"{model_name}-simulated", prompt)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return call_mock(f"{model_name}-simulated", prompt)
    
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        start = time.time()
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500  # Limit tokens for faster responses
        )
        
        latency = round(time.time() - start, 2)
        text = response.choices[0].message.content
        
        return text, {
            "model": model_name,
            "provider": "openai",
            "latency": latency,
            "tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0
        }
    
    except Exception as e:
        # Fallback to mock on any error (rate limits, network issues, etc.)
        return call_mock(f"{model_name}-simulated", prompt)


def call_anthropic(model_name, prompt, timeout=30):
    """Call Anthropic Claude API with fallback to mock on error."""
    if not ANTHROPIC_AVAILABLE:
        return call_mock(f"{model_name}-simulated", prompt)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return call_mock(f"{model_name}-simulated", prompt)
    
    try:
        client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        start = time.time()
        
        response = client.messages.create(
            model=model_name,
            max_tokens=500,  # Limit tokens for faster responses
            messages=[{"role": "user", "content": prompt}]
        )
        
        latency = round(time.time() - start, 2)
        text = response.content[0].text
        
        return text, {
            "model": model_name,
            "provider": "anthropic",
            "latency": latency,
            "tokens": response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else 0
        }
    
    except Exception as e:
        # Fallback to mock on any error
        return call_mock(f"{model_name}-simulated", prompt)


def call_gemini(model_name, prompt, timeout=30):
    """Call Google Gemini API with fallback to mock on error."""
    if not GEMINI_AVAILABLE:
        return call_mock(f"{model_name}-simulated", prompt)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return call_mock(f"{model_name}-simulated", prompt)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        start = time.time()
        response = model.generate_content(prompt)
        latency = round(time.time() - start, 2)
        
        text = response.text
        
        return text, {
            "model": model_name,
            "provider": "google",
            "latency": latency,
            "tokens": 0
        }
    
    except Exception as e:
        # Fallback to mock on any error
        return call_mock(f"{model_name}-simulated", prompt)


def resolve_model(model_spec, cfg):
    """Resolve model specification to actual model name and provider."""
    if not model_spec:
        model_spec = "gpt-4o-mini"
    
    model_spec = str(model_spec).lower()
    
    # OpenAI models
    if any(x in model_spec for x in ["gpt", "openai"]):
        if "gpt-4" in model_spec:
            return "gpt-4o-mini", "openai"
        elif "gpt-3.5" in model_spec:
            return "gpt-3.5-turbo", "openai"
        else:
            return "gpt-4o-mini", "openai"
    
    # Anthropic models
    elif any(x in model_spec for x in ["claude", "anthropic"]):
        if "opus" in model_spec:
            return "claude-3-opus-20240229", "anthropic"
        elif "sonnet" in model_spec:
            return "claude-3-5-sonnet-20241022", "anthropic"
        else:
            return "claude-3-5-sonnet-20241022", "anthropic"
    
    # Gemini models
    elif any(x in model_spec for x in ["gemini", "google"]):
        if "pro" in model_spec:
            return "gemini-1.5-pro", "google"
        else:
            return "gemini-1.5-flash", "google"
    
    # Default to OpenAI
    else:
        return "gpt-4o-mini", "openai"


def call_model(model_spec, prompt, role, cfg):
    """
    Main model calling function with graceful fallback.
    Tries real APIs first, falls back to mock on errors.
    
    Returns:
        {
            "text": str,
            "proof": dict,
            "error": dict | None
        }
    """
    model_name, provider = resolve_model(model_spec, cfg)
    
    # Call appropriate API (with automatic fallback to mock)
    if provider == "openai":
        text, proof = call_openai(model_name, prompt)
    elif provider == "anthropic":
        text, proof = call_anthropic(model_name, prompt)
    elif provider == "google":
        text, proof = call_gemini(model_name, prompt)
    else:
        text, proof = call_mock(model_name, prompt)
    
    # Add timestamp
    proof["timestamp"] = time.time()
    proof["fallback_used"] = proof.get("provider") == "mock"
    
    return {
        "text": text,
        "proof": proof,
        "error": None
    }
