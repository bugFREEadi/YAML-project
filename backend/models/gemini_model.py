# models/gemini_model.py
"""
Google Gemini model implementation - REAL API CALLS with robust error handling.
"""

import os


# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def call_gemini(prompt, temperature=0.7, max_tokens=500, system_message=None):
    """
    Call Google Gemini API with the given prompt.
    
    Args:
        prompt: User prompt to send
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens to generate
        system_message: Optional system instruction
    
    Returns:
        str: Generated text from Gemini
    
    Raises:
        Exception: If API key is missing or API call fails
    """
    # Validate API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception(
            "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set. "
            "Set it in your .env file or environment."
        )
    
    if not api_key.strip():
        raise Exception("GEMINI_API_KEY/GOOGLE_API_KEY is empty")
    
    # Validate inputs
    if not prompt:
        raise Exception("Prompt cannot be empty")
    
    try:
        import google.generativeai as genai
    except ImportError:
        raise Exception(
            "Google Generative AI package not installed. "
            "Run: pip install google-generativeai"
        )
    
    try:
        genai.configure(api_key=api_key)
        
        # Combine system message and prompt if provided
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        # Validate response
        if not response:
            raise Exception("No response returned from Gemini")
        
        if not hasattr(response, 'text'):
            raise Exception("Gemini response has no text attribute")
        
        text = response.text
        if text is None:
            raise Exception("Gemini returned None text")
        
        return text
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise Exception(f"Gemini authentication failed: {error_msg}")
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            raise Exception(f"Gemini rate limit or quota exceeded: {error_msg}")
        elif "timeout" in error_msg.lower():
            raise Exception(f"Gemini API timeout: {error_msg}")
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise Exception(f"Network error connecting to Gemini: {error_msg}")
        elif "blocked" in error_msg.lower() or "safety" in error_msg.lower():
            raise Exception(f"Gemini safety filter blocked response: {error_msg}")
        else:
            raise Exception(f"Gemini API error: {error_msg}")

