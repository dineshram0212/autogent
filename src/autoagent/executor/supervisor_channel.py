# autoagent/orchestrator/supervisor_channel.py

from autoagent.executor.conversation_manager import ConversationManager

class SupervisorChannel:
    """
    Simple API for human override without sharing with LLM.
    """

    def __init__(self, convo_mgr: ConversationManager):
        self.convo_mgr = convo_mgr

    def take_over(self, session_id: str):
        """Explicitly pause the session so LLM stops responding."""
        self.convo_mgr.pause(session_id)

    def inject(self, session_id: str, content: str):
        """
        Inject supervisor message into the full transcript only.
        """
        self.convo_mgr.inject_supervisor(session_id, content)

    def release(self, session_id: str):
        """Supervisor finishes — resume LLM participation."""
        self.convo_mgr.resume(session_id)
