import os
from typing import List, Dict, Optional, Union
import gspread
from fastmcp import FastMCP, Context
from oauth2client.service_account import ServiceAccountCredentials

# Initialize FastMCP server
mcp = FastMCP("Google Sheets MCP")

def init_gspread_client():
    """Initialize and return a gspread client using service account credentials"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds_file = os.getenv('GOOGLE_CREDS_FILE', 'google_creds.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    return gspread.authorize(credentials)

@mcp.tool()
async def create_google_sheet(
    title: str,
    data: List[List[Union[str, int, float, bool]]],
    formulas: Optional[Dict[str, str]] = None,
    share_with: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, str]:
    """Create a Google Sheet with the specified data and formulas.
    
    Args:
        title: Name of the spreadsheet
        data: List of lists containing the data
        formulas: Dictionary of cell references to formulas
        share_with: Email address to share the spreadsheet with
        ctx: MCP context
    
    Returns:
        Dictionary containing status, message and spreadsheet URL
    """
    try:
        # Initialize client
        gc = init_gspread_client()
        
        # Create new spreadsheet
        if ctx:
            await ctx.info(f"Creating spreadsheet '{title}'...")
        
        sh = gc.create(title)
        worksheet = sh.sheet1
        
        # Update data
        if ctx:
            await ctx.info("Populating data...")
        
        worksheet.update('A1', data)
        
        # Apply formulas if provided
        if formulas:
            if ctx:
                await ctx.info("Applying formulas...")
            
            for cell_ref, formula in formulas.items():
                worksheet.update_acell(cell_ref, formula)
        
        # Share if email provided
        if share_with:
            if ctx:
                await ctx.info(f"Sharing spreadsheet with {share_with}...")
            
            sh.share(share_with, perm_type='user', role='writer')
        
        url = f"https://docs.google.com/spreadsheets/d/{sh.id}"
        
        return {
            "status": "success",
            "message": "Spreadsheet created successfully",
            "url": url
        }
        
    except Exception as e:
        error_msg = str(e)
        if ctx:
            await ctx.error(f"Error creating spreadsheet: {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    mcp.run()
