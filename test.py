#!/usr/bin/env python
"""
Example script demonstrating how to use the Google Sheets MCP tools.

This script provides examples of creating, updating, and retrieving Google Sheets
using the Model Context Protocol (MCP). It demonstrates various operations such as:

1. Creating a simple spreadsheet with data
2. Creating a spreadsheet with formulas
3. Creating and sharing a spreadsheet with a specific email
4. Listing all accessible Google Sheets
5. Retrieving data from a Google Sheet

Usage:
    python test.py --email user@example.com [--examples 1,2,3]

Options:
    --email     Email address to share spreadsheets with (required)
    --examples  Comma-separated list of example numbers to run (default: all)
                Available examples: 1, 2, 3, 4, 5

Example:
    python test.py --email user@example.com --examples 1,3,5
"""
import asyncio
import argparse
import json
import re
import sys
from fastmcp import Client
from gsheets_mcp import mcp


def parse_response(response):
    """Parse the response from the MCP client.
    
    The response is a list of TextContent objects, and we need to extract the JSON string
    from it and parse it into a Python dictionary.
    """
    if isinstance(response, list) and len(response) > 0:
        # Extract the text from the first TextContent object
        text = response[0].text
        try:
            # Parse the JSON string into a Python dictionary
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Text content: {text}")
    return None


def is_valid_email(email):
    """Check if the provided email address is valid."""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))


async def run_example_1(client, email):
    """Run Example 1: Create a simple spreadsheet with data."""
    print("\n--- Example 1: Simple Spreadsheet ---")
    
    # Create the spreadsheet
    create_response = await client.call_tool(
        "create_google_sheet",
        {
            "title": "Sample Spreadsheet",
            "share_with": email
        },
        _return_raw_result=True
    )
    
    # Parse the response
    create_data = parse_response(create_response.content)
    if not create_data:
        print("Error: Could not parse create response")
        return None
        
    print(f"Create response: {json.dumps(create_data, indent=2)}")
    
    # Extract the spreadsheet URL
    if "spreadsheet_url" in create_data:
        spreadsheet_url = create_data["spreadsheet_url"]
        print(f"Spreadsheet URL: {spreadsheet_url}")
    else:
        print("Error: Could not get spreadsheet URL from create response")
        return None
    
    # Update the spreadsheet with data
    print("\nUpdating the spreadsheet with data...")
    update_response = await client.call_tool(
        "update_google_sheet",
        {
            "spreadsheet_url": spreadsheet_url,
            "worksheet_name": None,  # Use default worksheet
            "data_and_formulas": [
                ["Name", "Department", "Salary"],
                ["John Doe", "Engineering", 85000],
                ["Jane Smith", "Marketing", 75000],
                ["Bob Johnson", "Finance", 90000]
            ],
            "set_basic_filter": True,
            "freeze_rows": 1,
            "set_bold_header": True
        },
        _return_raw_result=True
    )
    
    # Parse the response
    update_data = parse_response(update_response.content)
    if not update_data:
        print("Error: Could not parse update response")
        return None
        
    print(f"Update response: {json.dumps(update_data, indent=2)}")
    
    return spreadsheet_url


async def run_example_2(client, email):
    """Run Example 2: Create a spreadsheet with formulas."""
    print("\n--- Example 2: Spreadsheet with Formulas ---")
    
    # Create the spreadsheet
    create_response = await client.call_tool(
        "create_google_sheet",
        {
            "title": "Budget Tracker",
            "share_with": email
        },
        _return_raw_result=True
    )
    
    # Parse the response
    create_data = parse_response(create_response.content)
    if not create_data:
        print("Error: Could not parse create response")
        return None
        
    print(f"Create response: {json.dumps(create_data, indent=2)}")
    
    # Extract the spreadsheet URL
    if "spreadsheet_url" in create_data:
        spreadsheet_url = create_data["spreadsheet_url"]
        print(f"Spreadsheet URL: {spreadsheet_url}")
    else:
        print("Error: Could not get spreadsheet URL from create response")
        return None
    
    # Update with data and formulas
    print("\nUpdating with data and formulas...")
    update_response = await client.call_tool(
        "update_google_sheet",
        {
            "spreadsheet_url": spreadsheet_url,
            "worksheet_name": None,  # Use default worksheet
            "data_and_formulas": [
                ["Month", "Income", "Expenses", "Savings"],
                ["January", 5000, 3500, "=B2-C2"],
                ["February", 5200, 3700, "=B3-C3"],
                ["March", 5100, 3600, "=B4-C4"],
                ["April", 5300, 3800, "=B5-C5"],
                ["", "=SUM(B2:B5)", "=SUM(C2:C5)", "=SUM(D2:D5)"]
            ],
            "set_basic_filter": True,
            "freeze_rows": 1,
            "set_bold_header": True
        },
        _return_raw_result=True
    )
    
    # Parse the response
    update_data = parse_response(update_response.content)
    if not update_data:
        print("Error: Could not parse update response")
        return None
        
    print(f"Update response: {json.dumps(update_data, indent=2)}")
    
    return spreadsheet_url


