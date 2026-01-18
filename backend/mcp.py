def run_tools(agent):

    if "tools" not in agent:
        return ""

    if "python" in agent["tools"]:
        return "[MCP] Python executed on provided data"

    return ""