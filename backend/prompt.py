def build_prompt(agent, context, intent):

    return f"""

YOU ARE AN AUTONOMOUS WORKER
NOT A CHAT ASSISTANT
NO QUESTIONS
RETURN FINAL ARTIFACT ONLY

INTENT: {intent}

ROLE: {agent['role']}
GOAL: {agent['goal']}

CONTEXT FROM PREVIOUS AGENTS:
{context}

AVAILABLE TOOLS: {agent.get("tools","none")}
"""