# models/router.py
"""
Model router - YAML-driven model selection with robust error handling.
Provides graceful fallback and detailed error messages.
"""

import warnings
import os
warnings.filterwarnings("ignore")

from models.openai_model import call_openai
from models.gemini_model import call_gemini
from models.claude_model import call_claude


def call_model(model_name, prompt, temperature=0.7, max_tokens=500, system_message=None):
    """
    Route to the appropriate model based on YAML specification.
    
    Args:
        model_name: Model name from YAML (e.g., "openai", "gemini", "gpt", "claude")
        prompt: User prompt to send
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        system_message: Optional system message
    
    Returns:
        dict: {
            "text": str,
            "model": str,
            "provider": str
        }
    
    Raises:
        Exception: If model is unknown or API call fails
    """
    # Validate inputs
    if not model_name:
        raise Exception("Model name cannot be empty")
    
    if not prompt:
        raise Exception("Prompt cannot be empty")
    
    model_name_lower = str(model_name).lower()
    
    # OpenAI routing
    if any(x in model_name_lower for x in ["openai", "gpt"]):
        try:
            # Check API key before calling
            if not os.getenv("OPENAI_API_KEY"):
                raise Exception("OPENAI_API_KEY environment variable not set")
            
            text = call_openai(prompt, temperature, max_tokens, system_message)
            return {
                "text": text,
                "model": "gpt-4o-mini",
                "provider": "openai"
            }
        except Exception as e:
            # Try to provide helpful error message
            error_msg = str(e)
            if "api key" in error_msg.lower():
                raise Exception(f"OpenAI API key error: {error_msg}")
            elif "rate limit" in error_msg.lower():
                raise Exception(f"OpenAI rate limit exceeded: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise Exception(f"OpenAI API timeout: {error_msg}")
            else:
                raise Exception(f"OpenAI API error: {error_msg}")
    
    # Gemini routing
    elif any(x in model_name_lower for x in ["gemini", "google"]):
        try:
            # Check API key before calling
            if not os.getenv("GOOGLE_API_KEY"):
                raise Exception("GOOGLE_API_KEY environment variable not set")
            
            text = call_gemini(prompt, temperature, max_tokens, system_message)
            return {
                "text": text,
                "model": "gemini-1.5-flash",
                "provider": "google"
            }
        except Exception as e:
            error_msg = str(e)
            if "api key" in error_msg.lower():
                raise Exception(f"Gemini API key error: {error_msg}")
            elif "rate limit" in error_msg.lower():
                raise Exception(f"Gemini rate limit exceeded: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise Exception(f"Gemini API timeout: {error_msg}")
            else:
                raise Exception(f"Gemini API error: {error_msg}")
    
    # Claude/Anthropic routing
    elif any(x in model_name_lower for x in ["claude", "anthropic"]):
        try:
            # Check API key before calling
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise Exception("ANTHROPIC_API_KEY environment variable not set")
            
            text = call_claude(prompt, temperature, max_tokens, system_message)
            return {
                "text": text,
                "model": "claude-3-5-sonnet",
                "provider": "anthropic"
            }
        except Exception as e:
            error_msg = str(e)
            if "api key" in error_msg.lower():
                raise Exception(f"Claude API key error: {error_msg}")
            elif "rate limit" in error_msg.lower():
                raise Exception(f"Claude rate limit exceeded: {error_msg}")
            elif "timeout" in error_msg.lower():
                raise Exception(f"Claude API timeout: {error_msg}")
            else:
                raise Exception(f"Claude API error: {error_msg}")
    
    # Unknown model - provide helpful error
    else:
        available_models = ["openai/gpt", "gemini/google", "claude/anthropic"]
        raise Exception(
            f"Unknown model: '{model_name}'. "
            f"Supported models: {', '.join(available_models)}. "
            f"Check your YAML configuration."
        )

