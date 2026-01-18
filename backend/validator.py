# validator.py
"""
Comprehensive YAML configuration validator with graceful error handling.
Returns ValidationResult with errors, warnings, and auto-fixes instead of crashing.
"""

from safety import ValidationResult, detect_cycles, build_dependency_graph, safe_get


def validate(cfg):
    """
    Comprehensive YAML configuration validator.
    Returns ValidationResult instead of raising exceptions.
    Implements two-tier validation: critical errors vs warnings with defaults.
    """
    result = ValidationResult(valid=True)
    
    # Handle None or empty config
    if cfg is None:
        result.add_error("Configuration is None - file may be empty or contain only comments")
        return result
    
    if not isinstance(cfg, dict):
        result.add_error(f"Configuration must be a dictionary, got {type(cfg).__name__}. Check YAML structure.")
        return result
    
    if not cfg:
        result.add_error("Configuration is empty - no keys found in YAML")
        return result
    
    # ===== TOP-LEVEL SECTIONS =====
    if "agents" not in cfg:
        result.add_error("Missing required 'agents' section. Add: agents: [...]")
    elif not isinstance(cfg["agents"], list):
        result.add_error(f"'agents' must be a list, got {type(cfg['agents']).__name__}")
    elif len(cfg["agents"]) == 0:
        result.add_error("'agents' list is empty - at least one agent is required")
    
    if "workflow" not in cfg:
        result.add_error("Missing required 'workflow' section. Add: workflow: {type: sequential, ...}")
    elif not isinstance(cfg["workflow"], dict):
        result.add_error(f"'workflow' must be a dictionary, got {type(cfg['workflow']).__name__}")
    elif not cfg["workflow"]:
        result.add_error("'workflow' section is empty - must contain 'type' field")
    
    # If missing main sections, abort early (cannot validate contents)
    if result.errors:
        return result
    
    # ===== AGENTS VALIDATION =====
    ids = []
    seen_ids = set()
    
    for i, agent in enumerate(cfg["agents"]):
        if not isinstance(agent, dict):
            result.add_error(f"Agent #{i+1} must be a dictionary, got {type(agent).__name__}")
            continue
        
        agent_id = agent.get("id", f"agent_{i}")
        
        # Required fields with graceful handling
        if "id" not in agent:
            result.add_warning(f"Agent #{i+1} missing 'id' field, using 'agent_{i}'")
            agent["id"] = f"agent_{i}"
            agent_id = f"agent_{i}"
            result.add_fix(f"Auto-assigned ID 'agent_{i}' to agent #{i+1}")
        else:
            if agent["id"] in seen_ids:
                result.add_error(f"Duplicate agent ID found: '{agent['id']}'")
            seen_ids.add(agent["id"])
            ids.append(agent["id"])
        
        if "role" not in agent:
            result.add_warning(f"Agent '{agent_id}' missing 'role' field, using default")
            agent["role"] = "Agent"
            result.add_fix(f"Auto-assigned role 'Agent' to '{agent_id}'")
        
        if "goal" not in agent:
            result.add_warning(f"Agent '{agent_id}' missing 'goal' field, using default")
            agent["goal"] = "Complete assigned task"
            result.add_fix(f"Auto-assigned default goal to '{agent_id}'")
        
        # Optional fields validation
        if "toolsets" in agent and not isinstance(agent["toolsets"], list):
            result.add_warning(f"Agent '{agent_id}': 'toolsets' must be a list, ignoring")
            agent["toolsets"] = []
            result.add_fix(f"Reset 'toolsets' to empty list for '{agent_id}'")
        
        if "tools" in agent and not isinstance(agent["tools"], list):
            result.add_warning(f"Agent '{agent_id}': 'tools' must be a list, ignoring")
            agent["tools"] = []
            result.add_fix(f"Reset 'tools' to empty list for '{agent_id}'")
        
        if "sub_agents" in agent:
            if not isinstance(agent["sub_agents"], list):
                result.add_warning(f"Agent '{agent_id}': 'sub_agents' must be a list, ignoring")
                agent["sub_agents"] = []
                result.add_fix(f"Reset 'sub_agents' to empty list for '{agent_id}'")
    
    # ===== MODELS VALIDATION =====
    if "models" in cfg:
        if not isinstance(cfg["models"], dict):
            result.add_warning("'models' section must be a dictionary, ignoring")
            cfg["models"] = {}
            result.add_fix("Reset 'models' to empty dictionary")
        else:
            for model_name, model_cfg in cfg["models"].items():
                if not isinstance(model_cfg, dict):
                    result.add_warning(f"Model '{model_name}' config must be a dictionary, ignoring")
                    continue
                
                if "provider" not in model_cfg:
                    result.add_warning(f"Model '{model_name}' missing 'provider' field, using 'openai'")
                    model_cfg["provider"] = "openai"
                    result.add_fix(f"Auto-assigned provider 'openai' to model '{model_name}'")
                else:
                    # Validate provider value
                    valid_providers = ["openai", "gemini", "google", "claude", "anthropic"]
                    if model_cfg["provider"].lower() not in valid_providers:
                        result.add_warning(
                            f"Model '{model_name}' has unknown provider '{model_cfg['provider']}'. "
                            f"Valid providers: {', '.join(valid_providers)}"
                        )
                
                if "model" not in model_cfg:
                    result.add_warning(f"Model '{model_name}' missing 'model' field, using 'gpt-4o-mini'")
                    model_cfg["model"] = "gpt-4o-mini"
                    result.add_fix(f"Auto-assigned model 'gpt-4o-mini' to '{model_name}'")
    
    # ===== WORKFLOW VALIDATION =====
    workflow = cfg["workflow"]
    
    if "type" not in workflow:
        result.add_error("Workflow missing required 'type' field. Must be 'sequential' or 'parallel'")
        return result
    
    workflow_type = workflow.get("type")
    if workflow_type not in ["sequential", "parallel"]:
        result.add_error(
            f"Workflow type must be 'sequential' or 'parallel', got '{workflow_type}'. "
            f"Fix: workflow: {{type: sequential, ...}}"
        )
        return result
    
    # Validate workflow structure recursively
    _validate_workflow_node(workflow, ids, result, path="workflow")
    
    # ===== SUB-AGENT VALIDATION =====
    for agent in cfg["agents"]:
        if "sub_agents" in agent and isinstance(agent["sub_agents"], list):
            for sub_agent_id in agent["sub_agents"]:
                if sub_agent_id not in ids:
                    result.add_error(f"Agent '{agent.get('id','?')}' references unknown sub-agent '{sub_agent_id}'")
    
    # ===== CYCLE DETECTION =====
    # Build dependency graph from sub_agents
    dep_graph = build_dependency_graph(cfg["agents"])
    cycles = detect_cycles(dep_graph)
    
    if cycles:
        for cycle in cycles:
            cycle_str = " -> ".join(cycle)
            result.add_error(f"Circular dependency detected: {cycle_str}")
    
    return result


