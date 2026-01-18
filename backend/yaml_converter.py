# yaml_converter.py
"""
Converts legacy YAML format to specification-compliant format.
Handles empty/malformed YAML gracefully with comprehensive error checking.

Legacy format (from problem statement):
  agents:
    - name: agent_name
      task: "task description"
      depends_on: parent_agent

New format (specification):
  agents:
    - id: agent_id
      role: role_name
      goal: goal_description
  workflow:
    type: sequential
    steps:
      - agent: agent_id
"""

from safety import safe_get


def convert_legacy_to_spec(cfg):
    """
    Convert legacy YAML format to specification format.
    Handles None, empty, and malformed YAML gracefully.
    
    If the config already has 'workflow' section, assume it's spec-compliant.
    If it has agents with 'name' and 'task', convert to spec format.
    """
    
    # Handle None or empty config
    if cfg is None:
        return {"agents": [], "workflow": {"type": "sequential", "steps": []}}
    
    if not isinstance(cfg, dict):
        return {"agents": [], "workflow": {"type": "sequential", "steps": []}}
    
    if not cfg:
        return {"agents": [], "workflow": {"type": "sequential", "steps": []}}
    
    # Check if already spec-compliant
    if "workflow" in cfg:
        return cfg
    
    # Check if has agents section
    if "agents" not in cfg:
        return cfg
    
    # Validate agents is a list
    if not isinstance(cfg["agents"], list):
        return cfg
    
    # Handle empty agents list
    if not cfg["agents"]:
        return {
            "agents": [],
            "workflow": {"type": "sequential", "steps": []}
        }
    
    # Check if agents use 'name' field (legacy) or 'id' field (spec)
    first_agent = cfg["agents"][0] if cfg["agents"] else {}
    
    if not isinstance(first_agent, dict):
        # Malformed agent, return as-is
        return cfg
    
    if "name" not in first_agent:
        # Already using 'id', assume spec-compliant
        return cfg
    
    from ui import PastelUI
    
    print(f"\n{PastelUI.info('Converting legacy YAML format to specification format...', '🔄')}")
    
    # Convert agents
    new_agents = []
    dependencies = {}  # Track dependencies for workflow construction
    
    for agent in cfg["agents"]:
        if not isinstance(agent, dict):
            continue  # Skip malformed agents
        
        name = safe_get(agent, "name", "unnamed_agent")
        task = safe_get(agent, "task", "")
        depends_on = safe_get(agent, "depends_on")
        
        # Convert to spec format
        new_agent = {
            "id": name,
            "role": name.replace("_", " ").title(),  # Convert snake_case to Title Case
            "goal": task if task else "Complete assigned task"
        }
        
        # Preserve other fields (model, tools, etc.)
        for key in ["model", "tools", "toolsets", "description", "instruction"]:
            if key in agent:
                new_agent[key] = agent[key]
        
        new_agents.append(new_agent)
        
        # Track dependency
        if depends_on:
            dependencies[name] = depends_on
    
    # Build workflow from dependencies
    workflow = build_workflow_from_dependencies(new_agents, dependencies)
    
    # Build new config
    new_cfg = {
        "agents": new_agents,
        "workflow": workflow
    }
    
    # Preserve vars section if it exists
    if "vars" in cfg:
        new_cfg["vars"] = cfg["vars"]
        print(f"{PastelUI.warning('Variable substitution ({{{{var}}}}) is not yet implemented', 'ℹ')}")
    
    # Preserve models section if it exists
    if "models" in cfg:
        new_cfg["models"] = cfg["models"]
    
    print(f"{PastelUI.success(f'Converted {len(new_agents)} agents to specification format', '✓')}\n")
    
    return new_cfg


def build_workflow_from_dependencies(agents, dependencies):
    """
    Build a sequential workflow from dependency graph.
    Handles empty agents list and circular dependencies gracefully.
    
    Args:
        agents: List of agent configs
        dependencies: Dict mapping agent_id -> parent_agent_id
    
    Returns:
        Workflow configuration
    """
    
    # Handle empty agents
    if not agents:
        return {
            "type": "sequential",
            "steps": []
        }
    
    # Find root agents (no dependencies)
    agent_ids = [a.get("id", "") for a in agents if a.get("id")]
    
    if not agent_ids:
        return {
            "type": "sequential",
            "steps": []
        }
    
    roots = [aid for aid in agent_ids if aid not in dependencies]
    
    if not roots:
        # No explicit dependencies, assume sequential order
        return {
            "type": "sequential",
            "steps": [{"agent": aid} for aid in agent_ids]
        }
    
    # Build execution order using topological sort
    visited = set()
    order = []
    visiting = set()  # Track nodes being visited to detect cycles
    
    def visit(agent_id):
        if agent_id in visited:
            return
        
        if agent_id in visiting:
            # Cycle detected, skip to avoid infinite loop
            return
        
        visiting.add(agent_id)
        
        # Visit dependencies first
        if agent_id in dependencies:
            parent = dependencies[agent_id]
            if parent in agent_ids:
                visit(parent)
        
        visiting.remove(agent_id)
        visited.add(agent_id)
        order.append(agent_id)
    
    # Visit all agents
    for aid in agent_ids:
        visit(aid)
    
    # Build sequential workflow
    return {
        "type": "sequential",
        "steps": [{"agent": aid} for aid in order]
    }
