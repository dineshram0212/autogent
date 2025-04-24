from collections import defaultdict
from typing import List, Dict

class ConversationManager:
    """
    Tracks two parallel logs per session:
      • _full_history   – every turn including supervisor
      • _llm_history    – only user/assistant turns for model context
    Also handles pause/resume for supervisor take-over.
    """

    def __init__(self):
        # session_id → full list of messages ({role,content})
        self._full_history: Dict[str, List[Dict[str,str]]] = defaultdict(list)
        # session_id → list without supervisor messages
        self._llm_history: Dict[str, List[Dict[str,str]]] = defaultdict(list)
        # pause flags
        self._paused: Dict[str, bool] = defaultdict(bool)

    def create_session(self, session_id: str):
        self._full_history[session_id] = []
        self._llm_history[session_id] = []
        self._paused[session_id] = False

    def append_user(self, session_id: str, content: str):
        msg = {"role": "user", "content": content}
        self._full_history[session_id].append(msg)
        self._llm_history[session_id].append(msg)

    def append_assistant(self, session_id: str, content: str):
        msg = {"role": "assistant", "content": content}
        self._full_history[session_id].append(msg)
        self._llm_history[session_id].append(msg)

    def inject_supervisor(self, session_id: str, content: str):
        """
        Supervisor intervenes.  This turns on pause and logs the
        supervisor message in full history only.
        """
        self.pause(session_id)
        msg = {"role": "supervisor", "content": content}
        self._full_history[session_id].append(msg)
        # note: do NOT append to _llm_history

    def resume(self, session_id: str):
        self._paused[session_id] = False

    def pause(self, session_id: str):
        self._paused[session_id] = True

    def is_paused(self, session_id: str) -> bool:
        return self._paused[session_id]

    def get_full_history(self, session_id: str) -> List[Dict[str,str]]:
        return list(self._full_history[session_id])

    def get_llm_history(self, session_id: str) -> List[Dict[str,str]]:
        return list(self._llm_history[session_id])
