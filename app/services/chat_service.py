import json
from typing import AsyncGenerator, Dict, Any, List, Set

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage
)

from app.agent.graph import agent_app, AgentState
from app.agent.prompts.system_prompts import get_system_prompt
from app.schemas.chat import ChatRequest
from app.schemas.user import UserInDB
from app.utils.message_utils import parse_history


class ChatService:
    """Service to manage and orchestrate chat interactions with the AI agent."""

    def __init__(self):
        self.agent_app = agent_app
        self.get_system_prompt = get_system_prompt

    async def stream_agent_response(
        self, request: ChatRequest, current_user: UserInDB
    ) -> AsyncGenerator[str, None]:
        """
        Processes a chat request and streams the agent's formatted response.
        """
        system_prompt = self.get_system_prompt(current_user)
        history = parse_history(request.history)
        
        messages: List[BaseMessage] = [SystemMessage(content=system_prompt)]
        messages.extend(history)
        messages.append(HumanMessage(content=request.input))
        
        initial_state: AgentState = {
            "messages": messages,
            "current_user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "timezone": current_user.timezone,
            },
        }

        seen_tool_calls: Set[str] = set()

        async for event in self.agent_app.astream(initial_state, {"recursion_limit": 25}):
            formatted_event = self._format_stream_event(event, seen_tool_calls)
            if formatted_event:
                yield formatted_event

        yield "data: [DONE]\n\n"

    def _format_stream_event(self, event: Dict[str, Any], seen_tool_calls: Set[str]) -> str | None:
        """
        Formats a single event chunk from the agent into an SSE-compatible string.

        Args:
            event (Dict[str, Any]): The event chunk from the agent.
            seen_tool_calls (Set[str]): A set of tool call IDs that have already been processed.

        Returns:
            str | None: The formatted SSE string, or None if the event should be ignored.
        """
        for key, value in event.items():
            if key == "agent":
                return self._format_ai_message(value, seen_tool_calls)
            elif key == "tools":
                return self._format_tool_message(value)
        return None

    def _format_ai_message(self, value: Dict[str, Any], seen_tool_calls: Set[str]) -> str | None:
        """
        Formats an AI message event into an SSE-compatible string.

        Args:
            value (Dict[str, Any]): The AI message event.
            seen_tool_calls (Set[str]): A set of tool call IDs that have already been processed.

        Returns:
            str | None: The formatted SSE string, or None if the event should be ignored.
        """
        ai_message = value.get("messages", [])[-1]
        if isinstance(ai_message, AIMessage):
            if ai_message.content:
                chunk = {"type": "token", "content": ai_message.content}
                return f"data: {json.dumps(chunk)}\n\n"
            if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
                tool_call = ai_message.tool_calls[0]
                tool_call_id = tool_call.get('id')
                if tool_call_id and tool_call_id not in seen_tool_calls:
                    seen_tool_calls.add(tool_call_id)
                    chunk = {
                        "type": "tool_start",
                        "id": tool_call_id,
                        "name": tool_call.get('name', 'unknown'),
                        "args": tool_call.get('args', {})
                    }
                    return f"data: {json.dumps(chunk)}\n\n"
        return None

    def _format_tool_message(self, value: Dict[str, Any]) -> str | None:
        """
        Formats a tool message event into an SSE-compatible string.

        Args:
            value (Dict[str, Any]): The tool message event.

        Returns:
            str | None: The formatted SSE string, or None if the event should be ignored.
        """
        tool_message = value.get("messages", [])[-1]
        if isinstance(tool_message, ToolMessage):
            chunk = {
                "type": "tool_end",
                "tool_call_id": tool_message.tool_call_id,
                "name": tool_message.name,
                "output": tool_message.content
            }
            return f"data: {json.dumps(chunk)}\n\n"
        return None
