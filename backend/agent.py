# agent.py
"""
Agent class with safe field access and comprehensive error handling.
"""

from safety import safe_get


class Agent:
    def __init__(self, cfg):
        """
        Initialize agent with safe field access and defaults.
        Handles missing or malformed fields gracefully.
        """
        if not isinstance(cfg, dict):
            cfg = {}
        
        self.id = safe_get(cfg, "id", "unknown_agent")
        self.role = safe_get(cfg, "role", "Agent")
        self.goal = safe_get(cfg, "goal", "Complete assigned task")
        self.model = safe_get(cfg, "model", "gpt-4o-mini")
        self.description = safe_get(cfg, "description", "")
        self.instruction = safe_get(cfg, "instruction", "")
        
        # Handle sub_agents with type validation
        sub_agents = safe_get(cfg, "sub_agents", [])
        self.sub_agents = sub_agents if isinstance(sub_agents, list) else []
        
        # SPEC COMPLIANT - support both toolsets and tools
        toolsets = safe_get(cfg, "toolsets", safe_get(cfg, "tools", []))
        self.toolsets = toolsets if isinstance(toolsets, list) else []

    def build_prompt(self, context, global_vars=None):
        """
        Build the final prompt, injecting context and performing variable substitution.
        Handles None/empty values gracefully.
        """
        # Ensure context is a string
        if context is None:
            context = ""
        
        # Use instruction if provided (for detailed agent configs)
        if self.instruction:
            prompt = f"""
{self.instruction}

CONTEXT:
{context}
"""
        else:
            # Default prompt format
            prompt = f"""
AGENT ID : {self.id}
ROLE     : {self.role}
GOAL     : {self.goal}
MODEL    : {self.model}

CONTEXT:
{context}
"""
        
        # ---- VARIABLE SUBSTITUTION ----
        # Replace {{var_name}} with values from global config 'vars'
        if global_vars and isinstance(global_vars, dict):
            for key, value in global_vars.items():
                placeholder = f"{{{{{key}}}}}"  # e.g., {{topic}}
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def __repr__(self):
        """String representation for better error messages."""
        return f"Agent(id='{self.id}', role='{self.role}', model='{self.model}')"