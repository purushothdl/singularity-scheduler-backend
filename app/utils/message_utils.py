from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

def parse_history(history: List[Dict]) -> List[BaseMessage]:
    """Converts a list of dicts into a list of LangChain message objects."""
    messages: List[BaseMessage] = []
    for msg in history:
        msg_type = msg.get("type")
        content = msg.get("content", "")
        if msg_type == "human":
            messages.append(HumanMessage(content=content))
        elif msg_type == "ai":
            messages.append(AIMessage(content=content))
    return messages