async def run_example_3(client, email):
    """Run Example 3: Create and share a spreadsheet."""
    print("\n--- Example 3: Shared Spreadsheet ---")
    
    # Create and share the spreadsheet
    create_response = await client.call_tool(
        "create_google_sheet",
        {
            "title": "Team Project Tracker",
            "share_with": email
        },
        _return_raw_result=True
    )
    
    # Parse the response
    create_data = parse_response(create_response.content)
    if not create_data:
        print("Error: Could not parse create response")
        return None
        
    print(f"Create response: {json.dumps(create_data, indent=2)}")
    
    # Extract the spreadsheet URL
    if "spreadsheet_url" in create_data:
        spreadsheet_url = create_data["spreadsheet_url"]
        print(f"Spreadsheet URL: {spreadsheet_url}")
    else:
        print("Error: Could not get spreadsheet URL from create response")
        return None
    
    # Update with data
    print("\nUpdating with data...")
    update_response = await client.call_tool(
        "update_google_sheet",
        {
            "spreadsheet_url": spreadsheet_url,
            "worksheet_name": None,  # Use default worksheet
            "data_and_formulas": [
                ["Task", "Assigned To", "Due Date", "Status"],
                ["Research", "Alice", "2025-05-20", "In Progress"],
                ["Design", "Bob", "2025-05-25", "Not Started"],
                ["Development", "Charlie", "2025-06-05", "Not Started"],
                ["Testing", "Diana", "2025-06-10", "Not Started"]
            ],
            "set_basic_filter": True,
            "freeze_rows": 1,
            "set_bold_header": True
        },
        _return_raw_result=True
    )
    
    # Parse the response
    update_data = parse_response(update_response.content)
    if not update_data:
        print("Error: Could not parse update response")
        return None
        
    print(f"Update response: {json.dumps(update_data, indent=2)}")
    
    return spreadsheet_url


async def run_example_4(client):
    """Run Example 4: List all Google Sheets."""
    print("\n--- Example 4: List Google Sheets ---")
    
    list_response = await client.call_tool(
        "list_google_sheets",
        {
            "limit": 10,
            "offset": 0
        },
        _return_raw_result=True
    )
    
    # Parse the response
    list_data = parse_response(list_response.content)
    if not list_data:
        print("Error: Could not parse list response")
        return None
        
    print(f"List response: {json.dumps(list_data, indent=2)}")
    
    return True


async def run_example_5(client, spreadsheet_url):
    """Run Example 5: Get data from a Google Sheet."""
    print("\n--- Example 5: Get Google Sheet Data ---")
    
    if not spreadsheet_url:
        print("Error: No spreadsheet URL available for Example 5")
        return None
    
    get_response = await client.call_tool(
        "get_google_sheet",
        {
            "spreadsheet_url": spreadsheet_url
        },
        _return_raw_result=True
    )
    
    # Parse the response
    get_data = parse_response(get_response.content)
    if not get_data:
        print("Error: Could not parse get response")
        return None
        
    print(f"Get response: {json.dumps(get_data, indent=2)}")
    
    # Display the retrieved data
    if "data" in get_data:
        print("\nSheet Data:")
        for row in get_data["data"]:
            print(row)
    else:
        print("Error: Could not get data from get_google_sheet response")
    
    return True


async def main(email, examples_to_run=None):
    """Run the selected examples.
    
    Args:
        email: Email address to share spreadsheets with
        examples_to_run: List of example numbers to run, or None to run all examples
    """
    # Validate email address
    if not is_valid_email(email):
        print(f"Error: '{email}' is not a valid email address")
        return
    
    try:
        async with Client(mcp) as client:
            # Track the last created spreadsheet URL for Example 5
            last_spreadsheet_url = None
            
            # Run Example 1: Create a simple spreadsheet
            if examples_to_run is None or 1 in examples_to_run:
                last_spreadsheet_url = await run_example_1(client, email)
            
            # Run Example 2: Create a spreadsheet with formulas
            if examples_to_run is None or 2 in examples_to_run:
                sheet_url = await run_example_2(client, email)
                if sheet_url:
                    last_spreadsheet_url = sheet_url
            
            # Run Example 3: Create and share a spreadsheet
            if examples_to_run is None or 3 in examples_to_run:
                sheet_url = await run_example_3(client, email)
                if sheet_url:
                    last_spreadsheet_url = sheet_url
            
            # Run Example 4: List all Google Sheets
            if examples_to_run is None or 4 in examples_to_run:
                await run_example_4(client)
            
            # Run Example 5: Get data from a Google Sheet
            if examples_to_run is None or 5 in examples_to_run:
                await run_example_5(client, last_spreadsheet_url)
                
    except Exception as e:
        print(f"Error during example: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Google Sheets MCP Example Script')
    parser.add_argument('--email', type=str, required=True,
                        help='Email address to share spreadsheets with (required)')
    parser.add_argument('--examples', type=str,
                        help='Comma-separated list of example numbers to run (e.g., "1,3,5")')
    
    args = parser.parse_args()
    
    # Parse examples to run
    examples_to_run = None
    if args.examples:
        try:
            examples_to_run = [int(ex.strip()) for ex in args.examples.split(',')]
            # Validate example numbers
            valid_examples = list(range(1, 6))  # Examples 1-5
            invalid_examples = [ex for ex in examples_to_run if ex not in valid_examples]
            if invalid_examples:
                print(f"Warning: Invalid example numbers: {invalid_examples}")
                print(f"Valid example numbers are: {valid_examples}")
                examples_to_run = [ex for ex in examples_to_run if ex in valid_examples]
        except ValueError:
            print(f"Error: Invalid example format. Please use comma-separated numbers (e.g., '1,3,5')")
            sys.exit(1)
    
    print(f"Using email: {args.email}")
    if examples_to_run:
        print(f"Running examples: {examples_to_run}")
    else:
        print("Running all examples")
        
    asyncio.run(main(args.email, examples_to_run))
