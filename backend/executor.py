# executor.py
"""
Judge-compliant workflow executor with modular architecture.
STRICT: Only imports from models.router, never direct API imports.
"""

import json
import time
import hashlib
from datetime import datetime
import concurrent.futures

# CRITICAL: Only import from router, never direct API imports
from models.router import call_model

from memory import save_memory
from mcp_tools import run_tools
from agent import Agent
from safety import ErrorReport, truncate_text

# Global execution log
EXECUTION_LOG = []
EXECUTION_ORDER = []

# Beautiful UI colors
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    
    PASTEL_PINK = '\033[38;5;217m'
    PASTEL_BLUE = '\033[38;5;153m'
    PASTEL_GREEN = '\033[38;5;158m'
    PASTEL_YELLOW = '\033[38;5;229m'
    PASTEL_PURPLE = '\033[38;5;183m'
    PASTEL_CYAN = '\033[38;5;159m'


def run_agent(agent: Agent, context: str, cfg: dict):
    """
    Execute agent with MANDATORY subagent-first execution.
    Uses router for all model calls - NO direct API imports.
    """
    global EXECUTION_LOG, EXECUTION_ORDER
    
    start_time = datetime.now()
    context_received = context
    
    # Validate agent object
    if not agent:
        error_msg = "Agent object is None"
        EXECUTION_LOG.append({
            "agent_id": "unknown",
            "role": "unknown",
            "goal": "unknown",
            "model": "unknown",
            "provider": "error",
            "model_used": "unknown",
            "context_received": context_received,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "artifact": f"[ERROR: {error_msg}]"
        })
        return {
            "artifact": f"[ERROR: {error_msg}]",
            "provider": "error",
            "status": "failed"
        }
    
    try:
        # ===== CRITICAL: SUBAGENTS MUST RUN FIRST =====
        if agent.sub_agents:
            sub_results = {}
            
            for sub_id in agent.sub_agents:
                try:
                    sub_agent_data = next((a for a in cfg.get("agents", []) if a.get("id") == sub_id), None)
                    if not sub_agent_data:
                        print(f"{Colors.YELLOW}⚠ Warning: Sub-agent '{sub_id}' not found for agent '{agent.id}'{Colors.RESET}")
                        continue
                    
                    # Recursively run sub-agent
                    sub_agent_obj = Agent(sub_agent_data)
                    sub_res = run_agent(sub_agent_obj, context, cfg)
                    sub_results[sub_id] = sub_res.get('artifact', '')
                except Exception as e:
                    print(f"{Colors.RED}✗ Error running sub-agent '{sub_id}': {str(e)}{Colors.RESET}")
                    sub_results[sub_id] = f"[ERROR: {str(e)}]"
            
            # Build context from sub-agent results
            for sub_id, sub_artifact in sub_results.items():
                truncated, _ = truncate_text(sub_artifact, 1024)
                context += f"\n\n--- FROM AGENT: {sub_id} ---\n{truncated}"
        
        # Build prompt
        try:
            global_vars = cfg.get("vars", {})
            prompt = agent.build_prompt(context, global_vars)
        except Exception as e:
            raise Exception(f"Failed to build prompt: {str(e)}")
        
        # Tool support
        tool_result = None
        if agent.toolsets:
            try:
                tool_result = run_tools(agent.toolsets)
                if tool_result:
                    prompt += f"\n\n[TOOLS]: {json.dumps(tool_result, indent=2)}"
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Tool execution failed for '{agent.id}': {str(e)}{Colors.RESET}")
        
        # ===== REAL LLM CALL VIA ROUTER WITH ReAct LOOP =====
        from mcp_tools import get_tool_instructions, calculate
        
        system_message = f"You are a {agent.role}. {agent.goal}"
        
        # Add tool instructions if applicable
        tool_instructions = get_tool_instructions(agent.toolsets)
        if tool_instructions:
            system_message = f"{system_message}\n\n{tool_instructions}"
        
        # Show progress indicator with beautiful colors
        from ui import PastelUI
        print(f"{PastelUI.PASTEL_CYAN}⏳ Running:{PastelUI.RESET} {PastelUI.BOLD}{agent.id}{PastelUI.RESET} {PastelUI.DIM}({agent.role}){PastelUI.RESET}", flush=True)
        
        # Validate model is specified
        if not agent.model:
            raise Exception(f"Agent '{agent.id}' has no model specified")
            
        final_text = ""
        current_prompt = prompt
        loop_count = 0
        max_loops = 3
        
        while loop_count < max_loops:
            try:
                res = call_model(
                    model_name=agent.model,
                    prompt=current_prompt,
                    temperature=0.7,
                    max_tokens=500,
                    system_message=system_message
                )
            except Exception as e:
                # Provide detailed error context
                error_msg = f"Model call failed for agent '{agent.id}' using model '{agent.model}': {str(e)}"
                raise Exception(error_msg)
            
            text = res.get("text", "")
            provider = res.get("provider", "unknown")
            model_used = res.get("model", agent.model)
            
            # Check for Calculator Tool Usage
            if "CALCULATE:" in text and "calculator" in agent.toolsets:
                import re
                match = re.search(r"CALCULATE:\s*(.+)", text, re.IGNORECASE)
                if match:
                    expression = match.group(1).strip()
                    print(f"{PastelUI.PASTEL_YELLOW}🛠  [Tool Call] Calculating: {expression}...{PastelUI.RESET}")
                    
                    # Execute Tool
                    result = calculate(expression)
                    
                    print(f"{PastelUI.BRIGHT_GREEN}✅ [Tool Result] {result}{PastelUI.RESET}")
                    
                    # Append result to prompt for next iteration
                    current_prompt += f"\n\n[AGENT OUTPUT]: {text}\n[SYSTEM TOOL RESULT]: {result}\n(Now continue your task with this result)"
                    loop_count += 1
                    continue # Loop again
            
            # If no tool call or loop finished
            final_text = text
            break
            
        if not final_text and text:
            final_text = text
            
        text = final_text

        provider = res.get("provider", "unknown")
        model_used = res.get("model", agent.model)
        
        # Validate response
        if not text:
            print(f"{Colors.YELLOW}⚠ Warning: Empty response from model for agent '{agent.id}'{Colors.RESET}")
            text = "[Empty response from model]"
        
        # ===== MEMORY EXTRACTION (BOUNDED) =====
        takeaways = {"insights": [], "numbers": [], "keywords": [], "decisions": []}
        
        if text:
            lines = text.split("\n")
            for line in lines[:50]:
                line_stripped = line.strip()
                if len(line_stripped) > 200:
                    continue
                
                line_lower = line.lower()
                
                if ("•" in line or line_stripped.startswith("-")) and len(takeaways["insights"]) < 10:
                    takeaways["insights"].append(line_stripped)
                
                if any(x in line_lower for x in ["%", "$", "₹", "million", "billion"]) and len(takeaways["numbers"]) < 10:
                    takeaways["numbers"].append(line_stripped)
                
                if any(x in line_lower for x in ["decided", "recommendation", "suggest"]) and len(takeaways["decisions"]) < 10:
                    takeaways["decisions"].append(line_stripped)
                
                keywords_list = ["ai", "startup", "market", "growth", "automation", "agent"]
                for k in keywords_list:
                    if k in line_lower and len(takeaways["keywords"]) < 10:
                        takeaways["keywords"].append(k)
        
        takeaways["keywords"] = list(set(takeaways["keywords"]))[:10]
        
        try:
            save_memory(agent.id, takeaways)
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Memory save failed for '{agent.id}': {str(e)}{Colors.RESET}")
        
        # Log execution
        end_time = datetime.now()
        EXECUTION_LOG.append({
            "agent_id": agent.id,
            "role": agent.role,
            "goal": agent.goal,
            "model": agent.model,
            "provider": provider,
            "model_used": model_used,
            "context_received": context_received,
            "timestamp": end_time.strftime("%H:%M:%S"),
            "artifact": text
        })
        EXECUTION_ORDER.append(agent.id)
        
        # Show completion indicator with beautiful colors
        from ui import PastelUI
        print(f"{PastelUI.BRIGHT_GREEN}✓ Completed:{PastelUI.RESET} {PastelUI.BOLD}{agent.id}{PastelUI.RESET}", flush=True)
        
        return {
            "artifact": text,
            "provider": provider,
            "model_used": model_used,
            "tool": tool_result,
            "status": "success"
        }
    
    except Exception as e:
        # Enhanced error logging with full context
        error_msg = str(e)
        error_type = type(e).__name__
        
        print(f"{Colors.RED}✗ Failed: {agent.id} - {error_msg}{Colors.RESET}")
        
        # Log failed execution with detailed error info
        EXECUTION_LOG.append({
            "agent_id": agent.id,
            "role": agent.role,
            "goal": agent.goal,
            "model": agent.model,
            "provider": "error",
            "model_used": agent.model,
            "context_received": context_received,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "artifact": f"[ERROR: {error_type}: {error_msg}]",
            "error_type": error_type,
            "error_message": error_msg
        })
        EXECUTION_ORDER.append(agent.id)
        
        return {
            "artifact": f"[ERROR: {error_type}: {error_msg}]",
            "provider": "error",
            "status": "failed",
            "error_type": error_type,
            "error_message": error_msg
        }



