from autoagent.llm.factory import AGENT_MAP

class SessionRouter:
    """
    Library class to map a flow name → agent instance.
    """

    def __init__(self, tenant_flows: dict, tool_registry: dict):
        """
        tenant_flows: {
          "<flow_name>": {
            "agent_type": str,         # e.g. "react", "rag", etc.
            "tools": [str,...],        # list of tool keys
            "agent_params": dict       # optional kwargs for the agent ctor
          },
          ...
        }
        tool_registry: {tool_key: ToolClass, ...}
        """
        self.flows = tenant_flows
        self.tool_registry = tool_registry

    def get_agent(self, flow_name: str, llm_config: dict):
        flow = self.flows.get(flow_name)
        if not flow:
            raise KeyError(f"Flow '{flow_name}' not defined in tenant config")

        agent_type = flow["agent_type"]
        agent_cls = AGENT_MAP.get(agent_type)
        if not agent_cls:
            raise KeyError(f"Agent type '{agent_type}' not supported")

        # Build a sub-registry of only the tools this flow allows
        tools = {k: self.tool_registry[k] for k in flow.get("tools", [])}

        params = flow.get("agent_params", {})
        # Instantiate and return the agent
        return agent_cls(llm_config, tools, **params)
