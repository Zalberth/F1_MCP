#!/usr/bin/env python3
"""
FastF1 MCP Server - Comprehensive F1 Data Server
基于FastF1库的MCP服务器，提供完整的F1数据访问功能
"""

import asyncio
import json
import sys
import os
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd

# FastF1 imports
try:
    import fastf1
    from fastf1 import get_session, get_event_schedule
    from fastf1.ergast import Ergast
    import fastf1.core
    import fastf1.utils
    # Session and Event are available through get_session and get_event_schedule
except ImportError as e:
    print(f"FastF1 not installed or import failed: {e}", file=sys.stderr)
    print("Please install with: pip install fastf1 pandas numpy matplotlib scipy tqdm requests urllib3", file=sys.stderr)
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FastF1MCPServer:
    """
    基于FastF1的MCP服务器，提供全面的F1数据访问功能
    """
    
    def __init__(self):
        self.name = "fastf1-mcp-server"
        self.version = "2.0.0"
        self.ergast = Ergast()
        self.cache_enabled = True
        self.cache_dir = None
        
        # 初始化FastF1缓存
        self._setup_cache()
        
    def _setup_cache(self):
        """设置FastF1缓存"""
        try:
            if self.cache_enabled:
                fastf1.Cache.enable_cache(self.cache_dir or './f1_cache')
                logger.info("FastF1 cache enabled")
        except Exception as e:
            logger.warning(f"Failed to setup cache: {e}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求的主入口点"""
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
            logger.error(f"Error handling request: {e}")
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
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
        """列出可用工具"""
        tools = [
            # 事件和会话工具
            {
                "name": "get_event_schedule",
                "description": "获取F1赛事日程表",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "赛季年份，默认为当前年份"
                        },
                        "include_testing": {
                            "type": "boolean",
                            "description": "是否包含测试赛，默认为false"
                        }
                    }
                }
            },
            {
                "name": "get_session",
                "description": "获取指定会话的数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型 (FP1, FP2, FP3, Q, SQ, R, Sprint)"
                        }
                    },
                    "required": ["year", "gp", "session"]
                }
            },
            {
                "name": "get_session_results",
                "description": "获取会话结果",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型 (FP1, FP2, FP3, Q, SQ, R, Sprint)"
                        }
                    },
                    "required": ["year", "gp", "session"]
                }
            },
            
            # 圈速和遥测数据工具
            {
                "name": "get_lap_times",
                "description": "获取车手圈速数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型"
                        },
                        "driver": {
                            "type": "string",
                            "description": "车手编号 (可选)"
                        }
                    },
                    "required": ["year", "gp", "session"]
                }
            },
            {
                "name": "get_telemetry",
                "description": "获取车手遥测数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型"
                        },
                        "driver": {
                            "type": "string",
                            "description": "车手编号"
                        },
                        "lap": {
                            "type": "integer",
                            "description": "圈数 (可选)"
                        }
                    },
                    "required": ["year", "gp", "session", "driver"]
                }
            },
            
            # 天气和赛道状态工具
            {
                "name": "get_weather_data",
                "description": "获取天气数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型"
                        }
                    },
                    "required": ["year", "gp", "session"]
                }
            },
            {
                "name": "get_track_status",
                "description": "获取赛道状态变化",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码"
                        },
                        "session": {
                            "type": "string",
                            "description": "会话类型"
                        }
                    },
                    "required": ["year", "gp", "session"]
                }
            },
            
            # 车手和车队信息工具
            {
                "name": "get_driver_info",
                "description": "获取车手信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "driver": {
                            "type": "string",
                            "description": "车手编号或姓名"
                        }
                    },
                    "required": ["year", "driver"]
                }
            },
            {
                "name": "get_team_info",
                "description": "获取车队信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "team": {
                            "type": "string",
                            "description": "车队名称"
                        }
                    },
                    "required": ["year", "team"]
                }
            },
            
            # 锦标赛积分榜工具
            {
                "name": "get_driver_standings",
                "description": "获取车手积分榜",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "round": {
                            "type": "integer",
                            "description": "回合数 (可选)"
                        }
                    },
                    "required": ["year"]
                }
            },
            {
                "name": "get_constructor_standings",
                "description": "获取车队积分榜",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "round": {
                            "type": "integer",
                            "description": "回合数 (可选)"
                        }
                    },
                    "required": ["year"]
                }
            },
            
            # 历史数据工具
            {
                "name": "get_historical_results",
                "description": "获取历史比赛结果",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码 (可选)"
                        }
                    },
                    "required": ["year"]
                }
            },
            {
                "name": "get_lap_records",
                "description": "获取赛道圈速记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "circuit": {
                            "type": "string",
                            "description": "赛道名称"
                        }
                    },
                    "required": ["circuit"]
                }
            },
            
            # 统计分析工具
            {
                "name": "calculate_driver_statistics",
                "description": "计算车手统计数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "driver": {
                            "type": "string",
                            "description": "车手编号"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码 (可选)"
                        }
                    },
                    "required": ["year", "driver"]
                }
            },
            {
                "name": "compare_drivers",
                "description": "比较两位车手的表现",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "year": {
                            "type": "integer",
                            "description": "年份"
                        },
                        "driver1": {
                            "type": "string",
                            "description": "第一位车手编号"
                        },
                        "driver2": {
                            "type": "string",
                            "description": "第二位车手编号"
                        },
                        "gp": {
                            "type": "string",
                            "description": "大奖赛名称或号码 (可选)"
                        }
                    },
                    "required": ["year", "driver1", "driver2"]
                }
            },
            
            # 配置和缓存工具
            {
                "name": "configure_cache",
                "description": "配置缓存设置",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "是否启用缓存"
                        },
                        "cache_dir": {
                            "type": "string",
                            "description": "缓存目录路径"
                        },
                        "clear_cache": {
                            "type": "boolean",
                            "description": "是否清除现有缓存"
                        }
                    }
                }
            },
            {
                "name": "get_cache_info",
                "description": "获取缓存信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
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
        """执行工具调用"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "get_event_schedule":
                result = await self._get_event_schedule(arguments)
            elif tool_name == "get_session":
                result = await self._get_session_data(arguments)
            elif tool_name == "get_session_results":
                result = await self._get_session_results(arguments)
            elif tool_name == "get_lap_times":
                result = await self._get_lap_times(arguments)
            elif tool_name == "get_telemetry":
                result = await self._get_telemetry(arguments)
            elif tool_name == "get_weather_data":
                result = await self._get_weather_data(arguments)
            elif tool_name == "get_track_status":
                result = await self._get_track_status(arguments)
            elif tool_name == "get_driver_info":
                result = await self._get_driver_info(arguments)
            elif tool_name == "get_team_info":
                result = await self._get_team_info(arguments)
            elif tool_name == "get_driver_standings":
                result = await self._get_driver_standings(arguments)
            elif tool_name == "get_constructor_standings":
                result = await self._get_constructor_standings(arguments)
            elif tool_name == "get_historical_results":
                result = await self._get_historical_results(arguments)
            elif tool_name == "get_lap_records":
                result = await self._get_lap_records(arguments)
            elif tool_name == "calculate_driver_statistics":
                result = await self._calculate_driver_statistics(arguments)
            elif tool_name == "compare_drivers":
                result = await self._compare_drivers(arguments)
            elif tool_name == "configure_cache":
                result = await self._configure_cache(arguments)
            elif tool_name == "get_cache_info":
                result = await self._get_cache_info()
            else:
                return self._error_response(request_id, -32602, f"Unknown tool: {tool_name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2, default=str)
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {e}")
            return self._error_response(request_id, -32603, f"Tool error: {str(e)}")
    
    async def _handle_list_resources(self, request_id: Any) -> Dict[str, Any]:
        """列出可用资源"""
        resources = [
            {
                "uri": "f1://schedule/current",
                "name": "当前赛季日程",
                "description": "当前赛季的F1赛事日程",
                "mimeType": "application/json"
            },
            {
                "uri": "f1://standings/drivers",
                "name": "车手积分榜",
                "description": "当前赛季车手积分榜",
                "mimeType": "application/json"
            },
            {
                "uri": "f1://standings/constructors",
                "name": "车队积分榜",
                "description": "当前赛季车队积分榜",
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
        """读取资源内容"""
        uri = params.get("uri")
        
        try:
            if uri == "f1://schedule/current":
                current_year = datetime.now().year
                schedule = await self._get_event_schedule({"year": current_year})
                content = json.dumps(schedule, ensure_ascii=False, indent=2, default=str)
            elif uri == "f1://standings/drivers":
                current_year = datetime.now().year
                standings = await self._get_driver_standings({"year": current_year})
                content = json.dumps(standings, ensure_ascii=False, indent=2, default=str)
            elif uri == "f1://standings/constructors":
                current_year = datetime.now().year
                standings = await self._get_constructor_standings({"year": current_year})
                content = json.dumps(standings, ensure_ascii=False, indent=2, default=str)
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
        except Exception as e:
            return self._error_response(request_id, -32603, f"Resource error: {str(e)}")
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """生成错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
    
    # 工具实现方法
    async def _get_event_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取赛事日程"""
        year = params.get("year", datetime.now().year)
        include_testing = params.get("include_testing", False)
        
        try:
            schedule = get_event_schedule(year, include_testing=include_testing)
            return {
                "year": year,
                "events": schedule.to_dict('records'),
                "total_events": len(schedule)
            }
        except Exception as e:
            raise Exception(f"Failed to get event schedule: {e}")
    
    async def _get_session_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取会话数据"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            
            return {
                "session_info": {
                    "name": session_obj.name,
                    "date": session_obj.date,
                    "circuit": session_obj.event.EventName,
                    "country": session_obj.event.Country,
                    "location": session_obj.event.Location
                },
                "drivers": session_obj.drivers,
                "total_drivers": len(session_obj.drivers)
            }
        except Exception as e:
            raise Exception(f"Failed to load session data: {e}")
    
    async def _get_session_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取会话结果"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            results = session_obj.results
            
            return {
                "session": session,
                "results": results.to_dict('records'),
                "total_results": len(results)
            }
        except Exception as e:
            raise Exception(f"Failed to get session results: {e}")
    
    async def _get_lap_times(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取圈速数据"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        driver = params.get("driver")
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            laps = session_obj.laps
            
            if driver:
                laps = laps[laps['Driver'] == driver]
            
            return {
                "session": session,
                "driver": driver,
                "lap_times": laps.to_dict('records'),
                "total_laps": len(laps)
            }
        except Exception as e:
            raise Exception(f"Failed to get lap times: {e}")
    
    async def _get_telemetry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取遥测数据"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        driver = params["driver"]
        lap = params.get("lap")
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            
            if lap:
                # 获取特定圈数的遥测数据
                driver_laps = session_obj.laps[session_obj.laps['Driver'] == driver]
                lap_data = driver_laps[driver_laps['LapNumber'] == lap]
                if len(lap_data) == 0:
                    raise Exception(f"Lap {lap} not found for driver {driver}")
                
                telemetry = lap_data.iloc[0].get_telemetry()
            else:
                # 获取车手所有遥测数据
                telemetry = session_obj.get_telemetry(driver)
            
            return {
                "driver": driver,
                "lap": lap,
                "telemetry": telemetry.to_dict('records'),
                "telemetry_channels": list(telemetry.columns)
            }
        except Exception as e:
            raise Exception(f"Failed to get telemetry: {e}")
    
    async def _get_weather_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气数据"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            weather = session_obj.weather_data
            
            return {
                "session": session,
                "weather_data": weather.to_dict('records'),
                "total_readings": len(weather)
            }
        except Exception as e:
            raise Exception(f"Failed to get weather data: {e}")
    
    async def _get_track_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取赛道状态"""
        year = params["year"]
        gp = params["gp"]
        session = params["session"]
        
        try:
            session_obj = get_session(year, gp, session)
            session_obj.load()
            track_status = session_obj.track_status
            
            return {
                "session": session,
                "track_status": track_status.to_dict('records'),
                "total_changes": len(track_status)
            }
        except Exception as e:
            raise Exception(f"Failed to get track status: {e}")
    
    async def _get_driver_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取车手信息"""
        year = params["year"]
        driver = params["driver"]
        
        try:
            # 获取车手信息
            session_obj = get_session(year, 1, 'R')  # 使用第一场比赛
            session_obj.load()
            
            driver_info = None
            for d in session_obj.drivers:
                if driver in [d['Abbreviation'], d['FullName'], str(d['DriverNumber'])]:
                    driver_info = d
                    break
            
            if not driver_info:
                raise Exception(f"Driver {driver} not found")
            
            return {
                "driver_info": driver_info,
                "year": year
            }
        except Exception as e:
            raise Exception(f"Failed to get driver info: {e}")
    
    async def _get_team_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取车队信息"""
        year = params["year"]
        team = params["team"]
        
        try:
            session_obj = get_session(year, 1, 'R')
            session_obj.load()
            
            team_drivers = []
            for driver in session_obj.drivers:
                if team.lower() in driver['TeamName'].lower():
                    team_drivers.append(driver)
            
            return {
                "team_name": team,
                "drivers": team_drivers,
                "year": year
            }
        except Exception as e:
            raise Exception(f"Failed to get team info: {e}")
    
    async def _get_driver_standings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取车手积分榜"""
        year = params["year"]
        round = params.get("round")
        
        try:
            if round:
                standings = self.ergast.get_driver_standings(season=year, round=round)
            else:
                standings = self.ergast.get_driver_standings(season=year)
            
            return {
                "year": year,
                "round": round,
                "standings": standings.content[0].to_dict('records')
            }
        except Exception as e:
            raise Exception(f"Failed to get driver standings: {e}")
    
    async def _get_constructor_standings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取车队积分榜"""
        year = params["year"]
        round = params.get("round")
        
        try:
            if round:
                standings = self.ergast.get_constructor_standings(season=year, round=round)
            else:
                standings = self.ergast.get_constructor_standings(season=year)
            
            return {
                "year": year,
                "round": round,
                "standings": standings.content[0].to_dict('records')
            }
        except Exception as e:
            raise Exception(f"Failed to get constructor standings: {e}")
    
    async def _get_historical_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取历史结果"""
        year = params["year"]
        gp = params.get("gp")
        
        try:
            if gp:
                results = self.ergast.get_race_results(season=year, round=gp)
            else:
                results = self.ergast.get_race_results(season=year)
            
            return {
                "year": year,
                "gp": gp,
                "results": results.content
            }
        except Exception as e:
            raise Exception(f"Failed to get historical results: {e}")
    
    async def _get_lap_records(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取圈速记录"""
        circuit = params["circuit"]
        
        try:
            # 使用Ergast API获取赛道记录
            records = self.ergast.get_circuit_info(circuit)
            
            return {
                "circuit": circuit,
                "records": records.content
            }
        except Exception as e:
            raise Exception(f"Failed to get lap records: {e}")
    
    async def _calculate_driver_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """计算车手统计"""
        year = params["year"]
        driver = params["driver"]
        gp = params.get("gp")
        
        try:
            if gp:
                session_obj = get_session(year, gp, 'R')
                session_obj.load()
                driver_laps = session_obj.laps[session_obj.laps['Driver'] == driver]
            else:
                # 获取整个赛季的数据
                schedule = get_event_schedule(year, include_testing=False)
                all_laps = []
                
                for event in schedule:
                    try:
                        session_obj = get_session(year, event['RoundNumber'], 'R')
                        session_obj.load()
                        driver_laps = session_obj.laps[session_obj.laps['Driver'] == driver]
                        all_laps.append(driver_laps)
                    except:
                        continue
                
                if all_laps:
                    driver_laps = pd.concat(all_laps)
                else:
                    driver_laps = pd.DataFrame()
            
            if len(driver_laps) == 0:
                raise Exception(f"No data found for driver {driver}")
            
            # 计算统计数据
            stats = {
                "driver": driver,
                "year": year,
                "gp": gp,
                "total_laps": len(driver_laps),
                "best_lap_time": driver_laps['LapTime'].min(),
                "average_lap_time": driver_laps['LapTime'].mean(),
                "fastest_lap": driver_laps.loc[driver_laps['LapTime'].idxmin()].to_dict() if len(driver_laps) > 0 else None,
                "pit_stops": len(driver_laps[driver_laps['PitOutTime'].notna()]),
                "positions_gained": 0,  # 需要更复杂的计算
                "dnf": len(driver_laps[driver_laps['IsPersonalBest'] == False])
            }
            
            return stats
        except Exception as e:
            raise Exception(f"Failed to calculate driver statistics: {e}")
    
    async def _compare_drivers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """比较车手"""
        year = params["year"]
        driver1 = params["driver1"]
        driver2 = params["driver2"]
        gp = params.get("gp")
        
        try:
            # 获取两位车手的数据
            stats1 = await self._calculate_driver_statistics({
                "year": year, "driver": driver1, "gp": gp
            })
            stats2 = await self._calculate_driver_statistics({
                "year": year, "driver": driver2, "gp": gp
            })
            
            comparison = {
                "year": year,
                "gp": gp,
                "driver1": stats1,
                "driver2": stats2,
                "lap_time_difference": abs(stats1.get("average_lap_time", 0) - stats2.get("average_lap_time", 0)),
                "total_laps_difference": stats1.get("total_laps", 0) - stats2.get("total_laps", 0)
            }
            
            return comparison
        except Exception as e:
            raise Exception(f"Failed to compare drivers: {e}")
    
    async def _configure_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """配置缓存"""
        enabled = params.get("enabled", self.cache_enabled)
        cache_dir = params.get("cache_dir", self.cache_dir)
        clear_cache = params.get("clear_cache", False)
        
        try:
            if clear_cache:
                fastf1.Cache.clear_cache()
            
            if enabled != self.cache_enabled:
                if enabled:
                    fastf1.Cache.enable_cache(cache_dir or './f1_cache')
                else:
                    fastf1.Cache.disable_cache()
                
                self.cache_enabled = enabled
            
            if cache_dir != self.cache_dir:
                self.cache_dir = cache_dir
                if enabled:
                    fastf1.Cache.enable_cache(cache_dir)
            
            return {
                "cache_enabled": self.cache_enabled,
                "cache_dir": self.cache_dir,
                "cache_cleared": clear_cache
            }
        except Exception as e:
            raise Exception(f"Failed to configure cache: {e}")
    
    async def _get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            cache_info = {
                "cache_enabled": self.cache_enabled,
                "cache_dir": self.cache_dir,
                "cache_size": "Unknown"  # FastF1 doesn't provide direct cache size info
            }
            
            return cache_info
        except Exception as e:
            raise Exception(f"Failed to get cache info: {e}")

# MCP服务器主循环
async def run_mcp_server():
    """运行MCP服务器"""
    server = FastF1MCPServer()
    
    sys.stderr.write("FastF1 MCP Server starting...\n")
    sys.stderr.flush()
    
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = await server.handle_request(request)
                
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json)
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
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
        sys.stderr.write("FastF1 MCP Server shutting down...\n")

if __name__ == "__main__":
    asyncio.run(run_mcp_server())