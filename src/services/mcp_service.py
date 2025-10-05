import asyncio
import logging
from typing import Dict, List, Any, Optional
import subprocess
import json
import os

class MCPService:
    def __init__(self):
        self.servers: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    async def start_server(self, server_id: str, config: Dict[str, Any]) -> bool:
        """Start an MCP server"""
        try:
            command = [config["command"]] + config.get("args", [])
            
            # Start the MCP server process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**config.get("env", {}), **dict(os.environ)}
            )
            
            self.servers[server_id] = {
                "process": process,
                "config": config,
                "status": "running"
            }
            
            self.logger.info(f"MCP server {server_id} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server {server_id}: {e}")
            return False
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict) -> Dict:
        """Call a tool on specific MCP server"""
        if server_id not in self.servers:
            return {"error": f"Server {server_id} not found"}
        
        try:
            # Simple MCP protocol implementation
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            process = self.servers[server_id]["process"]
            process.stdin.write(json.dumps(request).encode() + b"\n")
            await process.stdin.drain()
            
            # Read response
            line = await process.stdout.readline()
            response = json.loads(line.decode())
            
            return response.get("result", {})
            
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
    
    def get_available_servers(self) -> List[str]:
        return list(self.servers.keys())
    
    async def stop_server(self, server_id: str):
        """Stop an MCP server"""
        if server_id in self.servers:
            process = self.servers[server_id]["process"]
            process.terminate()
            await process.wait()
            del self.servers[server_id]

# Global MCP service instance
mcp_service = MCPService()