from langgraph.prebuilt import create_react_agent
from langchain_community.chat_models import ChatOllama
from ai_engine.tools import (
    search_products, check_stock, agent_create_order,
    check_expiry_alert, generate_marketing_draft, suggest_recipe_products,
    scan_receipt_text, create_draft_po
)
from ai_engine.prompts import STAFF_SYSTEM_PROMPT, CUSTOMER_SYSTEM_PROMPT
from typing import Optional, Any
from langchain_core.messages import HumanMessage, SystemMessage

# Define Tool Sets
STAFF_TOOLS = [
    search_products, check_stock, agent_create_order,
    check_expiry_alert, generate_marketing_draft,
    scan_receipt_text, create_draft_po
]
CUSTOMER_TOOLS = [search_products, check_stock, suggest_recipe_products]

def get_llm():
    return ChatOllama(model="llama3")

def get_agent_executor(mode: str = "staff", llm: Optional[Any] = None):
    if llm is None:
        llm = get_llm()

    if mode == "customer":
        tools = CUSTOMER_TOOLS
        system_prompt = CUSTOMER_SYSTEM_PROMPT
    else:
        tools = STAFF_TOOLS
        system_prompt = STAFF_SYSTEM_PROMPT

    return create_react_agent(llm, tools, state_modifier=system_prompt)

def run_agent(query: str, mode: str = "staff", llm: Optional[Any] = None):
    """
    Run the agent with the specified mode ('staff' or 'customer').
    """
    agent = get_agent_executor(mode, llm)
    try:
        result = agent.invoke({"messages": [HumanMessage(content=query)]})
        messages = result.get("messages", [])
        if messages:
             last_msg = messages[-1]
             return last_msg.content
        return "No response from agent."
    except Exception as e:
        return f"Error running agent: {str(e)}"