def process_step(step_node, context, agents_map, cfg, depth=0):
    """Process workflow steps recursively with proper context aggregation."""
    if depth > 20:
        return {
            "error": {
                "artifact": "[ERROR: Maximum workflow depth exceeded (infinite loop detection)]",
                "provider": "system",
                "status": "failed"
            }
        }
    
    outputs = {}
    current_context = context
    
    if not isinstance(step_node, dict):
        return outputs
    
    # Parallel execution
    if step_node.get("type") == "parallel":
        branches = step_node.get("branches", [])
        branch_outputs = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(run_agent, agents_map[aid], current_context, cfg): aid 
                      for aid in branches if aid in agents_map}
            
            for future in concurrent.futures.as_completed(futures):
                aid = futures[future]
                try:
                    branch_outputs[aid] = future.result(timeout=120)
                except:
                    branch_outputs[aid] = {
                        "artifact": f"[TIMEOUT: {aid}]",
                        "provider": "error",
                        "status": "failed"
                    }
        
        outputs.update(branch_outputs)
        
        # Aggregate parallel outputs for next stage (reviewer needs full context)
        for k, v in branch_outputs.items():
            # Use larger truncation for reviewer to get detailed context
            truncated, _ = truncate_text(v.get('artifact', ''), 2048)
            current_context += f"\n\n--- From {k} ---\n{truncated}"
    
    # Sequential execution
    elif step_node.get("type") == "sequential":
        for sub_step in step_node.get("steps", []):
            step_outs = process_step(sub_step, current_context, agents_map, cfg, depth + 1)
            outputs.update(step_outs)
            
            for k, v in step_outs.items():
                truncated, _ = truncate_text(v.get('artifact', ''), 1024)
                current_context += f"\n\n--- From {k} ---\n{truncated}"
    
    # Single agent
    elif "agent" in step_node:
        aid = step_node.get("agent")
        if aid in agents_map:
            res = run_agent(agents_map[aid], current_context, cfg)
            outputs[aid] = res
            truncated, _ = truncate_text(res.get('artifact', ''), 1024)
            current_context += f"\n\n--- From {aid} ---\n{truncated}"
    
    # Handle 'then' chaining
    if "then" in step_node:
        next_outputs = process_step(step_node["then"], current_context, agents_map, cfg, depth + 1)
        outputs.update(next_outputs)
    
    return outputs


