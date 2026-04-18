from fastapi import APIRouter, Depends, HTTPException
from ..mcp_server import server as mcp_root
from pydantic import BaseModel
from typing import Any

router = APIRouter(prefix="/debug", tags=["debug"])

class ToolRequest(BaseModel):
    name: str
    arguments: dict

@router.post("/tools/call")
async def call_tool_debug(request: ToolRequest):
    """
    Manually invoke an MCP tool for debugging.
    """
    tool_func = mcp_root.mcp._tools.get(request.name)
    if not tool_func:
        raise HTTPException(status_code=404, detail=f"Tool {request.name} not found")
        
    try:
        result = await tool_func.fn(**request.arguments)
        return {"tool": request.name, "result": result}
    except Exception as e:
        return {"error": str(e)}

@router.get("/tools")
async def list_tools():
    """
    List all registered forensic tools.
    """
    return {
        "tools": [
            {"name": name, "description": tool.description}
            for name, tool in mcp_root.mcp._tools.items()
        ]
    }
