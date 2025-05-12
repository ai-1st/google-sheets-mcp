import os
import time
import functools
from typing import Dict, List, Optional, Union, Callable, Any

import gspread
from fastmcp import FastMCP, Context
from oauth2client.service_account import ServiceAccountCredentials

# Initialize FastMCP server
mcp = FastMCP("Google Sheets MCP")

# Backoff decorator for handling API rate limiting
def backoff_handler(max_retries: int = 5, initial_delay: float = 1.0):
    """Decorator that implements exponential backoff for API calls.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds, will be doubled each retry
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    # Check if it's a rate limit error (429)
                    if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429:
                        last_exception = e
                        # Wait with exponential backoff
                        time.sleep(delay)
                        delay *= 2  # Double the delay for next retry
                    else:
                        # If it's not a rate limit error, re-raise immediately
                        raise
            
            # If we've exhausted all retries, raise the last exception
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator

@backoff_handler(max_retries=5, initial_delay=1.0)
def init_gspread_client():
    """Initialize and return a gspread client using service account credentials"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    creds_file = os.getenv('GOOGLE_CREDS_FILE', os.path.join(script_dir, 'google_creds.json'))
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    return gspread.authorize(credentials)

@mcp.tool()
async def create_google_sheet(
    title: str,
    share_with: str,
    ctx: Context = None
) -> Dict[str, Union[str, List[str]]]:
    """Create a new Google Sheet.
    
    Args:
        title: Name of the spreadsheet
        share_with: Email address to share the spreadsheet with
    
    Returns:
        Dictionary containing status, message and spreadsheet URL
    """
    # Input validation
    validation_errors = []
    
    # Validate title
    if not title or not isinstance(title, str):
        validation_errors.append("Title must be a non-empty string")
    
    # Validate share_with
    if not share_with or not isinstance(share_with, str):
        validation_errors.append("share_with must be a non-empty string with a valid email address")
    
    if validation_errors:
        return {
            "status": "error",
            "message": "; ".join(validation_errors)
        }
    
    try:
        client = init_gspread_client()
        
        # Create a new spreadsheet
        spreadsheet = client.create(title)
        
        # Share the spreadsheet with the provided email
        spreadsheet.share(share_with, perm_type='user', role='writer')
        
        return {
            "status": "success",
            "message": f"Spreadsheet '{title}' created successfully",
            "spreadsheet_url": spreadsheet.url
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating spreadsheet: {str(e)}"
        }

