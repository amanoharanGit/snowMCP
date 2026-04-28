# ServiceNow MCP Server
 
A Model Context Protocol (MCP) server that exposes ServiceNow ITSM tools via Streamable HTTP transport. Designed for demo use with a ServiceNow Personal Developer Instance (PDI).
 
## Tools Exposed
 
| Tool | Description |
|------|-------------|
| `list_incidents` | List incidents, optionally filtered by state or priority |
| `get_incident` | Retrieve full details of a single incident by number |
| `create_incident` | Open a new incident |
| `update_incident` | Update state, priority, assignee, or add work notes |
| `add_comment` | Add a public comment or private work note |
| `get_user` | Look up a user by username |
| `search_incidents` | Search incidents by keyword |
 
## Environment Variables
 
Set these in Render (or a local `.env` file):
 
```
SNOW_INSTANCE_URL=https://dev392935.service-now.com
SNOW_USERNAME=mcp.api
SNOW_PASSWORD=your_password_here
```
 
## Deploying to Render
 
1. Push this repo to GitHub
2. Create a new **Web Service** on Render
3. Connect your GitHub repo
4. Set the environment variables above
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
Your MCP server URL will be: `https://your-service.onrender.com/mcp`
 
## Connecting to Claude
 
In Claude's MCP settings, add a new server with:
- **Transport**: Streamable HTTP
- **URL**: `https://your-service.onrender.com/mcp`
## Health Check
 
`GET /health` — returns `{"status": "ok"}`. Use this endpoint for uptime monitoring or self-ping to prevent Render free tier sleep.
