# Speed Optimization & API Key Setup

## Speed Improvements Made

### 1. Mock Response Speed
- **Before**: 1.5 seconds per mock call
- **After**: 0.3 seconds per mock call
- **Improvement**: 5x faster

### 2. API Timeout
- **Before**: 60 seconds timeout
- **After**: 30 seconds timeout
- **Improvement**: Faster failure detection

### 3. Token Limits
- **Before**: Unlimited tokens (slow, expensive)
- **After**: 500 max tokens per response
- **Improvement**: Faster responses, lower cost

## Performance Comparison

**team.yaml (3 agents)**:
- **Before**: ~4.5 seconds (1.5s × 3)
- **After**: ~0.9 seconds (0.3s × 3)
- **Speedup**: 5x faster

**agents.yaml (9 agents)**:
- **Before**: ~13.5 seconds (1.5s × 9)
- **After**: ~2.7 seconds (0.3s × 9)
- **Speedup**: 5x faster

## Setting Up New OpenAI API Key

If you want to use real OpenAI API calls instead of mocks:

### Option 1: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY="your-new-api-key-here"
python run.py samples/team.yaml
```

### Option 2: .env File
Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your-new-api-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

### Option 3: Direct in Code (Not Recommended)
I can add it directly to the code, but this is less secure.

## Benefits of Real API

With a valid API key:
- ✅ Real, unique responses for each agent
- ✅ Better quality outputs
- ✅ Actual reasoning and creativity
- ✅ No "[MOCK RESPONSE]" text

Let me know if you want to provide the API key and which method you prefer!
