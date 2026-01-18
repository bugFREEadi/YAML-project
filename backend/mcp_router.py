"""
MCP STYLE ROUTER – CONCEPTUALLY CORRECT STUB
"""

def mcp_execute(tool_name, context):

    registry = {
        "python": python_stub,
        "calculator": calc_stub,
        "web": web_stub
    }

    fn = registry.get(tool_name)

    if not fn:
        return f"[MCP] Unknown tool: {tool_name}"

    return fn(context)


def python_stub(ctx):
    return "[MCP-python] executed safely (stub)"


def calc_stub(ctx):
    return "[MCP-calculator] result (stub)"


def web_stub(ctx):
    return "[MCP-web] fetched (stub)"