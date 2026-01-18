# models/claude_model.py
"""
Anthropic Claude model implementation - REAL API CALLS with robust error handling.
"""

import os


# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def call_claude(prompt, temperature=0.7, max_tokens=500, system_message=None):
    """
    Call Anthropic Claude API with the given prompt.
    
    Args:
        prompt: User prompt to send
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        system_message: Optional system message
    
    Returns:
        str: Generated text from Claude
    
    Raises:
        Exception: If API key is missing or API call fails
    """
    # Validate API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Set it in your .env file or environment."
        )
    
    if not api_key.strip():
        raise Exception("ANTHROPIC_API_KEY is empty")
    
    # Validate inputs
    if not prompt:
        raise Exception("Prompt cannot be empty")
    
    try:
        import anthropic
    except ImportError:
        raise Exception(
            "Anthropic package not installed. "
            "Run: pip install anthropic"
        )
    
    try:
        client = anthropic.Anthropic(api_key=api_key, timeout=30)
        
        # Build messages
        messages = [{"role": "user", "content": prompt}]
        
        # Add system message if provided
        system_param = system_message if system_message else ""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_param,
            messages=messages
        )
        
        # Validate response
        if not response:
            raise Exception("No response returned from Claude")
        
        if not hasattr(response, 'content') or not response.content:
            raise Exception("Claude response has no content")
        
        if not response.content[0].text:
            raise Exception("Claude returned empty text")
        
        return response.content[0].text
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise Exception(f"Claude authentication failed: {error_msg}")
        elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            raise Exception(f"Claude rate limit or quota exceeded: {error_msg}")
        elif "timeout" in error_msg.lower():
            raise Exception(f"Claude API timeout (30s): {error_msg}")
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise Exception(f"Network error connecting to Claude: {error_msg}")
        elif "overloaded" in error_msg.lower():
            raise Exception(f"Claude API is overloaded: {error_msg}")
        else:
            raise Exception(f"Claude API error: {error_msg}")

