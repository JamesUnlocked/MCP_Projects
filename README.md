# MCP Server Project

A Model Context Protocol (MCP) server implementation that provides example tools for AI assistants.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between AI applications and external data sources and tools. This server implements the MCP specification to expose tools that can be used by AI assistants like Claude.

## Features

This MCP server provides the following tools:

- **echo**: Echoes back input text (useful for testing)
- **add**: Adds two numbers together
- **get_current_time**: Returns the current date and time

## Installation

1. Clone this repository:
```bash
git clone https://github.com/JamesUnlocked/MCP_Projects.git
cd MCP_Projects
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Usage

### Running the Server

You can run the server in development mode using tsx:
```bash
npm run dev
```

Or build and run the compiled version:
```bash
npm run build
npm start
```

### Integrating with Claude Desktop

To use this MCP server with Claude Desktop, add the following to your Claude configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "example-server": {
      "command": "node",
      "args": ["/absolute/path/to/MCP_Projects/dist/index.js"]
    }
  }
}
```

Replace `/absolute/path/to/MCP_Projects` with the actual path to this project directory.

### Testing the Tools

Once connected, you can ask Claude to use the tools:

- "Can you echo 'Hello, MCP!' for me?"
- "Please add 42 and 58"
- "What's the current time?"

## Development

### Project Structure

```
MCP_Projects/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Compiled JavaScript output
├── package.json          # Project dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

### Available Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Run in development mode with tsx
- `npm run watch` - Watch for changes and recompile
- `npm start` - Run the compiled server

### Adding New Tools

To add a new tool:

1. Add the tool definition to the `TOOLS` array in `src/index.ts`
2. Add a case handler in the `CallToolRequestSchema` handler
3. Rebuild the project with `npm run build`

Example:
```typescript
{
  name: "my_tool",
  description: "Description of what the tool does",
  inputSchema: {
    type: "object",
    properties: {
      param1: {
        type: "string",
        description: "Description of parameter"
      }
    },
    required: ["param1"]
  }
}
```

## Technical Details

- Built with TypeScript
- Uses the official `@modelcontextprotocol/sdk` package
- Communicates via stdio (standard input/output)
- Follows the MCP specification for tool registration and execution

## License

ISC

## Contributing

Feel free to submit issues or pull requests to enhance the server's functionality!

