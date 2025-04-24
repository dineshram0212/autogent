from .agents.tot_agent import TOTAgent
from .agents.self_refine_agent import SelfRefineAgent
from .agents.code_agent import CodeAgent
from .agents.base_agent import BaseAgent
from .agents.autonomous_agent import AutonomousAgent
from .agents.convo_overlap_agent import ConvoOverlapAgent
from .agents.rag_agent import RAGAgent
from .agents.react_agent import ReActAgent
from .agents.cot_agent import CoTAgent


AGENT_MAP = {
  "react": ReActAgent,
  "cot": CoTAgent,
  "rag": RAGAgent,
  "tot": TOTAgent,
  "self_refine": SelfRefineAgent,
  "code": CodeAgent,
  "autonomous": AutonomousAgent,
  "convo_overlap": ConvoOverlapAgent,
}


'''
Usage:
agent_cls = AGENT_MAP[agent_type]
agent = agent_cls(config, TOOL_REGISTRY)
result = agent.run(user_input, session_context)
'''