# Google Sheets MCP Tool

A Model Context Protocol (MCP) tool for creating and manipulating Google Sheets.

## Overview

This tool allows AI assistants and other MCP clients to create Google Sheets with specified:
- Title
- Data (as lists of lists)
- Formulas
- Sharing permissions

The tool returns the URL of the created sheet, making it easy for users to access their newly created spreadsheets.

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Google API Setup

To use this tool, you need to set up Google API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create a service account
5. Download the service account key as JSON
6. Save the key as `google_creds.json` in the project directory or set the `GOOGLE_CREDS_FILE` environment variable to point to your credentials file

## Usage

### Running the Server

```bash
python gsheets_mcp.py
```

### Using the Tool

The `create_google_sheet` tool accepts the following parameters:

- `title` (required): Name of the spreadsheet
- `data` (required): List of lists containing the data
- `formulas` (optional): Dictionary of cell references to formulas
- `share_with` (optional): Email address to share the spreadsheet with

Example input:

```json
{
  "title": "My Spreadsheet",
  "data": [
    ["Name", "Age"],
    ["Alice", 30],
    ["Bob", 25]
  ],
  "formulas": {
    "B4": "=SUM(B2:B3)",
    "C4": "=AVERAGE(B2:B3)"
  },
  "share_with": "user@example.com"
}
```

Example output:

```json
{
  "status": "success",
  "message": "Spreadsheet created successfully",
  "url": "https://docs.google.com/spreadsheets/d/abc123"
}
```

## Testing

Run the tests with pytest:

```bash
pytest
```

## License

MIT
