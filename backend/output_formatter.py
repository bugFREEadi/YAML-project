# output_formatter.py
"""
STRICT OUTPUT FORMATTER - INSTRUCTOR COMPLIANT
Outputs ONLY 4 sections in exact order, using beautiful PastelUI.
"""

from ui import PastelUI

def get_workflow_diagram_str(cfg):
    """
    Generates the string representation of the workflow diagram.
    """
    lines = []
    workflow = cfg.get("workflow", {})
    
    def visualize_workflow(node, indent=0):
        """Recursively visualize workflow nodes"""
        if not isinstance(node, dict):
            return
        
        prefix = "  " * indent
        
        if node.get("type") == "parallel":
            branches = node.get("branches", [])
            then_node = node.get("then")
            
            # Show parallel branches
            if len(branches) == 2:
                lines.append(f"{prefix}{branches[0]}  ─┐")
                if then_node:
                    if isinstance(then_node, dict) and "agent" in then_node:
                        lines.append(f"{prefix}             ├──► {then_node['agent']}")
                        if "then" in then_node:
                            lines[-1] += " ──►"
                    else:
                        lines.append(f"{prefix}             ├──►")
                lines.append(f"{prefix}{branches[1]}  ─┘")
            else:
                # Multiple branches
                for i, branch in enumerate(branches):
                    if i == 0:
                        lines.append(f"{prefix}{branch}  ─┐")
                    elif i == len(branches) - 1:
                        final_line = f"{prefix}{' ' * (len(branch) + 2)}├──►"
                        if then_node and isinstance(then_node, dict) and "agent" in then_node:
                            final_line += f" {then_node['agent']}"
                        lines.append(final_line)
                        lines.append(f"{prefix}{branch}  ─┘")
                    else:
                        lines.append(f"{prefix}{branch}  ─┤")
            
            # Continue with 'then' if it's a complex node
            if then_node and isinstance(then_node, dict):
                if "then" in then_node:
                    lines.append(f"{prefix}                 │")
                    lines.append(f"{prefix}                 ▼")
                    visualize_workflow(then_node.get("then"), indent)
        
        elif node.get("type") == "sequential":
            steps = node.get("steps", [])
            for step in steps:
                if isinstance(step, dict) and "agent" in step:
                    lines.append(f"{prefix}{step['agent']} ──►")
                    if "then" in step:
                        visualize_workflow(step["then"], indent)
                else:
                    visualize_workflow(step, indent)
        
        elif "agent" in node:
            agent_id = node["agent"]
            line = f"{prefix}{agent_id}"
            if "then" in node:
                line += " ──►"
                lines.append(line)
                visualize_workflow(node["then"], indent)
            else:
                line += " ──► FINAL"
                lines.append(line)
    
    visualize_workflow(workflow)
    return "\n".join(lines)


def print_strict_output(cfg, outputs, execution_log):
    """
    Main output function - prints ONLY the 4 required sections.
    Uses PastelUI for beautiful formatting.
    """
    
    # Identify workflow type
    workflow = cfg.get("workflow", {})
    workflow_type = workflow.get("type", "sequential")
    
    # SECTION 1: Workflow Diagram
    print(PastelUI.section("SECTION 1 – CONCEPTUAL WORKFLOW DIAGRAM", PastelUI.PASTEL_PURPLE))
    diagram = get_workflow_diagram_str(cfg)
    print(PastelUI.box(diagram, title="WorkFlow", color=PastelUI.PASTEL_BLUE))
    
    # SECTION 2: Detailed Agent Responses
    print(PastelUI.section("SECTION 2 – DETAILED AGENT RESPONSES", PastelUI.PASTEL_PURPLE))
    
    # Improved: Iterate strictly through execution log to capture ALL responses
    for entry in execution_log:
        agent_id = entry.get("agent_id", "UNKNOWN")
        artifact = entry.get("artifact", "")
        role = entry.get("role", "Agent")
        
        # Skip internal system entries if any
        if not agent_id or agent_id == "unknown":
            continue
            
        # Use box for each agent response
        title = f"{agent_id.upper()} ({role})"
        print(PastelUI.box(artifact.strip(), title=title, color=PastelUI.PASTEL_CYAN))
        print()
            
    # SECTION 3: Reviewer Response (Optional/Conditional)
    is_parallel_with_reviewer = (
        workflow_type == "parallel" and 
        isinstance(workflow.get("then"), dict) and 
        "agent" in workflow.get("then", {})
    )
    
    if is_parallel_with_reviewer:
        reviewer_id = workflow["then"]["agent"]
        if reviewer_id in outputs:
            print(PastelUI.section("SECTION 3 – CONSOLIDATED REVIEWER RESPONSE", PastelUI.PASTEL_PURPLE))
            
            output = outputs[reviewer_id]
            artifact = output.get("artifact", "")
            print(PastelUI.box(artifact.strip(), title=f"{reviewer_id.upper()} (Reviewer)", color=PastelUI.PASTEL_GREEN))
            print()
    
    # SECTION 4: LLM Trace Table
    print(PastelUI.section("SECTION 4 – LLM CALL TRACE TABLE", PastelUI.PASTEL_PURPLE))
    
    # Prepare table data
    headers = ["Agent", "Model", "Provider", "Purpose"]
    rows = []
    
    for entry in execution_log:
        agent_id = entry.get("agent_id", "unknown")
        model = entry.get("model_used", "unknown")
        provider = entry.get("provider", "unknown")
        role = entry.get("role", "agent")
        
        # Determine purpose
        purpose = role.lower()
        if "research" in purpose:
            purpose = "research"
        elif "writer" in purpose or "write" in purpose:
            purpose = "content creation"
        elif "review" in purpose or "lead" in purpose:
            purpose = "consolidation"
        else:
            purpose = purpose[:20]
            
        rows.append([agent_id, model, provider, purpose])
        
    print(PastelUI.table(headers, rows))
    print()
