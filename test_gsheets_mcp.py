import asyncio
import json
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

async def run_tests():
    try:
        async with Client(mcp) as client:

            # # Step 1: List Google Sheets with pagination
            # print("\n1c. Listing Google Sheets with pagination (limit=2, offset=0)...")
            # list_paginated_response = await client.call_tool(
            #     "list_google_sheets",
            #     {
            #         "limit": 2,
            #         "offset": 0
            #     },
            #     _return_raw_result=True
            # )

            # # Parse the paginated response
            # list_paginated_data = parse_response(list_paginated_response.content)
            # if not list_paginated_data:
            #     print("Error: Could not parse paginated list response")
            #     return
            
            # print(f"Paginated list response: {list_paginated_data}")
    
            
            # Step 2: Create a Google Sheet
            print("\n2. Creating a new Google Sheet...")
            create_response = await client.call_tool(
                "create_google_sheet",
                {
                    "title": "Test Sheet",
                    "share_with": "dmitry.degtyarev@devfactory.com"
                },
                _return_raw_result=True
            )
            
            # Parse the response
            create_data = parse_response(create_response.content)
            if not create_data:
                print("Error: Could not parse create response")
                return
                
            print(f"Create response: {create_data}")
            
            # Extract the spreadsheet URL
            if "spreadsheet_url" in create_data:
                spreadsheet_url = create_data["spreadsheet_url"]
                print(f"Spreadsheet URL: {spreadsheet_url}")
            else:
                print("Error: Could not get spreadsheet URL from create response")
                return
            
            # Step 2: Update the Google Sheet
            print("\n2. Updating the Google Sheet with data and formulas...")
            update_response = await client.call_tool(
                "update_google_sheet",
                {
                    "spreadsheet_url": spreadsheet_url,
                    "worksheet_name": "Sheet1",  # Specify the worksheet name
                    "data_and_formulas": [
                        ["Name", "Age"],
                        ["Alice", 30],
                        ["Bob", 25],
                        ["Total", "=SUM(B2:B3)"]
                    ]
                },
                _return_raw_result=True
            )
            
            # Parse the response
            update_data = parse_response(update_response.content)
            if not update_data:
                print("Error: Could not parse update response")
                return
                
            print(f"Update response: {update_data}")
            
            # Step 3: Retrieve the Google Sheet data
            print("\n3. Retrieving the Google Sheet data...")
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
                return
                
            print(f"Get response: {get_data}")
            
            # Display the retrieved data
            if "data" in get_data:
                print("\nSheet Data:")
                for row in get_data["data"]:
                    print(row)
            else:
                print("Error: Could not get data from get_google_sheet response")
    
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

# Run the async test function
if __name__ == "__main__":
    asyncio.run(run_tests())