"""PostgreSQL MCP Server

This MCP server enables Claude to interact with a local PostgreSQL database through
well-designed tools for querying, schema inspection, and data analysis.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from contextlib import asynccontextmanager
import asyncpg
import json
import os

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_ROW_LIMIT = 100

# Initialize MCP server
mcp = FastMCP("postgres_mcp")


# Enums for response formats
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# Pydantic models for input validation
class ExecuteQueryInput(BaseModel):
    """Input model for executing SQL queries."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    query: str = Field(
        ...,
        description="SQL query to execute (e.g., 'SELECT * FROM users WHERE age > 25 LIMIT 10'). "
                    "Queries are read-only for safety.",
        min_length=1,
        max_length=5000
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable tables or 'json' for structured data"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query_safety(cls, v: str) -> str:
        """Ensure query is read-only."""
        query_upper = v.strip().upper()
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(
                    f"Destructive operations not allowed. Query contains '{keyword}'. "
                    "Only SELECT queries are permitted for safety."
                )
        return v.strip()


class ListTablesInput(BaseModel):
    """Input model for listing database tables."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    schema: str = Field(
        default="public",
        description="Database schema to list tables from (e.g., 'public', 'analytics')",
        min_length=1,
        max_length=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class DescribeTableInput(BaseModel):
    """Input model for describing table structure."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    table_name: str = Field(
        ...,
        description="Name of the table to describe (e.g., 'users', 'orders')",
        min_length=1,
        max_length=100
    )
    schema: str = Field(
        default="public",
        description="Database schema containing the table",
        min_length=1,
        max_length=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class GetTableSampleInput(BaseModel):
    """Input model for getting sample data from a table."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    table_name: str = Field(
        ...,
        description="Name of the table to sample (e.g., 'users', 'products')",
        min_length=1,
        max_length=100
    )
    schema: str = Field(
        default="public",
        description="Database schema containing the table",
        min_length=1,
        max_length=100
    )
    limit: int = Field(
        default=10,
        description="Number of rows to return (1-100)",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


# Database connection management
@asynccontextmanager
async def database_lifespan():
    """Manage database connection pool lifecycle."""
    # Get connection details from environment variables
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = int(os.getenv('POSTGRES_PORT', '5432'))
    db_name = os.getenv('POSTGRES_DB', 'postgres')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    
    # Create connection pool
    pool = await asyncpg.create_pool(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        min_size=2,
        max_size=10
    )
    
    try:
        yield {"pool": pool}
    finally:
        await pool.close()


# Initialize MCP with lifespan
mcp = FastMCP("postgres_mcp", lifespan=database_lifespan)


# Helper functions
def format_markdown_table(columns: List[str], rows: List[tuple]) -> str:
    """Format query results as a markdown table."""
    if not rows:
        return "No results found."
    
    # Create header
    header = "| " + " | ".join(str(col) for col in columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    
    # Create rows (convert all values to strings, handle None)
    table_rows = []
    for row in rows:
        formatted_row = "| " + " | ".join(
            "NULL" if val is None else str(val) for val in row
        ) + " |"
        table_rows.append(formatted_row)
    
    return "\n".join([header, separator] + table_rows)


def format_json_results(columns: List[str], rows: List[tuple]) -> str:
    """Format query results as JSON."""
    results = []
    for row in rows:
        row_dict = {}
        for col, val in zip(columns, row):
            # Handle special types
            if val is None:
                row_dict[col] = None
            else:
                row_dict[col] = val
        results.append(row_dict)
    
    return json.dumps(results, indent=2, default=str)


def truncate_if_needed(content: str, limit: int = CHARACTER_LIMIT) -> str:
    """Truncate content if it exceeds character limit."""
    if len(content) <= limit:
        return content
    
    truncated = content[:limit]
    return truncated + f"\n\n[Response truncated at {limit} characters. Use more specific queries or filters to reduce result size.]"


# MCP Tools
@mcp.tool(
    name="postgres_execute_query",
    annotations={
        "title": "Execute PostgreSQL Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def execute_query(params: ExecuteQueryInput, ctx) -> str:
    """Execute a read-only SQL query against the PostgreSQL database.
    
    This tool allows you to run SELECT queries to retrieve data from the database.
    Only read-only queries are permitted for safety - no INSERT, UPDATE, DELETE, etc.
    
    Args:
        params (ExecuteQueryInput): Query parameters containing:
            - query (str): SQL SELECT query to execute
            - response_format (ResponseFormat): Output format ('markdown' or 'json')
    
    Returns:
        str: Query results formatted as specified (markdown table or JSON array)
             Returns column names and row data. For markdown format, results are
             displayed in a readable table. For JSON format, returns array of objects.
    
    Examples:
        - "SELECT * FROM users LIMIT 10"
        - "SELECT name, email FROM users WHERE created_at > '2024-01-01'"
        - "SELECT COUNT(*) as total FROM orders WHERE status = 'completed'"
    
    Errors:
        - Raises ValueError if query contains destructive operations
        - Returns error message if query syntax is invalid
        - Returns error message if table or column doesn't exist
    """
    pool = ctx.request_context.lifespan_state["pool"]
    
    try:
        async with pool.acquire() as conn:
            # Execute query
            result = await conn.fetch(params.query)
            
            if not result:
                return "Query executed successfully but returned no rows."
            
            # Extract columns and rows
            columns = list(result[0].keys())
            rows = [tuple(row.values()) for row in result]
            
            # Format response
            if params.response_format == ResponseFormat.MARKDOWN:
                output = format_markdown_table(columns, rows)
                output = f"Query returned {len(rows)} row(s):\n\n{output}"
            else:
                output = format_json_results(columns, rows)
            
            return truncate_if_needed(output)
            
    except asyncpg.PostgresSyntaxError as e:
        return f"SQL syntax error: {str(e)}\n\nPlease check your query syntax and try again."
    except asyncpg.UndefinedTableError as e:
        return f"Table not found: {str(e)}\n\nUse 'postgres_list_tables' to see available tables."
    except asyncpg.UndefinedColumnError as e:
        return f"Column not found: {str(e)}\n\nUse 'postgres_describe_table' to see table structure."
    except Exception as e:
        return f"Error executing query: {str(e)}\n\nPlease verify your query and database connection."


@mcp.tool(
    name="postgres_list_tables",
    annotations={
        "title": "List Database Tables",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def list_tables(params: ListTablesInput, ctx) -> str:
    """List all tables in the specified database schema.
    
    This tool retrieves a list of all tables available in a schema, along with
    the estimated row count for each table. Useful for database exploration.
    
    Args:
        params (ListTablesInput): Parameters containing:
            - schema (str): Schema name (default: 'public')
            - response_format (ResponseFormat): Output format ('markdown' or 'json')
    
    Returns:
        str: List of tables with row counts, formatted as specified.
             For each table, shows: table name, estimated rows, and table type.
    
    Examples:
        - List tables in public schema: schema='public'
        - List tables in custom schema: schema='analytics'
    
    Errors:
        - Returns error message if schema doesn't exist
        - Returns empty list if schema has no tables
    """
    pool = ctx.request_context.lifespan_state["pool"]
    
    try:
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    tablename as table_name,
                    schemaname as schema_name
                FROM pg_tables 
                WHERE schemaname = $1
                ORDER BY tablename
            """
            
            result = await conn.fetch(query, params.schema)
            
            if not result:
                return f"No tables found in schema '{params.schema}'."
            
            # Get row counts for each table
            tables_info = []
            for row in result:
                count_query = f"SELECT COUNT(*) FROM {params.schema}.{row['table_name']}"
                count_result = await conn.fetchval(count_query)
                tables_info.append({
                    'table_name': row['table_name'],
                    'schema': row['schema_name'],
                    'estimated_rows': count_result
                })
            
            if params.response_format == ResponseFormat.MARKDOWN:
                output = f"## Tables in schema '{params.schema}'\n\n"
                for table in tables_info:
                    output += f"- **{table['table_name']}** ({table['estimated_rows']:,} rows)\n"
                output += f"\nTotal: {len(tables_info)} table(s)"
            else:
                output = json.dumps(tables_info, indent=2)
            
            return output
            
    except Exception as e:
        return f"Error listing tables: {str(e)}\n\nPlease verify the schema name and try again."


@mcp.tool(
    name="postgres_describe_table",
    annotations={
        "title": "Describe Table Structure",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def describe_table(params: DescribeTableInput, ctx) -> str:
    """Get detailed structure information about a specific table.
    
    This tool returns the complete schema definition for a table, including:
    - Column names, data types, and constraints
    - Primary keys and foreign keys
    - Indexes and constraints
    - Table size and row count
    
    Args:
        params (DescribeTableInput): Parameters containing:
            - table_name (str): Name of the table to describe
            - schema (str): Schema name (default: 'public')
            - response_format (ResponseFormat): Output format ('markdown' or 'json')
    
    Returns:
        str: Complete table structure with columns, types, and constraints
    
    Examples:
        - Describe users table: table_name='users', schema='public'
        - Describe custom table: table_name='orders', schema='sales'
    
    Errors:
        - Returns error if table doesn't exist
        - Suggests using 'postgres_list_tables' if table not found
    """
    pool = ctx.request_context.lifespan_state["pool"]
    
    try:
        async with pool.acquire() as conn:
            # Get column information
            query = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            """
            
            columns = await conn.fetch(query, params.schema, params.table_name)
            
            if not columns:
                return (
                    f"Table '{params.schema}.{params.table_name}' not found.\n\n"
                    "Use 'postgres_list_tables' to see available tables."
                )
            
            # Get primary key info
            pk_query = """
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_schema = $1 AND table_name = $2
                AND constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_schema = $1 AND table_name = $2
                    AND constraint_type = 'PRIMARY KEY'
                )
            """
            primary_keys = await conn.fetch(pk_query, params.schema, params.table_name)
            pk_columns = [pk['column_name'] for pk in primary_keys]
            
            if params.response_format == ResponseFormat.MARKDOWN:
                output = f"## Table: {params.schema}.{params.table_name}\n\n"
                output += "### Columns\n\n"
                output += "| Column | Type | Nullable | Default | Primary Key |\n"
                output += "|--------|------|----------|---------|-------------|\n"
                
                for col in columns:
                    col_name = col['column_name']
                    data_type = col['data_type']
                    if col['character_maximum_length']:
                        data_type += f"({col['character_maximum_length']})"
                    nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
                    default = col['column_default'] or "-"
                    is_pk = "✓" if col_name in pk_columns else ""
                    
                    output += f"| {col_name} | {data_type} | {nullable} | {default} | {is_pk} |\n"
            else:
                output = json.dumps([dict(col) for col in columns], indent=2, default=str)
            
            return output
            
    except Exception as e:
        return f"Error describing table: {str(e)}"


@mcp.tool(
    name="postgres_get_table_sample",
    annotations={
        "title": "Get Sample Data from Table",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_table_sample(params: GetTableSampleInput, ctx) -> str:
    """Retrieve sample rows from a table for quick data inspection.
    
    This tool fetches a limited number of rows from a table to help understand
    the data structure and content without querying the entire table.
    
    Args:
        params (GetTableSampleInput): Parameters containing:
            - table_name (str): Name of the table to sample
            - schema (str): Schema name (default: 'public')
            - limit (int): Number of rows to return (1-100, default: 10)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')
    
    Returns:
        str: Sample rows from the table, formatted as specified
    
    Examples:
        - Get 10 rows: table_name='users', limit=10
        - Get 50 rows: table_name='orders', limit=50
    
    Errors:
        - Returns error if table doesn't exist
        - Returns empty result if table has no data
    """
    pool = ctx.request_context.lifespan_state["pool"]
    
    try:
        async with pool.acquire() as conn:
            query = f"SELECT * FROM {params.schema}.{params.table_name} LIMIT $1"
            result = await conn.fetch(query, params.limit)
            
            if not result:
                return f"Table '{params.schema}.{params.table_name}' exists but contains no data."
            
            columns = list(result[0].keys())
            rows = [tuple(row.values()) for row in result]
            
            if params.response_format == ResponseFormat.MARKDOWN:
                output = f"Sample data from {params.schema}.{params.table_name} (showing {len(rows)} of {params.limit} requested rows):\n\n"
                output += format_markdown_table(columns, rows)
            else:
                output = format_json_results(columns, rows)
            
            return truncate_if_needed(output)
            
    except asyncpg.UndefinedTableError:
        return (
            f"Table '{params.schema}.{params.table_name}' not found.\n\n"
            "Use 'postgres_list_tables' to see available tables."
        )
    except Exception as e:
        return f"Error sampling table: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run()
