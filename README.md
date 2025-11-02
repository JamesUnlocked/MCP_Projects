# PostgreSQL MCP Server

A Model Context Protocol (MCP) server that enables Claude Desktop to interact with your local PostgreSQL database through natural language queries.

## Features

- **Execute SQL Queries**: Run read-only SELECT queries safely
- **Database Exploration**: List tables and inspect schemas
- **Table Description**: Get detailed column information and constraints
- **Sample Data**: Preview table contents without full queries
- **Multiple Output Formats**: Markdown tables or JSON for different use cases
- **Safety First**: Read-only operations prevent accidental data modification

## 🪟 Quick Start for Windows 11

1. **Save the files** to a folder, e.g., `C:\Users\YourUsername\postgres-mcp\`

2. **Open Command Prompt** in that folder and run:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Copy `.env.example` to `.env`** and edit with your database credentials

4. **Edit Claude Desktop config** at:
   ```
   C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
   ```
   
   Add this (with YOUR actual paths):
   ```json
   {
     "mcpServers": {
       "postgres": {
         "command": "C:\\Users\\YourUsername\\postgres-mcp\\venv\\Scripts\\python.exe",
         "args": ["C:\\Users\\YourUsername\\postgres-mcp\\postgres_mcp.py"],
         "env": {
           "POSTGRES_HOST": "localhost",
           "POSTGRES_PORT": "5432",
           "POSTGRES_DB": "your_database",
           "POSTGRES_USER": "postgres",
           "POSTGRES_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

5. **Restart Claude Desktop** completely (Quit and reopen)

6. **Look for the 🔌 icon** in Claude Desktop - you're connected!

## Prerequisites

- Python 3.10 or higher
- PostgreSQL database running locally or remotely
- Claude Desktop application

## Installation

### 1. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
# source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the same directory as `postgres_mcp.py`:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

**Security Note**: Never commit your `.env` file to version control. Add it to `.gitignore`.

### 3. Test the Server

Verify your server works before connecting to Claude Desktop:

```bash
# Test that the file has no syntax errors
python -m py_compile postgres_mcp.py

# The server is ready if no errors appear
```

## Configuring Claude Desktop

### 1. Locate Your Claude Desktop Config

**For Windows 11**, the configuration file is located at:
```
%APPDATA%\Claude\claude_desktop_config.json
```

This typically expands to:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

**Other OS locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add Your MCP Server

Edit the config file to add your PostgreSQL MCP server.

**For Windows 11**, your configuration will look like this:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "C:\\Users\\YourUsername\\postgres-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YourUsername\\postgres-mcp\\postgres_mcp.py"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "your_database_name",
        "POSTGRES_USER": "your_username",
        "POSTGRES_PASSWORD": "your_password"
      }
    }
  }
}
```

**Important**: Replace the paths and credentials with your actual values:
- `C:\\Users\\YourUsername\\postgres-mcp\\venv\\Scripts\\python.exe` → Full path to your virtual environment's Python
- `C:\\Users\\YourUsername\\postgres-mcp\\postgres_mcp.py` → Full path to the server script
- Note the double backslashes (`\\`) in Windows paths for JSON

**Complete Example for Windows 11**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "C:\\Users\\John\\Documents\\postgres-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\John\\Documents\\postgres-mcp\\postgres_mcp.py"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "secretpassword"
      }
    }
  }
}
```

**Example for macOS/Linux**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "/Users/yourname/projects/postgres-mcp/venv/bin/python",
      "args": ["/Users/yourname/projects/postgres-mcp/postgres_mcp.py"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "secretpassword"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After saving the configuration:
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Look for the 🔌 icon indicating MCP servers are connected

## Usage Examples

Once configured, you can ask Claude to interact with your database:

### Explore Your Database
```
"What tables are in my database?"
"Show me the structure of the users table"
"Give me a sample of 20 rows from the orders table"
```

### Query Your Data
```
"How many users signed up in the last month?"
"Show me the top 10 products by sales"
"Find all orders with status 'pending' from the last week"
"What's the average order value by customer segment?"
```

### Complex Analysis
```
"Analyze customer retention rates by cohort"
"Which products have the highest return rate?"
"Show me sales trends over the last 6 months"
```

## Available Tools

The MCP server provides these tools to Claude:

1. **postgres_execute_query**: Execute any SELECT query
2. **postgres_list_tables**: List all tables in a schema
3. **postgres_describe_table**: Get table structure and constraints
4. **postgres_get_table_sample**: Preview table data

All tools support both Markdown (human-readable) and JSON (machine-readable) output formats.

## Security Features

- **Read-Only Operations**: Only SELECT queries are allowed
- **Query Validation**: Blocks INSERT, UPDATE, DELETE, DROP, etc.
- **Error Handling**: Clear, actionable error messages
- **Connection Pooling**: Efficient database connection management

## Troubleshooting

### Claude Desktop doesn't show the MCP server

1. Check that the config file is valid JSON (use a JSON validator)
2. Verify all paths are absolute paths, not relative
3. Ensure your virtual environment's Python path is correct
4. Check Claude Desktop logs for error messages

### "Connection refused" errors

1. Verify PostgreSQL is running: `psql -U your_username -d your_database`
2. Check your connection credentials in the config
3. Ensure PostgreSQL accepts connections from localhost

### "Table not found" errors

1. Verify the table exists: Ask Claude to list tables first
2. Check you're using the correct schema (default is 'public')
3. Ensure your user has SELECT permissions on the table

### Python module errors

1. Ensure you're using the virtual environment's Python
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python version: `python --version` (should be 3.10+)

## Advanced Configuration

### Custom Response Limits

Adjust the character limit for large result sets by modifying the constant in `postgres_mcp.py`:

```python
CHARACTER_LIMIT = 25000  # Increase or decrease as needed
```

### Connection Pool Settings

Customize the database connection pool in the `database_lifespan` function:

```python
pool = await asyncpg.create_pool(
    # ... other params ...
    min_size=2,   # Minimum connections
    max_size=10   # Maximum connections
)
```

## Development

### Adding New Tools

To add a new tool to the server:

1. Define a Pydantic model for input validation
2. Create the tool function with `@mcp.tool()` decorator
3. Add comprehensive docstrings
4. Handle errors gracefully

Example:
```python
class NewToolInput(BaseModel):
    param: str = Field(..., description="Parameter description")

@mcp.tool(name="postgres_new_tool")
async def new_tool(params: NewToolInput, ctx) -> str:
    """Tool description."""
    # Implementation
    pass
```

## License

This MCP server is provided as-is for personal and commercial use.

## Support

For issues specific to this MCP server, review the troubleshooting section above.

For general MCP protocol questions, visit: https://modelcontextprotocol.io
For Claude Desktop support, visit: https://support.claude.com

## Credits

Built using:
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- [asyncpg](https://github.com/MagicStack/asyncpg)
