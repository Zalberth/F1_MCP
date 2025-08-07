#!/usr/bin/env python3
"""
FastF1 MCP Server Usage Examples
演示如何使用FastF1 MCP服务器的各种功能
"""

import json
import asyncio
import sys
from datetime import datetime

class FastF1MCPClient:
    """简单的MCP客户端示例"""
    
    def __init__(self):
        self.request_id = 0
    
    def get_request_id(self):
        self.request_id += 1
        return self.request_id
    
    async def send_request(self, method, params=None):
        """发送MCP请求"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_request_id(),
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request)
        print(f"发送请求: {request_json}")
        
        # 在实际使用中，这里会发送到服务器
        # 现在我们只是打印请求格式
        
        return request
    
    async def demonstrate_usage(self):
        """演示各种用法"""
        print("=== FastF1 MCP Server 使用示例 ===\n")
        
        # 1. 获取赛事日程
        print("1. 获取2024年赛事日程:")
        await self.send_request("get_event_schedule", {
            "year": 2024,
            "include_testing": False
        })
        print()
        
        # 2. 获取特定会话数据
        print("2. 获取2024年摩纳哥大奖赛排位赛数据:")
        await self.send_request("get_session", {
            "year": 2024,
            "gp": "Monaco",
            "session": "Q"
        })
        print()
        
        # 3. 获取车手圈速
        print("3. 获取维斯塔潘在2024年摩纳哥的圈速:")
        await self.send_request("get_lap_times", {
            "year": 2024,
            "gp": "Monaco",
            "session": "R",
            "driver": "VER"
        })
        print()
        
        # 4. 获取遥测数据
        print("4. 获取汉密尔顿在2024年摩纳哥第10圈的遥测数据:")
        await self.send_request("get_telemetry", {
            "year": 2024,
            "gp": "Monaco",
            "session": "R",
            "driver": "HAM",
            "lap": 10
        })
        print()
        
        # 5. 获取天气数据
        print("5. 获取2024年摩纳哥正赛天气数据:")
        await self.send_request("get_weather_data", {
            "year": 2024,
            "gp": "Monaco",
            "session": "R"
        })
        print()
        
        # 6. 获取车手积分榜
        print("6. 获取2024年车手积分榜:")
        await self.send_request("get_driver_standings", {
            "year": 2024
        })
        print()
        
        # 7. 获取车队积分榜
        print("7. 获取2024年车队积分榜:")
        await self.send_request("get_constructor_standings", {
            "year": 2024
        })
        print()
        
        # 8. 比较车手
        print("8. 比较维斯塔潘和汉密尔顿在2024年的表现:")
        await self.send_request("compare_drivers", {
            "year": 2024,
            "driver1": "VER",
            "driver2": "HAM"
        })
        print()
        
        # 9. 计算车手统计
        print("9. 计算勒克莱尔在2024年摩纳哥的统计数据:")
        await self.send_request("calculate_driver_statistics", {
            "year": 2024,
            "driver": "LEC",
            "gp": "Monaco"
        })
        print()
        
        # 10. 获取历史结果
        print("10. 获取2023年所有比赛结果:")
        await self.send_request("get_historical_results", {
            "year": 2023
        })
        print()
        
        # 11. 获取赛道状态
        print("11. 获取2024年摩纳哥正赛赛道状态:")
        await self.send_request("get_track_status", {
            "year": 2024,
            "gp": "Monaco",
            "session": "R"
        })
        print()
        
        # 12. 配置缓存
        print("12. 配置缓存设置:")
        await self.send_request("configure_cache", {
            "enabled": True,
            "cache_dir": "./f1_cache",
            "clear_cache": False
        })
        print()

async def main():
    """主函数"""
    client = FastF1MCPClient()
    await client.demonstrate_usage()
    
    print("\n=== 使用说明 ===")
    print("1. 确保已安装FastF1: pip install fastf1")
    print("2. 启动服务器: python fastf1_mcp_server.py")
    print("3. 在MCP客户端中配置此服务器")
    print("4. 使用上述示例中的方法调用")
    print("\n支持的会话类型:")
    print("- FP1: 第一节自由练习")
    print("- FP2: 第二节自由练习")
    print("- FP3: 第三节自由练习")
    print("- Q: 排位赛")
    print("- SQ: 冲刺排位赛")
    print("- R: 正赛")
    print("- Sprint: 冲刺赛")
    print("\n支持的车手编号缩写:")
    print("- VER: Verstappen")
    print("- HAM: Hamilton")
    print("- LEC: Leclerc")
    print("- SAI: Sainz")
    print("- NOR: Norris")
    print("- RUS: Russell")
    print("- PER: Perez")
    print("- ALO: Alonso")
    print("- STR: Stroll")
    print("- HUL: Hulkenberg")
    print("- MAG: Magnussen")
    print("- BOT: Bottas")
    print("- ZHO: Zhou")
    print("- ALB: Albon")
    print("- SAR: Sargeant")
    print("- DEV: De Vries")
    print("- TSU: Tsunoda")
    print("- LAW: Lawson")
    print("- PIA: Piastri")
    print("- OCO: Ocon")
    print("- GAS: Gasly")

if __name__ == "__main__":
    asyncio.run(main())