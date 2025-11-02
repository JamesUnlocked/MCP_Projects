# MCP Server Project

A Model Context Protocol (MCP) server application for building custom tools and integrations.

## Overview

This project implements an MCP server that provides custom tools and capabilities. The Model Context Protocol enables seamless integration between AI applications and external tools/data sources.

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
npm install
```

### Building

```bash
npm run build
```

### Running

```bash
npm start
```

## Development

### Watch Mode

To automatically rebuild on file changes:

```bash
npm run watch
```

## Project Structure

```
.
├── src/
│   └── index.ts       # Main server implementation
├── build/             # Compiled JavaScript (generated)
├── package.json       # Project dependencies and scripts
├── tsconfig.json      # TypeScript configuration
└── README.md          # This file
```

## Adding Custom Tools

Edit `src/index.ts` to add your custom tools. Each tool needs:

1. A definition in the `ListToolsRequestSchema` handler
2. An implementation in the `CallToolRequestSchema` handler

## License

MIT
