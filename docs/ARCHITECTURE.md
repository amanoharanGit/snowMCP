# Architecture
 
## Overview
 
This repository contains a **Model Context Protocol (MCP) server** that exposes ServiceNow ITSM capabilities as AI-callable tools. It enables AI assistants (GitHub Copilot, Microsoft Copilot Studio, Claude) to interact with ServiceNow incidents using natural language.
 
## Full Stack Diagram
 
```
┌─────────────────────────────────────────────────────────────────┐
│                        AI FRONT ENDS                            │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  GitHub Copilot  │  │ Microsoft 365   │  │    Claude /   │  │
│  │  Chat (VS Code / │  │ Copilot Studio  │  │  Other MCP    │  │
│  │   Codespaces)    │  │    Agent        │  │   Clients     │  │
│  └────────┬────────┘  └────────┬────────┘  └──────┬────────┘  │
└───────────┼────────────────────┼──────────────────┼────────────┘
            │                    │                  │
            └────────────────────┼──────────────────┘
                                 │
                    MCP Streamable HTTP
                    POST /mcp
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RENDER (Free Tier)                          │
│                  https://snowmcp.onrender.com                   │
│                                                                 │
│   server.py — FastMCP + Python                                  │
│                                                                 │
│   Tools:                                                        │
│   • list_incidents      • update_incident                       │
│   • get_incident        • add_comment                           │
│   • create_incident     • get_user                              │
│   • search_incidents                                            │
│                                                                 │
│   Config (env vars):                                            │
│   SNOW_INSTANCE_URL / SNOW_USERNAME / SNOW_PASSWORD             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                REST API (Basic Auth)
                GET/POST/PATCH
                /api/now/table/incident
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVICENOW PDI                                     │
│          https://dev392935.service-now.com                      │
│                                                                 │
│   User: mcp.api (itil role)                                     │
│   Tables: incident, sys_user                                    │
│   Version: Australia (Latest Release)                           │
└─────────────────────────────────────────────────────────────────┘
```
 
## Repository Structure
 
```
snowMCP/
├── .devcontainer/
│   └── devcontainer.json        # Codespaces auto-configuration
├── .github/
│   └── workflows/
│       └── deploy.yml           # Auto-deploy to Render on push to main
├── .vscode/
│   └── mcp.json                 # MCP client config for Copilot Chat
├── docs/
│   └── ARCHITECTURE.md          # This file
├── server.py                    # MCP server — all 7 tools
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render service configuration
└── README.md                    # Setup and usage guide
```
 
## Components
 
### `server.py`
The core MCP server built with FastMCP. Exposes 7 tools that map directly to ServiceNow REST API calls. Uses Streamable HTTP transport for broad client compatibility.
 
### `render.yaml`
Render Web Service configuration. Defines build command, start command, and environment variable placeholders. Credentials are stored in Render's dashboard — never in code.
 
### `.devcontainer/devcontainer.json`
Codespaces configuration. When a developer opens this repo in GitHub Codespaces, Python 3.12 is pre-configured, all dependencies are auto-installed, port 8000 is forwarded, and the GitHub Copilot extension is pre-installed.
 
### `.vscode/mcp.json`
Points GitHub Copilot Chat's Agent Mode at the live Render server. Any developer opening this repo in VS Code or Codespaces gets the ServiceNow tools available in Copilot immediately.
 
### `.github/workflows/deploy.yml`
GitHub Actions workflow that triggers a Render deploy hook on every push to `main`. Requires `RENDER_DEPLOY_HOOK_URL` to be set as a GitHub repository secret.
 
## Deployment
 
### Environment Variables (Render Dashboard)
| Variable | Description |
|---|---|
| `SNOW_INSTANCE_URL` | ServiceNow instance URL e.g. `https://dev392935.service-now.com` |
| `SNOW_USERNAME` | API user e.g. `mcp.api` |
| `SNOW_PASSWORD` | API user password |
 
### GitHub Secrets (for CI/CD)
| Secret | Description |
|---|---|
| `RENDER_DEPLOY_HOOK_URL` | Found in Render → Settings → Deploy Hook |
 
## MCP Clients Supported
 
| Client | Transport | Config |
|---|---|---|
| GitHub Copilot (VS Code / Codespaces) | Streamable HTTP | `.vscode/mcp.json` |
| Microsoft Copilot Studio | Streamable HTTP | Add tool via MCP wizard |
| Claude Desktop | Streamable HTTP | `claude_desktop_config.json` |
| MCP Inspector | Streamable HTTP | Direct URL entry |
 
## ServiceNow Tools Reference
 
| Tool | Method | Description |
|---|---|---|
| `list_incidents` | GET | List incidents filtered by state/priority |
| `get_incident` | GET | Get full details by incident number |
| `create_incident` | POST | Open a new incident |
| `update_incident` | PATCH | Update state, priority, assignee, notes |
| `add_comment` | PATCH | Add public comment or private work note |
| `get_user` | GET | Look up a user by username |
| `search_incidents` | GET | Keyword search across incident fields |