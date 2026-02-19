from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatOllama
from ai_engine.tools import search_products, check_stock, agent_create_order
from typing import Optional, Any
from langchain_core.messages import HumanMessage, BaseMessage

# Tools definition
tools = [search_products, check_stock, agent_create_order]

def get_llm():
    # Default to ChatOllama running locally
    return ChatOllama(model="llama3")

def get_agent_executor(llm: Optional[Any] = None):
    if llm is None:
        llm = get_llm()

    # create_react_agent creates a CompiledGraph
    return create_react_agent(llm, tools)

def run_agent(query: str, llm: Optional[Any] = None):
    agent = get_agent_executor(llm)
    try:
        # invoke returns a dict with 'messages': List[BaseMessage]
        result = agent.invoke({"messages": [HumanMessage(content=query)]})
        messages = result.get("messages", [])
        if messages:
             last_msg = messages[-1]
             return last_msg.content
        return "No response from agent."
    except Exception as e:
        return f"Error running agent: {str(e)}"
