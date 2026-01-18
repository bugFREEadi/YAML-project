# models/openai_model.py
"""
OpenAI model implementation - REAL API CALLS with robust error handling.
"""

import os


# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def call_openai(prompt, temperature=0.7, max_tokens=500, system_message=None):
    """
    Call OpenAI API with the given prompt.
    
    Args:
        prompt: User prompt to send
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        system_message: Optional system message
    
    Returns:
        str: Generated text from OpenAI
    
    Raises:
        Exception: If API key is missing or API call fails
    """
    # Validate API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception(
            "OPENAI_API_KEY environment variable not set. "
            "Set it in your .env file or environment."
        )
    
    if not api_key.strip():
        raise Exception("OPENAI_API_KEY is empty")
    
    # Validate inputs
    if not prompt:
        raise Exception("Prompt cannot be empty")
    
    try:
        from openai import OpenAI
    except ImportError:
        raise Exception(
            "OpenAI package not installed. Run: pip install openai"
        )
    
    # Global lock to prevent parallel requests from hitting rate limit instantly
    from threading import Lock
    _request_lock = Lock()
    
    try:
        client = OpenAI(api_key=api_key, timeout=30)
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Retry logic for Rate Limits
        import time
        import random
        max_retries = 5
        retry_delay = 25  # Start with 25s for strict limits
        
        for attempt in range(max_retries + 1):
            try:
                # Add a small random delay before every request to de-sync threads
                time.sleep(random.uniform(0.5, 2.0))
                
                # Optional: Strict serialization if limits are very low
                # with _request_lock: 
                #     pass 
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                break # Success, exit loop
                
            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limit specifically
                if "rate_limit" in error_str or "429" in error_str:
                    if attempt < max_retries:
                        # Add jitter to the retry delay to prevent thundering herd
                        jitter = random.uniform(1, 10)
                        wait_time = retry_delay + jitter
                        
                        print(f"\033[93m⚠ OpenAI Rate Limit hit. Waiting {wait_time:.1f}s before retry ({attempt+1}/{max_retries})...\033[0m")
                        time.sleep(wait_time)
                        retry_delay *= 1.5  # Exponential backoff
                        continue
                raise e # Re-raise if not rate limit or retries exhausted
        
        # Validate response
        if not response.choices:
            raise Exception("No response choices returned from OpenAI")
        
        content = response.choices[0].message.content
        if content is None:
            raise Exception("OpenAI returned None content")
        
        return content
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise Exception(f"OpenAI authentication failed: {error_msg}")
        elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            raise Exception(f"OpenAI rate limit or quota exceeded ({max_retries} retries exhausted): {error_msg}")
        elif "timeout" in error_msg.lower():
            raise Exception(f"OpenAI API timeout (30s): {error_msg}")
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise Exception(f"Network error connecting to OpenAI: {error_msg}")
        else:
            raise Exception(f"OpenAI API error: {error_msg}")

