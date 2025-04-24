from autoagent.config.llm_resolver import resolve_llm_config
from autoagent.executor.session_router import SessionRouter
from autoagent.executor.conversation_manager import ConversationManager

class AgentRunner:
    """
    Common library entrypoint to manage sessions and execute agents.
    """

    def __init__(self, base_cfg, tool_registry):
        """
        base_cfg: BaseConfig instance
        tool_registry: {tool_key: ToolClass, ...}
        """
        self.base_cfg = base_cfg
        self.tool_registry = tool_registry
        self.convo_mgr = ConversationManager()
        # session_id → {tenant_cfg, user_cfg, flows}
        self._sessions = {}

    def start_session(self, session_id: str, tenant_cfg, user_cfg, tenant_flows: dict):
        """
        Initialize a new session context.
        tenant_cfg: TenantConfig instance
        user_cfg:   UserConfig instance
        tenant_flows: dict of flows from tenant config
        """
        self.convo_mgr.create_session(session_id)
        self._sessions[session_id] = {
            "tenant_cfg": tenant_cfg,
            "user_cfg": user_cfg,
            "flows": tenant_flows
        }

    def handle_message(self, session_id: str, user_message: str, flow_name: str) -> dict:
        """
        Process one user message:
          - Check pause state
          - Append to history
          - Resolve LLM config
          - Instantiate the right agent
          - Run it and append assistant reply
        Returns: {"answer": str, "trace": list}
        """
        meta = self._sessions.get(session_id)
        if not meta:
            raise KeyError(f"Session '{session_id}' not found")

        if self.convo_mgr.is_paused(session_id):
            return {"answer": None, "status": "paused"}

        # Record user message
        self.convo_mgr.append(session_id, "user", user_message)

        # Resolve LLM config
        llm_cfg = resolve_llm_config(
            self.base_cfg,
            meta["tenant_cfg"],
            meta["user_cfg"]
        )

        # Pick and build agent
        router = SessionRouter(meta["flows"], self.tool_registry)
        agent = router.get_agent(flow_name, llm_cfg)

        # Run agent
        history = self.convo_mgr.get_history(session_id)
        result = agent.run(user_message, context=history)

        # Record and return
        self.convo_mgr.append(session_id, "assistant", result["answer"])
        return {
            "answer": result["answer"],
            "trace": result.get("trace", [])
        }
