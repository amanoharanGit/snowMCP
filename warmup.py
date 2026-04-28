#!/usr/bin/env python3
"""
warmup.py — Pre-demo jumpstart script
Wakes up Render (free tier sleep) and verifies ServiceNow PDI is online
before you walk into a demo or presentation.
 
Usage:
    python warmup.py
 
Environment variables required (or set in .env):
    SNOW_INSTANCE_URL
    SNOW_USERNAME
    SNOW_PASSWORD
    MCP_SERVER_URL (optional, defaults to https://snowmcp.onrender.com)
"""
 
import os
import sys
import time
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
# --- Config ---
MCP_SERVER_URL   = os.environ.get("MCP_SERVER_URL", "https://snowmcp.onrender.com")
SNOW_INSTANCE    = os.environ.get("SNOW_INSTANCE_URL", "").rstrip("/")
SNOW_USERNAME    = os.environ.get("SNOW_USERNAME", "")
SNOW_PASSWORD    = os.environ.get("SNOW_PASSWORD", "")
 
RENDER_HEALTH    = f"{MCP_SERVER_URL}/health"
RENDER_MCP       = f"{MCP_SERVER_URL}/mcp"
SNOW_HEALTH      = f"{SNOW_INSTANCE}/api/now/table/incident?sysparm_limit=1"
 
MAX_RETRIES      = 10
RETRY_DELAY      = 8  # seconds between retries
 
 
def print_status(label, ok, detail=""):
    icon = "✅" if ok else "❌"
    print(f"  {icon}  {label}", end="")
    if detail:
        print(f"  →  {detail}", end="")
    print()
 
 
def wake_render():
    """Ping Render health endpoint, retrying until it wakes up."""
    print("\n🔄  Waking up Render server...")
    print(f"    URL: {RENDER_HEALTH}")
    print(f"    (Free tier can take up to {MAX_RETRIES * RETRY_DELAY}s to wake)\n")
 
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(RENDER_HEALTH, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                print_status("Render server", True, f"awake after {attempt} attempt(s)")
                return True
            else:
                print(f"  ⏳  Attempt {attempt}/{MAX_RETRIES} — HTTP {resp.status_code}, retrying...")
        except requests.exceptions.ConnectionError:
            print(f"  ⏳  Attempt {attempt}/{MAX_RETRIES} — still waking up...")
        except requests.exceptions.Timeout:
            print(f"  ⏳  Attempt {attempt}/{MAX_RETRIES} — timeout, retrying...")
 
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
 
    print_status("Render server", False, "failed to wake after all retries")
    return False
 
 
def check_mcp_endpoint():
    """Verify the /mcp endpoint responds to an MCP initialize handshake."""
    print("\n🔄  Verifying MCP endpoint...")
 
    try:
        resp = requests.post(
            RENDER_MCP,
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {}
                },
                "id": 1
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=20
        )
 
        if resp.status_code == 200:
            print_status("MCP /mcp endpoint", True, "responding to initialize handshake")
            return True
        else:
            print_status("MCP /mcp endpoint", False, f"HTTP {resp.status_code}")
            return False
 
    except Exception as e:
        print_status("MCP /mcp endpoint", False, str(e))
        return False
 
 
def check_snow_pdi():
    """Verify ServiceNow PDI is online and credentials work."""
    print("\n🔄  Checking ServiceNow PDI...")
 
    if not SNOW_INSTANCE:
        print_status("ServiceNow PDI", False, "SNOW_INSTANCE_URL not set")
        return False
 
    if not SNOW_USERNAME or not SNOW_PASSWORD:
        print_status("ServiceNow PDI", False, "SNOW_USERNAME or SNOW_PASSWORD not set")
        return False
 
    try:
        resp = requests.get(
            SNOW_HEALTH,
            auth=(SNOW_USERNAME, SNOW_PASSWORD),
            headers={"Accept": "application/json"},
            timeout=20
        )
 
        if resp.status_code == 200:
            records = resp.json().get("result", [])
            print_status("ServiceNow PDI", True, f"online and authenticated ({SNOW_INSTANCE})")
            return True
        elif resp.status_code == 401:
            print_status("ServiceNow PDI", False, "401 Unauthorized — check SNOW_USERNAME / SNOW_PASSWORD")
            return False
        elif resp.status_code == 403:
            print_status("ServiceNow PDI", False, "403 Forbidden — mcp.api user may lack itil role")
            return False
        else:
            print_status("ServiceNow PDI", False, f"HTTP {resp.status_code}")
            return False
 
    except requests.exceptions.ConnectionError:
        print_status("ServiceNow PDI", False, "connection refused — PDI may be hibernating")
        print("  💡  Go to https://developer.servicenow.com → My Instance → Wake")
        return False
    except requests.exceptions.Timeout:
        print_status("ServiceNow PDI", False, "timeout — PDI may be starting up, try again in 30s")
        return False
    except Exception as e:
        print_status("ServiceNow PDI", False, str(e))
        return False
 
 
def main():
    print("=" * 55)
    print("  🚀  ServiceNow MCP — Pre-Demo Warmup")
    print("=" * 55)
 
    results = {}
 
    # Step 1 — Wake Render
    results["render"] = wake_render()
 
    # Step 2 — Check MCP endpoint (only if Render is up)
    if results["render"]:
        results["mcp"] = check_mcp_endpoint()
    else:
        results["mcp"] = False
 
    # Step 3 — Check ServiceNow PDI
    results["snow"] = check_snow_pdi()
 
    # --- Summary ---
    print("\n" + "=" * 55)
    print("  📋  Summary")
    print("=" * 55)
    print_status("Render server awake",    results["render"])
    print_status("MCP endpoint live",      results["mcp"])
    print_status("ServiceNow PDI online",  results["snow"])
    print()
 
    all_good = all(results.values())
 
    if all_good:
        print("  🟢  All systems go — you're ready to demo!\n")
    else:
        print("  🔴  One or more systems need attention before demoing.\n")
        if not results["snow"]:
            print("  💡  If PDI is hibernating:")
            print("      → Go to https://developer.servicenow.com")
            print("      → Click My Instance → Wake Instance\n")
        if not results["render"]:
            print("  💡  If Render won't wake:")
            print("      → Go to https://render.com → your service → Manual Deploy\n")
 
    sys.exit(0 if all_good else 1)
 
 
if __name__ == "__main__":
    main()
