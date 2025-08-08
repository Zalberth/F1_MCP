#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实MCP服务器数据的F1性能对比分析
获取2024年奥地利大奖赛真实数据进行红牛vs迈凯轮对比
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('dark_background')

class RealMCPAnalyzer:
    """
    使用真实MCP服务器数据的F1性能分析器
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
    
    def analyze_session_results(self, session_data):
        """
        分析会话结果数据
        """
        if not session_data or 'results' not in session_data:
            return None
            
        results = session_data['results']
        team_performance = {}
        
        for result in results:
            team = result.get('TeamName', 'Unknown')
            if team not in team_performance:
                team_performance[team] = {
                    'drivers': [],
                    'positions': [],
                    'points': [],
                    'best_position': float('inf'),
                    'total_points': 0
                }
            
            team_performance[team]['drivers'].append(result.get('FullName', 'Unknown'))
            team_performance[team]['positions'].append(result.get('Position', 999))
            team_performance[team]['points'].append(result.get('Points', 0))
            team_performance[team]['best_position'] = min(
                team_performance[team]['best_position'], 
                result.get('Position', 999)
            )
            team_performance[team]['total_points'] += result.get('Points', 0)
        
        return team_performance
    
    def create_team_comparison_chart(self, team_data, team1, team2, race_name="奥地利大奖赛"):
        """
        创建车队对比图表
        """
        if not team_data or team1 not in team_data or team2 not in team_data:
            print(f"❌ 缺少 {team1} 或 {team2} 的数据")
            return
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('#0E1117')
        
        # 1. 车队积分对比
        teams = [team1, team2]
        points = [team_data[team1]['total_points'], team_data[team2]['total_points']]
        colors = [self.team_colors.get(team1, '#FF0000'), self.team_colors.get(team2, '#00FF00')]
        
        bars1 = ax1.bar(teams, points, color=colors, alpha=0.8)
        ax1.set_ylabel('积分')
        ax1.set_title('车队积分对比')
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, point in zip(bars1, points):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{point}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 2. 最佳排名对比
        best_positions = [team_data[team1]['best_position'], team_data[team2]['best_position']]
        
        bars2 = ax2.bar(teams, best_positions, color=colors, alpha=0.8)
        ax2.set_ylabel('排名 (数字越小越好)')
        ax2.set_title('最佳完赛排名')
        ax2.invert_yaxis()  # 反转Y轴，让第1名在顶部
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, pos in zip(bars2, best_positions):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height - 0.1,
                    f'P{pos}', ha='center', va='top', fontsize=12, fontweight='bold')
        
        # 3. 车手排名分布
        team1_positions = team_data[team1]['positions']
        team2_positions = team_data[team2]['positions']
        
        x1 = [f"{team1}\n车手{i+1}" for i in range(len(team1_positions))]
        x2 = [f"{team2}\n车手{i+1}" for i in range(len(team2_positions))]
        
        x_pos = np.arange(max(len(team1_positions), len(team2_positions)))
        width = 0.35
        
        # 填充较短的列表
        if len(team1_positions) < len(team2_positions):
            team1_positions.extend([None] * (len(team2_positions) - len(team1_positions)))
            x1.extend([f"{team1}\n车手{i+1}" for i in range(len(team1_positions), len(team2_positions))])
        elif len(team2_positions) < len(team1_positions):
            team2_positions.extend([None] * (len(team1_positions) - len(team2_positions)))
            x2.extend([f"{team2}\n车手{i+1}" for i in range(len(team2_positions), len(team1_positions))])
        
        # 只绘制有数据的柱子
        team1_valid = [pos for pos in team1_positions if pos is not None]
        team2_valid = [pos for pos in team2_positions if pos is not None]
        
        if team1_valid:
            bars3_1 = ax3.bar(x_pos[:len(team1_valid)] - width/2, team1_valid, width, 
                             label=team1, color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        if team2_valid:
            bars3_2 = ax3.bar(x_pos[:len(team2_valid)] + width/2, team2_valid, width, 
                             label=team2, color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        ax3.set_ylabel('完赛排名')
        ax3.set_title('车手排名对比')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([f'车手{i+1}' for i in range(len(x_pos))])
        ax3.legend()
        ax3.invert_yaxis()
        ax3.grid(True, alpha=0.3)
        
        # 添加数值标签
        if team1_valid:
            for i, (bar, pos) in enumerate(zip(bars3_1, team1_valid)):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height - 0.1,
                        f'P{pos}', ha='center', va='top', fontsize=10)
        if team2_valid:
            for i, (bar, pos) in enumerate(zip(bars3_2, team2_valid)):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height - 0.1,
                        f'P{pos}', ha='center', va='top', fontsize=10)
        
        # 4. 车队表现总结
        ax4.axis('off')
        
        # 创建表现总结文本
        summary_text = f"""
🏆 {race_name} 车队表现总结

{team1}:
• 总积分: {team_data[team1]['total_points']} 分
• 最佳排名: P{team_data[team1]['best_position']}
• 参赛车手: {len(team_data[team1]['drivers'])} 人
• 车手: {', '.join(team_data[team1]['drivers'])}

{team2}:
• 总积分: {team_data[team2]['total_points']} 分  
• 最佳排名: P{team_data[team2]['best_position']}
• 参赛车手: {len(team_data[team2]['drivers'])} 人
• 车手: {', '.join(team_data[team2]['drivers'])}

