from ai_engine.agent import run_agent, STAFF_TOOLS
from unittest.mock import MagicMock, patch
import pytest
import os

@patch("ai_engine.tools.requests")
def test_search_products_tool(mock_requests):
    # Mock backend response
    mock_response = MagicMock()
    mock_response.json.return_value = [{"name": "Milk", "description": "Dairy", "price": 3.99}]
    mock_requests.get.return_value = mock_response

    from ai_engine.tools import search_products
    result = search_products("milk")

    assert "Milk" in result

    # The tool now uses os.getenv("BACKEND_URL"), which might differ in test env
    # Check what the tool actually called
    expected_url = f"{os.getenv('BACKEND_URL', 'http://backend:8000/api/v1')}/products/"
    mock_requests.get.assert_called_with(expected_url)

@patch("ai_engine.agent.create_react_agent")
def test_agent_run(mock_create_react_agent):
    # Mock the graph returned by create_react_agent
    mock_graph = MagicMock()
    # mock_graph.invoke returns a dict with 'messages'
    mock_message = MagicMock()
    mock_message.content = "I found milk in stock."
    mock_graph.invoke.return_value = {"messages": [MagicMock(), mock_message]}

    mock_create_react_agent.return_value = mock_graph

    response = run_agent("Do we have milk?")
    assert "I found milk" in response
    mock_graph.invoke.assert_called_once()

def test_tool_definitions():
    # Verify staff tools
    assert len(STAFF_TOOLS) >= 3
    tool_names = [t.__name__ for t in STAFF_TOOLS]
    assert "search_products" in tool_names
    assert "check_stock" in tool_names
    assert "agent_create_order" in tool_names
