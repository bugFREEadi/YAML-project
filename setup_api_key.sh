#!/bin/bash
# setup_api_key.sh - Set up OpenAI API key for the session

export OPENAI_API_KEY="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"
export GOOGLE_API_KEY="AIzaSyCd2gcwdocpTdavTo2AStmVykh8mPLs13o"

echo "✅ OpenAI API key set successfully!"
echo ""
echo "Now you can run:"
echo "  cd backend"
echo "  python run.py samples/team.yaml"
echo ""
echo "The system will use REAL OpenAI API calls instead of mocks."