@mcp.tool()
async def update_google_sheet(
    spreadsheet_url: str,
    worksheet_name: Optional[str],
    data_and_formulas: List[List[Union[str, int, float, bool]]],
    ctx: Context = None
) -> Dict[str, Union[str, List[str]]]:
    """Update a Google Sheet with the specified data and formulas.
    
    Args:
        spreadsheet_url: URL of the spreadsheet to update
        worksheet_name: Name of the worksheet to update or create (uses first sheet if None)
        data_and_formulas: List of lists containing the data and formulas. Formulas start with = sign.
    
    Returns:
        Dictionary containing status, message and spreadsheet URL
    """
    # Input validation
    validation_errors = []
    
    # Validate spreadsheet_url
    if not spreadsheet_url or not isinstance(spreadsheet_url, str):
        validation_errors.append("spreadsheet_url must be a non-empty string")
    
    # Validate data
    if not data_and_formulas:
        validation_errors.append("Data must not be empty")
    elif not isinstance(data_and_formulas, list):
        validation_errors.append("Data must be a list of lists")
    else:
        for row in data_and_formulas:
            if not isinstance(row, list):
                validation_errors.append("Each row in data must be a list")
                break
    
    if validation_errors:
        return {
            "status": "error",
            "message": "; ".join(validation_errors)
        }
    
    try:
        if ctx:
            await ctx.info(f"Opening spreadsheet from URL: {spreadsheet_url}")
        
        client = init_gspread_client()
        
        # Open the spreadsheet by URL
        try:
            spreadsheet = client.open_by_url(spreadsheet_url)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not open spreadsheet: {str(e)}"
            }
        
        # Get or create the specified worksheet
        if worksheet_name:
            if ctx:
                await ctx.info(f"Looking for worksheet: {worksheet_name}")
            
            # Try to get the worksheet by name
            worksheet = None
            for ws in spreadsheet.worksheets():
                if ws.title == worksheet_name:
                    worksheet = ws
                    break
            
            # Create it if it doesn't exist
            if not worksheet:
                if ctx:
                    await ctx.info(f"Creating new worksheet: {worksheet_name}")
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, 
                                                     rows=len(data_and_formulas), 
                                                     cols=len(data_and_formulas[0]) if data_and_formulas and data_and_formulas[0] else 1)
        else:
            # Use the first worksheet
            worksheet = spreadsheet.get_worksheet(0)
            if ctx:
                await ctx.info(f"Using first worksheet: {worksheet.title}")
        
        # Update the worksheet with data
        if ctx:
            await ctx.info(f"Updating worksheet with {len(data_and_formulas)} rows of data")
        
        # Process data to handle formulas correctly
        # We need to separate regular data from formulas
        regular_data = []
        formulas = {}
        
        # First pass: collect regular data and identify formulas
        for row_idx, row in enumerate(data_and_formulas):
            new_row = []
            for col_idx, cell_value in enumerate(row):
                # Check if the cell value is a formula (starts with '=')
                if isinstance(cell_value, str) and cell_value.startswith('='):
                    # Convert to A1 notation (e.g., A1, B2, etc.)
                    col_letter = chr(65 + col_idx)  # A, B, C, etc.
                    cell_ref = f"{col_letter}{row_idx+1}"
                    formulas[cell_ref] = cell_value
                    # Use a placeholder in the regular data
                    new_row.append('')
                else:
                    new_row.append(cell_value)
            regular_data.append(new_row)
        
        # Apply backoff to worksheet update
        @backoff_handler(max_retries=5, initial_delay=1.0)
        def update_worksheet_data(worksheet, data):
            return worksheet.update(data)
        
        # Update with regular data first
        update_worksheet_data(worksheet, regular_data)
        
        # Then apply formulas if there are any
        if formulas:
            if ctx:
                await ctx.info(f"Applying {len(formulas)} formulas")
            
            # Apply backoff to formula updates
            @backoff_handler(max_retries=3, initial_delay=1.0)
            def update_cell_formula(worksheet, cell_ref, formula):
                return worksheet.update_acell(cell_ref, formula)
            
            formula_errors = []
            for cell_ref, formula in formulas.items():
                try:
                    update_cell_formula(worksheet, cell_ref, formula)
                except Exception as formula_error:
                    error_msg = f"Error applying formula to {cell_ref}: {str(formula_error)}"
                    formula_errors.append(error_msg)
                    if ctx:
                        await ctx.warning(error_msg)
            
            if formula_errors and len(formula_errors) == len(formulas):
                return {
                    "status": "partial_success",
                    "message": f"Data updated but all formulas failed: {'; '.join(formula_errors)}",
                    "spreadsheet_url": spreadsheet.url
                }
            elif formula_errors:
                return {
                    "status": "partial_success",
                    "message": f"Data updated but some formulas failed: {'; '.join(formula_errors)}",
                    "spreadsheet_url": spreadsheet.url
                }
        
        return {
            "status": "success",
            "message": f"Spreadsheet updated successfully",
            "spreadsheet_url": spreadsheet.url
        }
        
    except Exception as e:
        error_msg = f"Error updating spreadsheet: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        
        return {
            "status": "error",
            "message": error_msg
        }

@mcp.tool()
async def get_google_sheet(
    spreadsheet_url: str,
    worksheet_name: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Union[str, List[List[Union[str, int, float, bool]]]]]: 
    """Get a Google Sheet by URL.
    
    Args:
        spreadsheet_url: URL of the spreadsheet to get
        worksheet_name: Name of the worksheet to get. If None, the first worksheet will be returned
    
    Returns:
        Dictionary containing the data from the worksheet
    """
    # Input validation
    validation_errors = []
    
    # Validate spreadsheet_url
    if not spreadsheet_url or not isinstance(spreadsheet_url, str):
        validation_errors.append("spreadsheet_url must be a non-empty string")
    
    if validation_errors:
        return {
            "status": "error",
            "message": "; ".join(validation_errors)
        }
    
    try:
        if ctx:
            await ctx.info(f"Opening spreadsheet from URL: {spreadsheet_url}")
        
        client = init_gspread_client()
        
        # Open the spreadsheet by URL
        try:
            spreadsheet = client.open_by_url(spreadsheet_url)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not open spreadsheet: {str(e)}"
            }
        
        # Get the specified worksheet or the first one
        if worksheet_name:
            if ctx:
                await ctx.info(f"Looking for worksheet: {worksheet_name}")
            
            # Try to get the worksheet by name
            worksheet = None
            for ws in spreadsheet.worksheets():
                if ws.title == worksheet_name:
                    worksheet = ws
                    break
            
            if not worksheet:
                return {
                    "status": "error",
                    "message": f"Worksheet '{worksheet_name}' not found"
                }
        else:
            # Use the first worksheet
            worksheet = spreadsheet.get_worksheet(0)
            if ctx:
                await ctx.info(f"Using first worksheet: {worksheet.title}")
        
        # Get all values from the worksheet
        if ctx:
            await ctx.info(f"Retrieving data from worksheet")
        
        # Apply backoff to worksheet data retrieval
        @backoff_handler(max_retries=5, initial_delay=1.0)
        def get_worksheet_data(worksheet):
            return worksheet.get_all_values()
        
        data = get_worksheet_data(worksheet)
        
        return {
            "status": "success",
            "message": f"Spreadsheet data retrieved successfully",
            "data": data,
            "spreadsheet_url": spreadsheet.url,
            "worksheet_name": worksheet.title
        }
        
    except Exception as e:
        error_msg = f"Error retrieving spreadsheet data: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    mcp.run()
