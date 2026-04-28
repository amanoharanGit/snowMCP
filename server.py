import os
import requests
#from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
 
# --- Configuration ---
SNOW_INSTANCE_URL = os.environ.get("SNOW_INSTANCE_URL", "").rstrip("/")
SNOW_USERNAME = os.environ.get("SNOW_USERNAME", "")
SNOW_PASSWORD = os.environ.get("SNOW_PASSWORD", "")
 
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
 
# --- FastMCP Server ---
mcp = FastMCP("ServiceNow MCP Server", json_response=True, stateless_http=True)
 
 
def snow_auth():
    return (SNOW_USERNAME, SNOW_PASSWORD)
 
 
def snow_get(path: str, params: dict = None) -> dict:
    url = f"{SNOW_INSTANCE_URL}{path}"
    resp = requests.get(url, auth=snow_auth(), headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()
 
 
def snow_post(path: str, payload: dict) -> dict:
    url = f"{SNOW_INSTANCE_URL}{path}"
    resp = requests.post(url, auth=snow_auth(), headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()
 
 
def snow_patch(path: str, payload: dict) -> dict:
    url = f"{SNOW_INSTANCE_URL}{path}"
    resp = requests.patch(url, auth=snow_auth(), headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()
 
 
# --- Tools ---
 
@mcp.tool()
def list_incidents(
    state: str = None,
    priority: str = None,
    limit: int = 10
) -> dict:
    """
    List incidents from ServiceNow.
    Optionally filter by state (e.g. '1' = New, '2' = In Progress, '3' = On Hold,
    '6' = Resolved, '7' = Closed) or priority ('1' = Critical, '2' = High,
    '3' = Moderate, '4' = Low). Defaults to returning 10 most recent.
    """
    query_parts = []
    if state:
        query_parts.append(f"state={state}")
    if priority:
        query_parts.append(f"priority={priority}")
 
    params = {
        "sysparm_limit": limit,
        "sysparm_fields": "number,short_description,state,priority,assigned_to,opened_at,sys_id",
        "sysparm_display_value": "true",
        "sysparm_order_by_desc": "opened_at",
    }
    if query_parts:
        params["sysparm_query"] = "^".join(query_parts)
 
    result = snow_get("/api/now/table/incident", params=params)
    return {"incidents": result.get("result", []), "count": len(result.get("result", []))}
 
 
@mcp.tool()
def get_incident(number: str) -> dict:
    """
    Retrieve a single ServiceNow incident by its number (e.g. INC0010001).
    Returns full incident details including description, state, priority,
    assigned_to, opened_at, resolved_at, and work notes.
    """
    params = {
        "sysparm_query": f"number={number}",
        "sysparm_display_value": "true",
        "sysparm_fields": "number,short_description,description,state,priority,urgency,impact,assigned_to,opened_by,opened_at,resolved_at,close_notes,work_notes,sys_id",
        "sysparm_limit": 1,
    }
    result = snow_get("/api/now/table/incident", params=params)
    records = result.get("result", [])
    if not records:
        return {"error": f"Incident {number} not found"}
    return records[0]
 
 
@mcp.tool()
def create_incident(
    short_description: str,
    description: str = "",
    priority: str = "3",
    urgency: str = "2",
    impact: str = "2",
    assigned_to: str = ""
) -> dict:
    """
    Create a new ServiceNow incident.
    Priority: 1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning.
    Urgency/Impact: 1=High, 2=Medium, 3=Low.
    assigned_to is optional — use a username or leave blank.
    Returns the created incident including its number and sys_id.
    """
    payload = {
        "short_description": short_description,
        "description": description,
        "priority": priority,
        "urgency": urgency,
        "impact": impact,
        "state": "1",  # New
    }
    if assigned_to:
        payload["assigned_to"] = assigned_to
 
    result = snow_post("/api/now/table/incident", payload)
    record = result.get("result", {})
    return {
        "message": "Incident created successfully",
        "number": record.get("number"),
        "sys_id": record.get("sys_id"),
        "state": record.get("state"),
        "priority": record.get("priority"),
    }
 
 
@mcp.tool()
def update_incident(
    number: str,
    state: str = None,
    priority: str = None,
    assigned_to: str = None,
    work_notes: str = None,
    close_notes: str = None
) -> dict:
    """
    Update an existing ServiceNow incident by its number (e.g. INC0010001).
    Provide only the fields you want to change.
    State values: 1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed.
    Priority values: 1=Critical, 2=High, 3=Moderate, 4=Low.
    work_notes adds an internal note. close_notes required when resolving.
    """
    # First look up the sys_id
    lookup = snow_get("/api/now/table/incident", params={
        "sysparm_query": f"number={number}",
        "sysparm_fields": "sys_id",
        "sysparm_limit": 1,
    })
    records = lookup.get("result", [])
    if not records:
        return {"error": f"Incident {number} not found"}
 
    sys_id = records[0]["sys_id"]
 
    payload = {}
    if state:
        payload["state"] = state
    if priority:
        payload["priority"] = priority
    if assigned_to:
        payload["assigned_to"] = assigned_to
    if work_notes:
        payload["work_notes"] = work_notes
    if close_notes:
        payload["close_notes"] = close_notes
 
    if not payload:
        return {"error": "No fields provided to update"}
 
    result = snow_patch(f"/api/now/table/incident/{sys_id}", payload)
    record = result.get("result", {})
    return {
        "message": f"Incident {number} updated successfully",
        "number": number,
        "sys_id": sys_id,
        "updated_fields": list(payload.keys()),
    }
 
 
@mcp.tool()
def add_comment(number: str, comment: str, is_internal: bool = False) -> dict:
    """
    Add a comment or work note to a ServiceNow incident.
    Set is_internal=True to add a private work note (visible to agents only).
    Set is_internal=False (default) to add a public comment visible to the caller.
    """
    lookup = snow_get("/api/now/table/incident", params={
        "sysparm_query": f"number={number}",
        "sysparm_fields": "sys_id",
        "sysparm_limit": 1,
    })
    records = lookup.get("result", [])
    if not records:
        return {"error": f"Incident {number} not found"}
 
    sys_id = records[0]["sys_id"]
    field = "work_notes" if is_internal else "comments"
    result = snow_patch(f"/api/now/table/incident/{sys_id}", {field: comment})
 
    return {
        "message": f"{'Work note' if is_internal else 'Comment'} added to {number}",
        "number": number,
        "type": "work_note" if is_internal else "public_comment",
    }
 
 
@mcp.tool()
def get_user(username: str) -> dict:
    """
    Look up a ServiceNow user by their username (user_id).
    Returns name, email, department, title, and active status.
    """
    params = {
        "sysparm_query": f"user_name={username}",
        "sysparm_fields": "user_name,name,email,department,title,active,sys_id",
        "sysparm_display_value": "true",
        "sysparm_limit": 1,
    }
    result = snow_get("/api/now/v2/table/sys_user", params=params)
    records = result.get("result", [])
    if not records:
        return {"error": f"User '{username}' not found"}
    return records[0]
 
 
@mcp.tool()
def search_incidents(keyword: str, limit: int = 5) -> dict:
    """
    Search incidents by keyword across short_description and description fields.
    Useful for finding related incidents or checking if an issue has been reported before.
    """
    params = {
        "sysparm_query": f"short_descriptionLIKE{keyword}^ORdescriptionLIKE{keyword}",
        "sysparm_fields": "number,short_description,state,priority,opened_at",
        "sysparm_display_value": "true",
        "sysparm_limit": limit,
        "sysparm_order_by_desc": "opened_at",
    }
    result = snow_get("/api/now/table/incident", params=params)
    records = result.get("result", [])
    return {"results": records, "count": len(records), "keyword": keyword}
 
 
# --- Streamable HTTP ---
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )