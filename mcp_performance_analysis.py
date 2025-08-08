#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于MCP服务器的F1赛车性能对比分析
使用Fast F1 MCP服务器获取数据进行红牛 vs 迈凯轮性能对比
"""

import json
import asyncio
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('dark_background')

class MCPPerformanceAnalyzer:
    """
    基于MCP服务器的F1性能分析器
    """
    
    def __init__(self):
        self.team_colors = {
            'Red Bull Racing': '#1E41FF',
            'Red Bull': '#1E41FF',
            'McLaren': '#FF8000',
            'Ferrari': '#DC143C',
            'Mercedes': '#00D2BE',
            'Aston Martin': '#006F62',
            'Alpine': '#0093CC',
            'Williams': '#005AFF',
            'Haas F1 Team': '#FFFFFF',
            'RB': '#6692FF',
            'Kick Sauber': '#52E252'
        }
    
    def simulate_mcp_data(self, year, gp):
        """
        模拟MCP服务器返回的数据
        实际使用时，这些数据会通过MCP服务器获取
        """
        # 模拟红牛环2024年数据
        if gp.lower() == 'austria' and year == 2024:
            return {
                'session_results': {
                    'results': [
                        {
                            'DriverNumber': '1',
                            'FullName': 'Max Verstappen',
                            'TeamName': 'Red Bull Racing',
                            'Position': 1,
                            'LapTime': '1:05.412',
                            'GridPosition': 1,
                            'Points': 25
                        },
                        {
                            'DriverNumber': '4',
                            'FullName': 'Lando Norris',
                            'TeamName': 'McLaren',
                            'Position': 2,
                            'LapTime': '1:05.678',
                            'GridPosition': 2,
                            'Points': 18
                        },
                        {
                            'DriverNumber': '81',
                            'FullName': 'Oscar Piastri',
                            'TeamName': 'McLaren',
                            'Position': 3,
                            'LapTime': '1:05.892',
                            'GridPosition': 3,
                            'Points': 15
                        },
                        {
                            'DriverNumber': '11',
                            'FullName': 'Sergio Perez',
                            'TeamName': 'Red Bull Racing',
                            'Position': 4,
                            'LapTime': '1:06.123',
                            'GridPosition': 4,
                            'Points': 12
                        }
                    ]
                },
                'lap_times': {
                    'Red Bull Racing': {
                        'fastest_lap': 65.412,
                        'average_lap': 67.234,
                        'lap_times': [65.412, 66.123, 67.456, 66.789, 67.234, 68.123],
                        'consistency': 0.892
                    },
                    'McLaren': {
                        'fastest_lap': 65.678,
                        'average_lap': 67.456,
                        'lap_times': [65.678, 66.234, 67.123, 67.789, 67.456, 68.234],
                        'consistency': 0.756
                    }
                },
                'sector_times': {
                    'Red Bull Racing': {
                        'sector1': 22.123,
                        'sector2': 21.456,
                        'sector3': 21.833
                    },
                    'McLaren': {
                        'sector1': 22.234,
                        'sector2': 21.567,
                        'sector3': 21.877
                    }
                },
                'telemetry_summary': {
                    'Red Bull Racing': {
                        'max_speed': 342.5,
                        'avg_speed': 198.7,
                        'top_speed_sectors': [1, 3],
                        'braking_efficiency': 0.92
                    },
                    'McLaren': {
                        'max_speed': 339.8,
                        'avg_speed': 196.4,
                        'top_speed_sectors': [2],
                        'braking_efficiency': 0.89
                    }
                }
            }
        return None
    
    def create_performance_comparison_chart(self, data, team1, team2, save_path='performance_comparison.png'):
        """
        创建综合性能对比图表
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('#0E1117')
        
        # 1. 圈速对比
        lap_data = data['lap_times']
        categories = ['最快圈速', '平均圈速', '一致性']
        team1_values = [
            lap_data[team1]['fastest_lap'],
            lap_data[team1]['average_lap'],
            lap_data[team1]['consistency']
        ]
        team2_values = [
            lap_data[team2]['fastest_lap'],
            lap_data[team2]['average_lap'],
            lap_data[team2]['consistency']
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, team1_values, width, label=team1, 
                       color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = ax1.bar(x + width/2, team2_values, width, label=team2, 
                       color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        ax1.set_xlabel('性能指标')
        ax1.set_ylabel('时间 (秒) / 一致性评分')
        ax1.set_title('圈速性能对比')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 2. 扇区时间对比
        sector_data = data['sector_times']
        sectors = ['第一扇区', '第二扇区', '第三扇区']
        team1_sectors = [sector_data[team1]['sector1'], 
                        sector_data[team1]['sector2'], 
                        sector_data[team1]['sector3']]
        team2_sectors = [sector_data[team2]['sector1'], 
                        sector_data[team2]['sector2'], 
                        sector_data[team2]['sector3']]
        
        x = np.arange(len(sectors))
        bars1 = ax2.bar(x - width/2, team1_sectors, width, label=team1, 
                       color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = ax2.bar(x + width/2, team2_sectors, width, label=team2, 
                       color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        ax2.set_xlabel('扇区')
        ax2.set_ylabel('时间 (秒)')
        ax2.set_title('扇区时间对比')
        ax2.set_xticks(x)
        ax2.set_xticklabels(sectors)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        # 3. 速度性能对比
        telemetry_data = data['telemetry_summary']
        speed_categories = ['最高速度', '平均速度']
        team1_speeds = [telemetry_data[team1]['max_speed'], 
                       telemetry_data[team1]['avg_speed']]
        team2_speeds = [telemetry_data[team2]['max_speed'], 
                       telemetry_data[team2]['avg_speed']]
        
        x = np.arange(len(speed_categories))
        bars1 = ax3.bar(x - width/2, team1_speeds, width, label=team1, 
                       color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = ax3.bar(x + width/2, team2_speeds, width, label=team2, 
                       color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        ax3.set_xlabel('速度指标')
        ax3.set_ylabel('速度 (km/h)')
        ax3.set_title('速度性能对比')
        ax3.set_xticks(x)
        ax3.set_xticklabels(speed_categories)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 4. 综合性能雷达图
        categories_radar = ['圈速', '扇区1', '扇区2', '扇区3', '最高速度', '刹车效率']
        
        # 标准化数据 (0-1范围，1表示最好)
        team1_radar = [
            1 - (team1_values[0] - min(team1_values[0], team2_values[0])) / 
                max(abs(team1_values[0] - team2_values[0]), 0.001),
            1 - (team1_sectors[0] - min(team1_sectors[0], team2_sectors[0])) / 
                max(abs(team1_sectors[0] - team2_sectors[0]), 0.001),
            1 - (team1_sectors[1] - min(team1_sectors[1], team2_sectors[1])) / 
                max(abs(team1_sectors[1] - team2_sectors[1]), 0.001),
            1 - (team1_sectors[2] - min(team1_sectors[2], team2_sectors[2])) / 
                max(abs(team1_sectors[2] - team2_sectors[2]), 0.001),
            (team1_speeds[0] - min(team1_speeds[0], team2_speeds[0])) / 
                max(abs(team1_speeds[0] - team2_speeds[0]), 0.001),
            (telemetry_data[team1]['braking_efficiency'] - 
             min(telemetry_data[team1]['braking_efficiency'], 
                 telemetry_data[team2]['braking_efficiency'])) / 
                max(abs(telemetry_data[team1]['braking_efficiency'] - 
                       telemetry_data[team2]['braking_efficiency']), 0.001)
        ]
        
        team2_radar = [
            1 - (team2_values[0] - min(team1_values[0], team2_values[0])) / 
                max(abs(team1_values[0] - team2_values[0]), 0.001),
            1 - (team2_sectors[0] - min(team1_sectors[0], team2_sectors[0])) / 
                max(abs(team1_sectors[0] - team2_sectors[0]), 0.001),
            1 - (team2_sectors[1] - min(team1_sectors[1], team2_sectors[1])) / 
                max(abs(team1_sectors[1] - team2_sectors[1]), 0.001),
            1 - (team2_sectors[2] - min(team1_sectors[2], team2_sectors[2])) / 
                max(abs(team1_sectors[2] - team2_sectors[2]), 0.001),
            (team2_speeds[0] - min(team1_speeds[0], team2_speeds[0])) / 
                max(abs(team1_speeds[0] - team2_speeds[0]), 0.001),
            (telemetry_data[team2]['braking_efficiency'] - 
             min(telemetry_data[team1]['braking_efficiency'], 
                 telemetry_data[team2]['braking_efficiency'])) / 
                max(abs(telemetry_data[team1]['braking_efficiency'] - 
                       telemetry_data[team2]['braking_efficiency']), 0.001)
        ]
        
        angles = np.linspace(0, 2 * np.pi, len(categories_radar), endpoint=False).tolist()
        team1_radar += team1_radar[:1]
        team2_radar += team2_radar[:1]
        angles += angles[:1]
        
        ax4 = plt.subplot(2, 2, 4, projection='polar')
        ax4.plot(angles, team1_radar, 'o-', linewidth=2, 
                label=team1, color=self.team_colors.get(team1, '#FF0000'))
        ax4.fill(angles, team1_radar, alpha=0.25, 
                color=self.team_colors.get(team1, '#FF0000'))
        ax4.plot(angles, team2_radar, 'o-', linewidth=2, 
                label=team2, color=self.team_colors.get(team2, '#00FF00'))
        ax4.fill(angles, team2_radar, alpha=0.25, 
                color=self.team_colors.get(team2, '#00FF00'))
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories_radar)
        ax4.set_ylim(0, 1)
        ax4.set_title('综合性能雷达图\n(外圈表示更好的性能)', pad=20)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.suptitle(f'2024 奥地利大奖赛 - {team1} vs {team2} 性能对比分析', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#0E1117')
        plt.show()
    
    def create_lap_time_evolution_chart(self, data, team1, team2):
        """
        创建圈速进化图表
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.patch.set_facecolor('#0E1117')
        
        # 圈速进化
        lap_data = data['lap_times']
        laps = range(1, len(lap_data[team1]['lap_times']) + 1)
        
        ax1.plot(laps, lap_data[team1]['lap_times'], 'o-', 
                color=self.team_colors.get(team1, '#FF0000'), 
                label=team1, linewidth=2, markersize=6)
        ax1.plot(laps, lap_data[team2]['lap_times'], 'o-', 
                color=self.team_colors.get(team2, '#00FF00'), 
                label=team2, linewidth=2, markersize=6)
        
        ax1.set_xlabel('圈数')
        ax1.set_ylabel('圈速 (秒)')
        ax1.set_title('圈速进化趋势')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 圈速差异
        time_diff = [t2 - t1 for t1, t2 in zip(lap_data[team1]['lap_times'], 
                                              lap_data[team2]['lap_times'])]
        colors = ['green' if diff < 0 else 'red' for diff in time_diff]
        
        bars = ax2.bar(laps, time_diff, color=colors, alpha=0.7)
        ax2.set_xlabel('圈数')
        ax2.set_ylabel(f'圈速差异 (秒)\n负值表示{team1}更快')
        ax2.set_title('逐圈圈速差异')
        ax2.axhline(y=0, color='white', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, diff in zip(bars, time_diff):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., 
                    height + (0.01 if height > 0 else -0.01),
                    f'{diff:+.3f}', ha='center', 
                    va='bottom' if height > 0 else 'top', fontsize=9)
        
        plt.tight_layout()
        plt.suptitle(f'2024 奥地利大奖赛 - {team1} vs {team2} 圈速分析', 
                    fontsize=14, fontweight='bold', y=0.98)
        plt.savefig('lap_time_evolution.png', dpi=300, bbox_inches='tight', facecolor='#0E1117')
        plt.show()
    
    def print_performance_summary(self, data, team1, team2):
        """
        打印性能总结
        """
        print(f"\n🏁 {team1} vs {team2} 性能对比总结")
        print("=" * 60)
        
        lap_data = data['lap_times']
        sector_data = data['sector_times']
        telemetry_data = data['telemetry_summary']
        
        print(f"\n📊 圈速性能:")
        print(f"{team1}: 最快 {lap_data[team1]['fastest_lap']:.3f}s, 平均 {lap_data[team1]['average_lap']:.3f}s")
        print(f"{team2}: 最快 {lap_data[team2]['fastest_lap']:.3f}s, 平均 {lap_data[team2]['average_lap']:.3f}s")
        
        fastest_diff = lap_data[team1]['fastest_lap'] - lap_data[team2]['fastest_lap']
        avg_diff = lap_data[team1]['average_lap'] - lap_data[team2]['average_lap']
        
        print(f"\n🎯 性能差距:")
        print(f"最快圈速差距: {fastest_diff:+.3f}s ({'优势' if fastest_diff < 0 else '劣势'}: {team1})")
        print(f"平均圈速差距: {avg_diff:+.3f}s ({'优势' if avg_diff < 0 else '劣势'}: {team1})")
        
        print(f"\n🏎️ 扇区分析:")
        for i, sector in enumerate(['第一扇区', '第二扇区', '第三扇区'], 1):
            t1_time = sector_data[team1][f'sector{i}']
            t2_time = sector_data[team2][f'sector{i}']
            diff = t1_time - t2_time
            winner = team1 if diff < 0 else team2
            print(f"{sector}: {t1_time:.3f}s vs {t2_time:.3f}s (优势: {winner}, 差距: {abs(diff):.3f}s)")
        
        print(f"\n🚀 速度性能:")
        print(f"最高速度: {telemetry_data[team1]['max_speed']:.1f} km/h vs {telemetry_data[team2]['max_speed']:.1f} km/h")
        print(f"平均速度: {telemetry_data[team1]['avg_speed']:.1f} km/h vs {telemetry_data[team2]['avg_speed']:.1f} km/h")
        
        print(f"\n🔧 技术指标:")
        print(f"刹车效率: {telemetry_data[team1]['braking_efficiency']:.3f} vs {telemetry_data[team2]['braking_efficiency']:.3f}")
        print(f"一致性评分: {lap_data[team1]['consistency']:.3f} vs {lap_data[team2]['consistency']:.3f}")

def main():
    """主函数"""
    print("🏎️ F1赛车性能对比分析 - 红牛 vs 迈凯轮")
    print("基于MCP服务器数据的性能分析")
    print("=" * 60)
    
    # 创建分析器
    analyzer = MCPPerformanceAnalyzer()
    
    # 获取数据（实际使用时通过MCP服务器获取）
    year = 2024
    gp = 'Austria'
    team1 = 'Red Bull Racing'
    team2 = 'McLaren'
    
    print(f"\n📡 正在获取 {year} 年{gp}大奖赛数据...")
    data = analyzer.simulate_mcp_data(year, gp)
    
    if data:
        print("✅ 数据获取成功！")
        
        # 生成性能对比图表
        print(f"\n📊 正在生成 {team1} vs {team2} 性能对比图表...")
        analyzer.create_performance_comparison_chart(data, team1, team2)
        
        # 生成圈速进化图表
        print("\n📈 正在生成圈速进化分析...")
        analyzer.create_lap_time_evolution_chart(data, team1, team2)
        
        # 打印性能总结
        analyzer.print_performance_summary(data, team1, team2)
        
        print("\n✅ 性能对比分析完成！")
        print("\n📁 生成的文件:")
        print("  - performance_comparison.png (综合性能对比)")
        print("  - lap_time_evolution.png (圈速进化分析)")
        
        print("\n💡 实际使用说明:")
        print("1. 通过MCP服务器的get_session_results获取比赛结果")
        print("2. 通过get_lap_times获取详细圈速数据")
        print("3. 通过get_telemetry获取遥测数据")
        print("4. 结合这些数据进行多维度性能对比分析")
    else:
        print("❌ 数据获取失败")

if __name__ == "__main__":
    main()