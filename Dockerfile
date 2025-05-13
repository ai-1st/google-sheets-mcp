FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gsheets_mcp.py .

# Copy credentials
COPY google_creds.json .

# Run the MCP server
CMD ["fastmcp", "run", "gsheets_mcp.py"]
