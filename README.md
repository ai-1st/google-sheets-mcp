# Google Sheets MCP Tool

A Model Context Protocol (MCP) tool for creating and manipulating Google Sheets.

## Overview

This tool allows AI assistants and other MCP clients to create and manipulate Google Sheets with specified:
- Title
- Data (as lists of lists)
- Formulas
- Formatting (basic filter, bold headers, frozen rows)
- Sharing permissions

The tool returns the URL of the created or updated sheet, making it easy for users to access their spreadsheets.

## Features

- Create new Google Sheets
- Update existing sheets with data and formulas
- Retrieve data from Google Sheets
- List all accessible Google Sheets with pagination and filtering options
- Automatic handling of API rate limiting with exponential backoff

## Docker Installation (Recommended)

1. Clone this repository
2. Set up Google API credentials (see below)
3. Place your `google_creds.json` file in the same directory as the Dockerfile
4. Build the Docker container:
   ```bash
   docker build -t google-sheets-mcp .
   ```
5. Update your `mcp_config.json` file to include the Google Sheets MCP:
   ```json
   {
     "Google Sheets MCP": {
       "command": "docker",
       "args": ["run", "--rm", "-i", "-q", "--network", "none", "google-sheets-mcp"]
     }
   }
   ```

## Google Service Account Setup

To use this tool, you need to set up a Google Service Account with access to Google Sheets and Drive APIs:

1. **Go to Google Cloud Console**
   - Open your web browser and go to [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account
   - Create a new Google Cloud project (e.g., name it "GoogleSheetsMCP")

2. **Enable Required APIs**
   - In the Google Cloud Console, click the Navigation Menu (☰) in the top-left corner
   - Go to APIs & Services > Library
   - Search for and enable the following APIs:
     - Google Sheets API
     - Google Drive API

3. **Create a Service Account**
   - From the Navigation Menu, go to IAM & Admin > Service Accounts
   - Click + Create Service Account at the top
   - Fill in:
     - Service account name: Choose a name (e.g., "sheets-mcp-service")
     - Service account ID: This auto-fills based on the name
     - Description: Optional, add a note if you want
   - Click Create and Continue
   - You may skip role assignment for basic use by clicking Continue
   - Click Done

4. **Create and Download the Credentials (Key)**
   - In the Service Accounts list, find your new service account and click on it
   - Go to the Keys tab
   - Click Add Key > Create new key
   - Choose JSON as the key type and click Create
   - A JSON file will download automatically to your computer
   - Rename this file to `google_creds.json` and place it in the project directory

5. **Share Google Sheets with the Service Account**
   - The service account has an email address (found in the service account details or in the JSON file)
   - When creating sheets through the API, you can share them with specific users
   - For existing sheets you want to access, you need to manually share them with the service account's email

## Usage

### Available Tools

The Google Sheets MCP provides the following tools:

1. **create_google_sheet**
   - Create a new Google Sheet with a title and share it with a specified email

2. **update_google_sheet**
   - Update an existing Google Sheet with data and formulas
   - Apply formatting like basic filters, bold headers, and frozen rows

3. **get_google_sheet**
   - Retrieve all data from a Google Sheet

4. **list_google_sheets**
   - List all Google Sheets accessible to the service account
   - Filter by title or folder
   - Paginate results

### Example Usage

To get a source of tabular data, we'll use "AWS Pricing MCP" tool:
   ```json
   {
    "AWS EC2 Pricing MCP": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-q", "--network", "none", "ai1st/aws-pricing-mcp"]
    }
   }
   ```

Example prompt:

```
Create a sheet with 10 cheapest ec2 instances having at least 32Gb RAM and share it with my-email@domain.com. Include a column with 3-yr costs prodfuced by a formula.
```

## License

MIT
