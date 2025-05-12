#!/usr/bin/env python
"""
Example script demonstrating how to use the Google Sheets MCP tool.
"""
import asyncio
import json
from fastmcp import Client

async def main():
    """Run the example."""
    # Connect to the MCP server (assuming it's running)
    # For a real application, you might want to specify the transport and endpoint
    async with Client("localhost") as client:
        
        # Example 1: Create a simple spreadsheet with just data
        print("\n--- Example 1: Simple Spreadsheet ---")
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Sample Spreadsheet",
                "data": [
                    ["Name", "Department", "Salary"],
                    ["John Doe", "Engineering", 85000],
                    ["Jane Smith", "Marketing", 75000],
                    ["Bob Johnson", "Finance", 90000]
                ]
            }
        )
        
        print(f"Result: {json.dumps(result.json, indent=2)}")
        
        if result.json.get("status") == "success":
            print(f"Spreadsheet created! URL: {result.json.get('url')}")
        
        # Example 2: Create a spreadsheet with formulas
        print("\n--- Example 2: Spreadsheet with Formulas ---")
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Budget Tracker",
                "data": [
                    ["Month", "Income", "Expenses", "Savings"],
                    ["January", 5000, 3500, ""],
                    ["February", 5200, 3700, ""],
                    ["March", 5100, 3600, ""],
                    ["April", 5300, 3800, ""],
                    ["", "Total:", "", ""]
                ],
                "formulas": {
                    "D2": "=B2-C2",
                    "D3": "=B3-C3",
                    "D4": "=B4-C4",
                    "D5": "=B5-C5",
                    "B6": "=SUM(B2:B5)",
                    "C6": "=SUM(C2:C5)",
                    "D6": "=SUM(D2:D5)"
                }
            }
        )
        
        print(f"Result: {json.dumps(result.json, indent=2)}")
        
        # Example 3: Create and share a spreadsheet
        print("\n--- Example 3: Shared Spreadsheet ---")
        result = await client.call_tool(
            "create_google_sheet",
            {
                "title": "Team Project Tracker",
                "data": [
                    ["Task", "Assigned To", "Due Date", "Status"],
                    ["Research", "Alice", "2025-05-20", "In Progress"],
                    ["Design", "Bob", "2025-05-25", "Not Started"],
                    ["Development", "Charlie", "2025-06-05", "Not Started"],
                    ["Testing", "Diana", "2025-06-10", "Not Started"]
                ],
                "share_with": "team-lead@example.com"  # Replace with a real email for testing
            }
        )
        
        print(f"Result: {json.dumps(result.json, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
