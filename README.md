Readme · MD
Copy

# ServiceNow MCP Server
 
A **Model Context Protocol (MCP) server** that exposes ServiceNow ITSM tools via Streamable HTTP transport. Connect any MCP-compatible AI assistant — GitHub Copilot, Microsoft Copilot Studio, Claude — to ServiceNow using natural language.
 
---
 
## What It Does
 
Ask your AI assistant things like:
- *"List all high priority open incidents"*
- *"Create an incident for the authentication service being down"*
- *"Update INC0010001 to In Progress and assign it to mcp.api"*
- *"Search for incidents related to network"*
- *"Add a work note to INC0010001 saying investigation is underway"*
## Tools Exposed
 
| Tool | Description |
|---|---|
| `list_incidents` | List incidents filtered by state or priority |
| `get_incident` | Get full details by incident number |
| `create_incident` | Open a new incident |
| `update_incident` | Update state, priority, assignee, or notes |
| `add_comment` | Add a public comment or private work note |
| `get_user` | Look up a user by username |
| `search_incidents` | Keyword search across incident fields |
 
---
 
## Quick Start (Codespaces)
 
The fastest way to get started — no local install needed:
 
1. Click **Code → Codespaces → Create codespace on main**
2. Wait ~60 seconds for the environment to auto-configure
3. Set your environment variables (see below)
4. Run the server locally: `python server.py`
5. Open Copilot Chat in Agent Mode and start prompting
---
 
## Environment Variables
 
Never commit credentials. Set these in Render (production) or as Codespaces secrets (development):
 
| Variable | Description | Example |
|---|---|---|
| `SNOW_INSTANCE_URL` | Your ServiceNow instance URL | `https://dev392935.service-now.com` |
| `SNOW_USERNAME` | API user with `itil` role | `mcp.api` |
| `SNOW_PASSWORD` | API user password | `your-password` |
 
### Setting Codespaces Secrets
Go to `https://github.com/settings/codespaces` and add the three variables above as Codespaces secrets. They'll be available automatically in any Codespace you open.
 
---
 
## Deploying to Render
 
1. Fork this repo
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your forked repo
4. Set the three environment variables in Render's dashboard
5. **Build command:** `pip install -r requirements.txt`
6. **Start command:** `python server.py`
Your MCP server will be live at `https://your-service.onrender.com/mcp`
 
### Auto-Deploy via GitHub Actions
 
Add your Render deploy hook as a GitHub repository secret:
1. In Render → your service → **Settings → Deploy Hook** → copy the URL
2. In GitHub → your repo → **Settings → Secrets → Actions** → add `RENDER_DEPLOY_HOOK_URL`
Every push to `main` will now auto-deploy to Render.
 
---
 
## Connecting to AI Clients
 
### GitHub Copilot (VS Code / Codespaces)
Already configured via `.vscode/mcp.json`. Open the file and click **Start**.
 
### Microsoft Copilot Studio
1. Create a new agent at [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Enable **Generative orchestration** in Settings
3. Go to **Tools → Add a tool → New tool → Model Context Protocol**
4. Enter your Render URL: `https://your-service.onrender.com/mcp`
5. Publish the agent to Microsoft 365 Copilot
### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "servicenow": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-service.onrender.com/mcp"]
    }
  }
}
```
 
---
 
## ServiceNow Setup
 
1. Get a free Personal Developer Instance at [developer.servicenow.com](https://developer.servicenow.com)
2. Create a dedicated API user (`mcp.api`) with the `itil` role
3. Use those credentials as your environment variables
---
 
## Architecture
 
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full stack diagram and component breakdown.
 
---
 
## Stack
 
- **Runtime:** Python 3.12
- **MCP SDK:** `mcp[cli]` 1.27.0
- **Transport:** Streamable HTTP
- **Hosting:** Render (free tier)
- **ServiceNow:** Personal Developer Instance