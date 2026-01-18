import yaml
from datetime import datetime

# ===================== VALIDATOR =====================

def validate_config(cfg):

    if "agents" not in cfg:
        return "❌ Missing 'agents' section"

    if "workflow" not in cfg:
        return "❌ Missing 'workflow' section"

    ids = [a["id"] for a in cfg["agents"] if "id" in a]

    # ----- Agents -----
    for a in cfg["agents"]:

        for k in ["id", "role", "goal"]:
            if k not in a:
                return f"❌ Agent missing field: {k}"

        if "tools" in a and not isinstance(a["tools"], list):
            return "❌ tools must be list"

        if "sub_agents" in a:
            for s in a["sub_agents"]:
                if s not in ids:
                    return f"❌ Unknown subagent reference: {s}"

    # ----- Models -----
    if "models" in cfg:
        for m in cfg["models"].keys():
            if "provider" not in cfg["models"][m]:
                return f"❌ model {m} missing provider"

    # ----- Workflow -----
    w = cfg["workflow"]

    if w.get("type") not in ["sequential", "parallel"]:
        return "❌ workflow.type must be sequential or parallel"

    if w["type"] == "sequential":
        if "steps" not in w:
            return "❌ Sequential needs steps"

    if w["type"] == "parallel":
        if "branches" not in w or "then" not in w:
            return "❌ Parallel needs branches + then"

    return None


# ===================== UTILITIES =====================

def build_text_graph(cfg):

    if cfg["workflow"]["type"] == "sequential":
        chain = " → ".join([s["agent"] for s in cfg["workflow"]["steps"]])
        return f"[SEQUENTIAL]\n{chain}"

    b = ", ".join(cfg["workflow"]["branches"])
    t = cfg["workflow"]["then"]["agent"]

    return f"""
[PARALLEL]
{b}
   ↓
[THEN] {t}
"""


def resolve_model(agent, cfg):

    # 1. agent me model diya ho to use karo
    if "model" in agent:
        return agent["model"]

    # 2. YAML me models section ho to uska default lo
    if "models" in cfg:
        first = list(cfg["models"].keys())[0]
        return first

    # 3. HARD DEFAULT → working OpenAI model
    return "gpt-4o-mini"


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


# ===================== MAIN EXECUTE YAML =====================

def execute_yaml(yaml_text):
    """
    Main entry point for executing YAML configuration.
    Called by API endpoint.
    """
    import yaml
    from executor import execute
    
    try:
        # Parse YAML
        cfg = yaml.safe_load(yaml_text)
        
        # Validate
        error = validate_config(cfg)
        if error:
            return {"error": error}
        
        # Build execution graph
        graph = build_text_graph(cfg)
        
        # Execute workflow
        from executor import run_sequential, run_parallel
        
        if cfg["workflow"]["type"] == "parallel":
            outputs = run_parallel(cfg)
        else:
            outputs = run_sequential(cfg)
        
        # Build trace
        trace = []
        for agent_id, result in outputs.items():
            trace.append({
                "agent": agent_id,
                "artifact": result["artifact"][:200] + "..." if len(result["artifact"]) > 200 else result["artifact"],
                "proof": result.get("proof", {}),
                "tool": result.get("tool")
            })
        
        # Get final output (last agent in chain)
        final_output = list(outputs.values())[-1]["artifact"] if outputs else ""
        
        # Load memory
        from memory import load_memory
        memory = load_memory()
        
        return {
            "graph": graph,
            "final_output": final_output,
            "trace": trace,
            "memory": memory
        }
        
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}
