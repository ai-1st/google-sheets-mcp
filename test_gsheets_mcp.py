import pytest
from fastmcp import Client
from gsheets_mcp import mcp

@pytest.mark.asyncio
async def test_create_google_sheet():
    async with Client(mcp) as client:
        # Test with minimal valid input
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Test Sheet",
                "data": [["Name", "Age"], ["Alice", 30]]
            }
        )
        assert result.json["status"] == "success"
        assert "url" in result.json

        # Test with formulas
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Test Sheet with Formulas",
                "data": [["A", "B"], [1, 2], [3, 4]],
                "formulas": {"C1": "=SUM(A2:A3)", "C2": "=AVERAGE(B2:B3)"}
            }
        )
        assert result.json["status"] == "success"
        assert "url" in result.json

        # Test error handling with invalid data
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Invalid Sheet",
                "data": "not a list"  # Invalid data format
            }
        )
        assert result.json["status"] == "error"
