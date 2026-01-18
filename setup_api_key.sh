#!/bin/bash
# setup_api_key.sh - Set up OpenAI API key for the session

export OPENAI_API_KEY="YOUR_API_KEY_HERE"

echo "✅ OpenAI API key set successfully!"
echo ""
echo "Now you can run:"
echo "  cd backend"
echo "  python run.py samples/team.yaml"
echo ""
echo "The system will use REAL OpenAI API calls instead of mocks."
