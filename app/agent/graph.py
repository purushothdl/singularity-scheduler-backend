import operator
from typing import Dict, TypedDict, Annotated, List

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.tools import calendar_tools, search_tools
from app.core.config import settings

# --- Agent State Definition ---
class AgentState(TypedDict):
    """
    Represents the state of our agent. This state is passed between nodes in the graph.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    current_user: Dict

# --- Tool & Model Definition ---

# Collect all the async tools we've built
tools = [
    calendar_tools.confirm_and_book_event,
    calendar_tools.list_events,
    calendar_tools.delete_event,
    calendar_tools.update_user_timezone,
    calendar_tools.update_event,
    calendar_tools.find_available_slots,
    search_tools.search_web,
    search_tools.search_news,
]

# The ToolNode will execute tools when called by the agent
tool_node = ToolNode(tools)

# Define the LLM. Using a specific model and temperature for consistent results.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Bind the tools to the LLM, so it knows what functions it can call
model_with_tools = llm.bind_tools(tools)

# --- Graph Node Definitions ---

def should_continue(state: AgentState) -> str:
    """
    Determines the next step for the agent.
    If the last message has tool calls, it routes to the 'tools' node.
    Otherwise, it ends the conversation turn.
    """
    return "tools" if state["messages"][-1].tool_calls else END

async def call_model(state: AgentState) -> Dict:
    """
    The primary node that calls the LLM.
    It takes the current conversation state and invokes the model.
    """
    # The custom_tool_node injects the user, so we don't pass it to the model directly
    # This prevents the model from trying to hallucinate the user object.
    messages_for_llm = [msg for msg in state['messages'] if msg.type != 'tool' or 'current_user' not in getattr(msg, 'additional_kwargs', {})]
    
    response = await model_with_tools.ainvoke(messages_for_llm)
    return {"messages": [response]}

async def custom_tool_node(state: AgentState):
    """
    A custom tool node that injects the current_user dictionary into
    every tool call's arguments before execution.
    """
    tool_messages = []
    # LangChain can handle async tool execution concurrently
    tool_invocation_tasks = []
    
    for tool_call in state["messages"][-1].tool_calls:
        tool_name = tool_call['name']
        for tool_func in tools:
            if tool_func.name == tool_name:
                # Add current_user to the args for the tool to use
                tool_args = tool_call['args']
                tool_args['current_user'] = state['current_user']
                
                # Invoke the async tool
                result = await tool_func.ainvoke(tool_args)
                
                # Append the result as a ToolMessage
                tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call['id']))
                break
                
    return {"messages": tool_messages}

# --- Graph Assembly ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", custom_tool_node) # Using our custom node

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "agent")

# The final, compiled LangGraph application
agent_app = workflow.compile()