def _validate_workflow_node(node, valid_agent_ids, result, path="workflow"):
    """
    Recursively validate workflow node structure.
    Handles sequential, parallel, and single agent nodes.
    """
    if not isinstance(node, dict):
        result.add_error(f"{path}: workflow node must be a dictionary")
        return
    
    node_type = node.get("type")
    
    # Sequential workflow validation
    if node_type == "sequential":
        if "steps" not in node:
            result.add_error(f"{path}: sequential workflow missing 'steps' field")
        elif not isinstance(node["steps"], list):
            result.add_error(f"{path}: workflow 'steps' must be a list")
        else:
            for idx, step in enumerate(node["steps"]):
                step_path = f"{path}.steps[{idx}]"
                _validate_workflow_node(step, valid_agent_ids, result, step_path)
    
    # Parallel workflow validation
    elif node_type == "parallel":
        if "branches" not in node:
            result.add_error(f"{path}: parallel workflow missing 'branches' field")
        elif not isinstance(node["branches"], list):
            result.add_error(f"{path}: workflow 'branches' must be a list")
        else:
            if len(node["branches"]) < 2:
                result.add_warning(f"{path}: parallel workflow has only {len(node['branches'])} branch(es), consider using sequential")
            
            for branch in node["branches"]:
                if branch not in valid_agent_ids:
                    result.add_error(f"{path}: workflow branch references unknown agent '{branch}'")
        
        # Parallel workflows should have 'then' for aggregation
        if "then" not in node:
            result.add_warning(f"{path}: parallel workflow missing 'then' field (no aggregation)")
    
    # Single agent node
    elif "agent" in node:
        agent_id = node["agent"]
        if agent_id not in valid_agent_ids:
            result.add_error(f"{path}: references unknown agent '{agent_id}'")
    
    # Handle 'then' chaining
    if "then" in node:
        then_path = f"{path}.then"
        _validate_workflow_node(node["then"], valid_agent_ids, result, then_path)