# Model Resolution Fix

## Issue
When a YAML file specifies a model (e.g., `claude-sonnet-4-0`), the system was simulating it with a different model (OpenAI) instead of making the API call to the exact model specified.

## Fix Applied

### Before ❌
```python
def call_anthropic(model, prompt, role):
    if anthropic_client:
        # Call Anthropic
    else:
        # Simulate Claude with OpenAI ← WRONG!
        return call_openai("gpt-4o-mini", prompt, role)
```

### After ✅
```python
def call_anthropic(model, prompt, role):
    if not anthropic_client:
        return f"ERROR: Model '{model}' requires ANTHROPIC_API_KEY..."
    
    # Always call the exact model specified
    r = anthropic_client.messages.create(model=model, ...)
```

## Behavior Now

1. **If YAML specifies OpenAI model** → Calls OpenAI API with exact model
2. **If YAML specifies Anthropic model** → Calls Anthropic API with exact model (or errors if no key)
3. **No simulation/substitution** → Always uses exact model from YAML

## Files Modified
- [models.py](file:///Users/adityashukla/Desktop/yaml-agent-system/backend/models.py) - Removed simulation fallback

## New Sample File
- [startup_openai.yaml](file:///Users/adityashukla/Desktop/yaml-agent-system/backend/samples/startup_openai.yaml) - OpenAI-only version for users without Anthropic key