# Old output functions removed - using new strict formatter


def execute(cfg):
    """Main execution with strict 4-section output format."""
    global EXECUTION_LOG, EXECUTION_ORDER
    EXECUTION_LOG = []
    EXECUTION_ORDER = []
    
    # Import new output formatter and UI
    from output_formatter import print_strict_output
    from ui import PastelUI, print_banner
    
    # Instantiate agents
    agents_map = {}
    for a_data in cfg.get("agents", []):
        if isinstance(a_data, dict) and "id" in a_data:
            try:
                agents_map[a_data["id"]] = Agent(a_data)
            except Exception as e:
                print(f"{Colors.RED}Error creating agent {a_data.get('id')}: {e}{Colors.RESET}")
    
    if not agents_map:
        print(f"{Colors.RED}ERROR: No valid agents{Colors.RESET}")
        return
    
    # Show beautiful execution start banner
    print_banner(f"{PastelUI.ROCKET}  YAML Agent Orchestration System  {PastelUI.SPARKLE}")
    print(f"{PastelUI.PASTEL_CYAN}{PastelUI.BOLD}Agents:{PastelUI.RESET} {len(agents_map)} | {PastelUI.PASTEL_LAVENDER}{PastelUI.BOLD}Workflow:{PastelUI.RESET} {cfg.get('workflow', {}).get('type', 'unknown')}")
    print(f"{PastelUI.divider('─', 80, PastelUI.PASTEL_PURPLE)}\n", flush=True)
    
    # Execute workflow
    try:
        outputs = process_step(cfg.get("workflow", {}), "", agents_map, cfg, depth=0)
    except Exception as e:
        print(f"{Colors.RED}Workflow execution error: {e}{Colors.RESET}")
        outputs = {}
    
    # Save output.json
    try:
        with open("output.json", "w") as f:
            json.dump(outputs, f, indent=2)
    except Exception as e:
        print(f"{Colors.RED}Error saving output.json: {e}{Colors.RESET}")
    
    # Print STRICT 4-section output (NO extra text)
    print_strict_output(cfg, outputs, EXECUTION_LOG)

