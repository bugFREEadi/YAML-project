# mcp_tools.py
"""
MCP tool execution with comprehensive error handling.
Provides safe expression evaluation for the Calculator tool.
"""

import math
import signal
import re

class ToolTimeoutError(Exception):
    """Raised when a tool execution times out."""
    pass

def timeout_handler(signum, frame):
    """Signal handler for tool timeout."""
    raise ToolTimeoutError("Tool execution timed out")

def evaluate_expression(expression):
    """
    Safe evaluation of mathematical expressions.
    Allowed: math.*, abs, round, min, max, +, -, *, /, **, %, (, )
    """
    try:
        # Sanitation
        # Allow numbers, operators, parens, commas, whitespace, and alphabet (for math.func)
        if not re.match(r'^[\d\.\+\-\*\/\%\(\)\,\s\w]+$', expression):
            return None, "Invalid characters in expression"

        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max, "math": math})
        
        # Compile restricted to eval mode
        code = compile(expression, "<string>", "eval")
        
        # Check for disallowed names
        for name in code.co_names:
            if name not in allowed_names and name != "math":
                return None, f"Use of '{name}' is not allowed"
        
        # Execute safely
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return result, None

    except Exception as e:
        return None, f"Calculation failed: {str(e)}"

def calculate(expression):
    """
    Public wrapper for calculation.
    """
    result, error = evaluate_expression(expression)
    if error:
        return f"ERROR: {error}"
    return str(result)

def get_tool_instructions(toolsets):
    """
    Returns system prompt instructions for available tools.
    """
    instructions = []
    
    if not toolsets:
        return ""
    
    if isinstance(toolsets, str):
        toolsets = [toolsets]
        
    for t in toolsets:
        if t == "calculator":
            instructions.append(
                "TOOL AVAILABLE: Calculator\n"
                "HOW TO USE: To perform a calculation, output a line starting with 'CALCULATE:' followed by the expression.\n"
                "EXAMPLE: CALCULATE: 125 * 45 + math.sqrt(16)\n"
                "The system will halt, compute the result, and define it in the next user message."
            )
        elif t == "python":
            instructions.append(
                "TOOL AVAILABLE: Python Interpreter\n"
                "HOW TO USE: This is a simulation. You can assume standard Python libraries are available."
            )
            
    return "\n\n".join(instructions)

def run_tools(toolsets):
    """
    Legacy method kept for compatibility, but now logic is moved to executor Loop.
    """
    return [{"status": "ready", "info": "Tools are managed via ReAct loop in executor."}]