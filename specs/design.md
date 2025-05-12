# Google Sheet MCP Tool Design

## Input Structure

The MCP tool, which we'll call `create_google_sheet`, accepts a JSON object with the following fields:

- **title** (required): A string that sets the name of the Google Sheet.

- **data** (required): A list of lists, where each inner list represents a row in the spreadsheet. Each element can be a string, number, or boolean, corresponding to cell values.

- **formulas** (optional): A dictionary where keys are cell references in A1 notation (e.g., "B4") and values are formula strings (e.g., "=SUM(B2:B3)").

- **share_with** (optional): A string representing an email address with which to share the spreadsheet (with writer permissions).

### Example Input

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

### Explanation:

- **title**: Names the spreadsheet "My Spreadsheet".

- **data**: Defines a table with headers "Name" and "Age", followed by two rows of data.

- **formulas**: Adds a sum of ages in cell B4 and an average in C4.

- **share_with**: Shares the spreadsheet with "user@example.com".

## Functionality

The `create_google_sheet` tool performs these steps:

1. **Create the Spreadsheet**: Uses the title to create a new Google Sheet via the gspread library.
2. **Insert Data**: Populates the first worksheet starting at cell A1 with the data.
3. **Apply Formulas**: For each entry in formulas, converts the A1 notation (e.g., "B4") to row and column indices and sets the formula in the specified cell.
4. **Share the Spreadsheet**: If share_with is provided, shares the spreadsheet with that email address, granting writer permissions.
5. **Return the URL**: Provides the URL of the created spreadsheet.

### How It Works with the Example

1. Creates a Google Sheet named "My Spreadsheet".
2. Inserts the data into A1:B3:

   | Name  | Age |
   |-------|-----|
   | Alice | 30  |
   | Bob   | 25  |

3. Sets B4 to `=SUM(B2:B3)` (result: 55) and C4 to `=AVERAGE(B2:B3)` (result: 27.5).
4. Shares the spreadsheet with "user@example.com" as a writer.
5. Returns the spreadsheet's URL.

## Output

The tool returns a JSON object with the following fields:

- **status**: A string indicating success or failure ("success" or "error").

- **message**: A string describing the outcome (e.g., "Spreadsheet created successfully").

- **url**: The URL of the created spreadsheet (if successful).

### Example Output

```json
{
  "status": "success",
  "message": "Spreadsheet created successfully",
  "url": "https://docs.google.com/spreadsheets/d/abc123"
}
```

### Error Example

If the input is invalid (e.g., data isn't a list of lists):

```json
{
  "status": "error",
  "message": "Invalid data format"
}
```

## Additional Details

- **Authentication**: The tool uses a Google service account to create the spreadsheet. The service account owns the sheet, but sharing it with the share_with email ensures user access.

- **Cell References**: Formulas use A1 notation (e.g., "A1", "B4"), which is converted to row and column numbers for gspread.

- **Starting Point**: Data is inserted starting at A1, keeping it simple and predictable.

- **Permissions**: The share_with email, if provided, gets writer access by default.

## Why This Design?

- **Simplicity**: The structure is straightforward—required fields (title, data) ensure the basic spreadsheet is created, while optional fields (formulas, share_with) add flexibility.

- **Clarity**: Separating data and formulas avoids confusion and allows formulas in any cell, not just within the data range.

- **Accessibility**: Sharing via email and returning the URL ensures the user can immediately use the spreadsheet.

This MCP tool fully satisfies your request for a Google Sheet with a title, data, optional formulas, and optional sharing. If you'd like to adjust any aspect (e.g., adding multiple emails for sharing or specifying a worksheet name), let me know, and we can refine it further!