📊 对比结果:
• 积分优势: {team1 if team_data[team1]['total_points'] > team_data[team2]['total_points'] else team2}
• 排名优势: {team1 if team_data[team1]['best_position'] < team_data[team2]['best_position'] else team2}
• 积分差距: {abs(team_data[team1]['total_points'] - team_data[team2]['total_points'])} 分
        """
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1E1E1E', alpha=0.8))
        
        plt.tight_layout()
        plt.suptitle(f'2024 {race_name} - {team1} vs {team2} 车队表现对比', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.savefig(f'team_comparison_{race_name}.png', dpi=300, bbox_inches='tight', facecolor='#0E1117')
        plt.show()
    
    def print_detailed_analysis(self, team_data, team1, team2, race_name="奥地利大奖赛"):
        """
        打印详细分析报告
        """
        print(f"\n🏁 2024 {race_name} - {team1} vs {team2} 详细分析")
        print("=" * 80)
        
        if team1 not in team_data or team2 not in team_data:
            print(f"❌ 缺少 {team1} 或 {team2} 的数据")
            return
        
        # 车队总体表现
        print(f"\n🏆 车队总体表现:")
        print(f"{team1}:")
        print(f"  • 总积分: {team_data[team1]['total_points']} 分")
        print(f"  • 最佳排名: P{team_data[team1]['best_position']}")
        print(f"  • 参赛车手数: {len(team_data[team1]['drivers'])}")
        
        print(f"\n{team2}:")
        print(f"  • 总积分: {team_data[team2]['total_points']} 分")
        print(f"  • 最佳排名: P{team_data[team2]['best_position']}")
        print(f"  • 参赛车手数: {len(team_data[team2]['drivers'])}")
        
        # 对比分析
        points_diff = team_data[team1]['total_points'] - team_data[team2]['total_points']
        position_diff = team_data[team2]['best_position'] - team_data[team1]['best_position']
        
        print(f"\n📊 对比分析:")
        print(f"积分差距: {points_diff:+d} 分 ({'优势' if points_diff > 0 else '劣势'}: {team1})")
        print(f"最佳排名差距: {position_diff:+d} 位 ({'优势' if position_diff > 0 else '劣势'}: {team1})")
        
        # 车手表现详情
        print(f"\n👨‍🏎️ 车手表现详情:")
        print(f"{team1}:")
        for i, (driver, pos, points) in enumerate(zip(
            team_data[team1]['drivers'], 
            team_data[team1]['positions'], 
            team_data[team1]['points']
        )):
            print(f"  {i+1}. {driver}: P{pos}, {points} 分")
        
        print(f"\n{team2}:")
        for i, (driver, pos, points) in enumerate(zip(
            team_data[team2]['drivers'], 
            team_data[team2]['positions'], 
            team_data[team2]['points']
        )):
            print(f"  {i+1}. {driver}: P{pos}, {points} 分")
        
        # 战略建议
        print(f"\n💡 分析总结:")
        if points_diff > 0:
            print(f"• {team1} 在本场比赛中表现更出色，获得了更多积分")
        elif points_diff < 0:
            print(f"• {team2} 在本场比赛中表现更出色，获得了更多积分")
        else:
            print(f"• 两队在积分上打成平手，竞争激烈")
        
        if position_diff > 0:
            print(f"• {team1} 获得了更好的最佳完赛排名")
        elif position_diff < 0:
            print(f"• {team2} 获得了更好的最佳完赛排名")
        else:
            print(f"• 两队的最佳完赛排名相同")

def main():
    """主函数 - 演示如何使用MCP服务器数据"""
    print("🏎️ 基于真实MCP数据的F1性能对比分析")
    print("=" * 60)
    
    analyzer = RealMCPAnalyzer()
    
    # 这里需要通过MCP服务器获取真实数据
    # 示例：通过run_mcp调用get_session_results
    print("\n📡 准备获取2024年奥地利大奖赛数据...")
    print("\n💡 使用方法:")
    print("1. 调用 run_mcp('mcp.config.usrlocalmcp.fastf1', 'get_session_results', {")
    print("     'year': 2024,")
    print("     'gp': 'Austria',")
    print("     'session': 'R'")
    print("   })")
    print("2. 获取数据后调用 analyzer.analyze_session_results(data)")
    print("3. 使用 analyzer.create_team_comparison_chart() 生成对比图表")
    
    # 模拟数据结构示例
    sample_data = {
        'results': [
            {
                'DriverNumber': '1',
                'FullName': 'Max Verstappen',
                'TeamName': 'Red Bull Racing',
                'Position': 1,
                'Points': 25
            },
            {
                'DriverNumber': '11', 
                'FullName': 'Sergio Perez',
                'TeamName': 'Red Bull Racing',
                'Position': 4,
                'Points': 12
            },
            {
                'DriverNumber': '4',
                'FullName': 'Lando Norris', 
                'TeamName': 'McLaren',
                'Position': 2,
                'Points': 18
            },
            {
                'DriverNumber': '81',
                'FullName': 'Oscar Piastri',
                'TeamName': 'McLaren', 
                'Position': 3,
                'Points': 15
            }
        ]
    }
    
    print("\n📊 使用示例数据进行演示...")
    team_data = analyzer.analyze_session_results(sample_data)
    
    if team_data:
        analyzer.create_team_comparison_chart(team_data, 'Red Bull Racing', 'McLaren')
        analyzer.print_detailed_analysis(team_data, 'Red Bull Racing', 'McLaren')
    
    print("\n✅ 演示完成！")
    print("\n🔧 实际使用时的完整流程:")
    print("1. 通过MCP服务器获取真实比赛数据")
    print("2. 分析数据并提取车队表现指标")
    print("3. 生成多维度对比图表")
    print("4. 输出详细的性能分析报告")

if __name__ == "__main__":
    main()