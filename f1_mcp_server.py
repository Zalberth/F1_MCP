import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class F1MCPServer:
    """
    符合MCP协议标准的F1数据服务器
    """
    
    def __init__(self):
        self.name = "f1-data-server"
        self.version = "1.0.0"
        self.session = self._create_session()
        self.base_url = "http://api.jolpi.ca/ergast/f1"
        self.initialized = False
    
    def _create_session(self):
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"])
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.headers.update({
            "User-Agent": "f1-mcp-server/1.0"
        })
        return session
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求的主入口点
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return await self._handle_list_tools(request_id)
            elif method == "tools/call":
                return await self._handle_call_tool(request_id, params)
            elif method == "resources/list":
                return await self._handle_list_resources(request_id)
            elif method == "resources/read":
                return await self._handle_read_resource(request_id, params)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
        except Exception as e:
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理初始化请求
        """
        self.initialized = True
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }
    
    async def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """
        列出可用工具
        """
        tools = [
            {
                "name": "get_drivers",
                "description": "获取指定年份的F1车手列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "赛季年份",
                            "default": 2025
                        }
                    }
                }
            },
            {
                "name": "get_driver_results",
                "description": "获取车手在指定年份的比赛结果",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "driver_id": {
                            "type": "string",
                            "description": "车手ID"
                        },
                        "year": {
                            "type": "integer",
                            "description": "赛季年份"
                        }
                    },
                    "required": ["driver_id", "year"]
                }
            },
            {
                "name": "calculate_average_position",
                "description": "计算车手年度平均排名",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "driver_id": {
                            "type": "string",
                            "description": "车手ID"
                        },
                        "year": {
                            "type": "integer",
                            "description": "赛季年份"
                        }
                    },
                    "required": ["driver_id", "year"]
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具调用
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_drivers":
            result = await self._get_drivers(arguments.get("year", 2025))
        elif tool_name == "get_driver_results":
            result = await self._get_driver_results(
                arguments.get("driver_id"),
                arguments.get("year")
            )
        elif tool_name == "calculate_average_position":
            result = await self._calculate_average_position(
                arguments.get("driver_id"),
                arguments.get("year")
            )
        else:
            return self._error_response(request_id, -32602, f"Unknown tool: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    async def _handle_list_resources(self, request_id: Any) -> Dict[str, Any]:
        """
        列出可用资源
        """
        resources = [
            {
                "uri": "f1://drivers/2025",
                "name": "2025年F1车手列表",
                "description": "当前赛季所有车手信息",
                "mimeType": "application/json"
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": resources
            }
        }
    
    async def _handle_read_resource(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        读取资源内容
        """
        uri = params.get("uri")
        
        if uri == "f1://drivers/2025":
            drivers = await self._get_drivers(2025)
            content = json.dumps(drivers, ensure_ascii=False, indent=2)
        else:
            return self._error_response(request_id, -32602, f"Unknown resource: {uri}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": content
                    }
                ]
            }
        }
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """
        生成错误响应
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    async def _get_drivers(self, year: int) -> List[Dict[str, Any]]:
        """
        获取车手列表
        """
        url = f"{self.base_url}/{year}/drivers.json"
        try:
            resp = self.session.get(url, params={"limit": 100}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data["MRData"]["DriverTable"]["Drivers"]
        except Exception as e:
            raise Exception(f"Failed to fetch drivers: {e}")
    
    async def _get_driver_results(self, driver_id: str, year: int) -> List[Dict[str, Any]]:
        """
        获取车手比赛结果
        """
        url = f"{self.base_url}/{year}/drivers/{driver_id}/results.json"
        try:
            resp = self.session.get(url, params={"limit": 100}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            races = data["MRData"]["RaceTable"]["Races"]
            races.sort(key=lambda r: int(r.get("round", 0)))
            return races
        except Exception as e:
            raise Exception(f"Failed to fetch results: {e}")
    
    async def _calculate_average_position(self, driver_id: str, year: int) -> Dict[str, Any]:
        """
        计算平均排名
        """
        races = await self._get_driver_results(driver_id, year)
        if not races:
            return {"error": "No race data found"}
        
        positions = []
        for race in races:
            if race['Results']:
                pos = race['Results'][0].get('position')
                if pos and pos.isdigit():
                    positions.append(int(pos))
                else:
                    positions.append(25)  # DNF等情况
        
        avg_position = sum(positions) / len(positions) if positions else None
        return {
            "driver_id": driver_id,
            "year": year,
            "average_position": avg_position,
            "races_count": len(races),
            "positions": positions
        }

# MCP服务器主循环
async def run_mcp_server():
    """
    运行真正的MCP服务器，通过stdin/stdout与客户端通信
    """
    server = F1MCPServer()
    
    # 向stderr输出调试信息，避免干扰stdin/stdout通信
    sys.stderr.write("F1 MCP Server starting...\n")
    sys.stderr.flush()
    
    try:
        while True:
            # 从stdin读取请求
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                # EOF，客户端断开连接
                break
                
            line = line.strip()
            if not line:
                continue
                
            try:
                # 解析JSON请求
                request = json.loads(line)
                
                # 处理请求
                response = await server.handle_request(request)
                
                # 发送响应到stdout
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json)
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                # 发送JSON解析错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        sys.stderr.write("Server stopped by user\n")
    except Exception as e:
        sys.stderr.write(f"Server error: {str(e)}\n")
    finally:
        sys.stderr.write("F1 MCP Server shutting down...\n")

if __name__ == "__main__":
    # 运行真正的MCP服务器
    asyncio.run(run_mcp_server())