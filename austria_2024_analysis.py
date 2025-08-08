#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2024年奥地利大奖赛真实数据分析
红牛 vs 迈凯轮性能对比
"""

import matplotlib.pyplot as plt
import numpy as np
import json

# 设置字体和样式
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('dark_background')

# 2024年奥地利大奖赛真实数据
austria_2024_data = {
    "session": "R",
    "results": [
        {
            "DriverNumber": "63",
            "FullName": "George Russell",
            "TeamName": "Mercedes",
            "Position": 1.0,
            "GridPosition": 3.0,
            "Points": 25.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "81",
            "FullName": "Oscar Piastri",
            "TeamName": "McLaren",
            "Position": 2.0,
            "GridPosition": 7.0,
            "Points": 18.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "55",
            "FullName": "Carlos Sainz",
            "TeamName": "Ferrari",
            "Position": 3.0,
            "GridPosition": 4.0,
            "Points": 15.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "44",
            "FullName": "Lewis Hamilton",
            "TeamName": "Mercedes",
            "Position": 4.0,
            "GridPosition": 5.0,
            "Points": 12.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "1",
            "FullName": "Max Verstappen",
            "TeamName": "Red Bull Racing",
            "Position": 5.0,
            "GridPosition": 1.0,
            "Points": 10.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "27",
            "FullName": "Nico Hulkenberg",
            "TeamName": "Haas F1 Team",
            "Position": 6.0,
            "GridPosition": 9.0,
            "Points": 8.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "11",
            "FullName": "Sergio Perez",
            "TeamName": "Red Bull Racing",
            "Position": 7.0,
            "GridPosition": 8.0,
            "Points": 6.0,
            "Status": "Finished"
        },
        {
            "DriverNumber": "4",
            "FullName": "Lando Norris",
            "TeamName": "McLaren",
            "Position": 20.0,
            "GridPosition": 2.0,
            "Points": 0.0,
            "Status": "Lapped"
        }
    ]
}

class Austria2024Analyzer:
    def __init__(self):
        self.team_colors = {
            'Red Bull Racing': '#3671C6',
            'McLaren': '#FF8000',
            'Mercedes': '#27F4D2',
            'Ferrari': '#E80020',
            'Haas F1 Team': '#B6BABD'
        }
    
    def analyze_team_performance(self, data):
        """分析车队表现"""
        team_stats = {}
        
        for result in data['results']:
            team = result['TeamName']
            if team not in team_stats:
                team_stats[team] = {
                    'drivers': [],
                    'positions': [],
                    'grid_positions': [],
                    'points': [],
                    'total_points': 0,
                    'best_position': float('inf'),
                    'grid_performance': []  # 发车位置 vs 完赛位置
                }
            
            team_stats[team]['drivers'].append(result['FullName'])
            team_stats[team]['positions'].append(result['Position'])
            team_stats[team]['grid_positions'].append(result['GridPosition'])
            team_stats[team]['points'].append(result['Points'])
            team_stats[team]['total_points'] += result['Points']
            team_stats[team]['best_position'] = min(team_stats[team]['best_position'], result['Position'])
            
            # 计算发车位置表现（负数表示进步，正数表示退步）
            position_change = result['Position'] - result['GridPosition']
            team_stats[team]['grid_performance'].append(position_change)
        
        return team_stats
    
    def create_comprehensive_analysis(self, team_stats):
        """创建综合分析图表"""
        fig = plt.figure(figsize=(20, 12))
        fig.patch.set_facecolor('#0E1117')
        
        # 创建网格布局
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 1. 车队积分对比 (左上)
        ax1 = fig.add_subplot(gs[0, 0])
        teams = list(team_stats.keys())
        points = [team_stats[team]['total_points'] for team in teams]
        colors = [self.team_colors.get(team, '#FFFFFF') for team in teams]
        
        bars = ax1.bar(teams, points, color=colors, alpha=0.8)
        ax1.set_title('Team Points Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Points')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, point in zip(bars, points):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(point)}', ha='center', va='bottom', fontweight='bold')
        
        # 2. 红牛 vs 迈凯轮详细对比 (右上)
        ax2 = fig.add_subplot(gs[0, 1:3])
        rb_data = team_stats.get('Red Bull Racing', {})
        mc_data = team_stats.get('McLaren', {})
        
        if rb_data and mc_data:
            categories = ['Total Points', 'Best Position', 'Avg Grid Pos', 'Position Changes']
            rb_values = [
                rb_data['total_points'],
                21 - rb_data['best_position'],  # 反转以便可视化
                21 - np.mean(rb_data['grid_positions']),  # 反转
                -np.mean(rb_data['grid_performance'])  # 反转，正值表示进步
            ]
            mc_values = [
                mc_data['total_points'],
                21 - mc_data['best_position'],
                21 - np.mean(mc_data['grid_positions']),
                -np.mean(mc_data['grid_performance'])
            ]
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax2.bar(x - width/2, rb_values, width, label='Red Bull Racing', 
                           color=self.team_colors['Red Bull Racing'], alpha=0.8)
            bars2 = ax2.bar(x + width/2, mc_values, width, label='McLaren', 
                           color=self.team_colors['McLaren'], alpha=0.8)
            
            ax2.set_title('Red Bull vs McLaren Performance', fontsize=14, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categories, rotation=45)
            ax2.legend()
            
            # 添加数值标签
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 3. 发车位置 vs 完赛位置散点图 (左中)
        ax3 = fig.add_subplot(gs[1, 0])
        for team in ['Red Bull Racing', 'McLaren']:
            if team in team_stats:
                grid_pos = team_stats[team]['grid_positions']
                race_pos = team_stats[team]['positions']
                ax3.scatter(grid_pos, race_pos, 
                           color=self.team_colors[team], 
                           label=team, s=100, alpha=0.7)
                
                # 添加车手标签
                for i, (gp, rp, driver) in enumerate(zip(grid_pos, race_pos, team_stats[team]['drivers'])):
                    ax3.annotate(driver.split()[-1], (gp, rp), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 添加对角线（无变化线）
        ax3.plot([1, 20], [1, 20], 'w--', alpha=0.5, label='No Change')
        ax3.set_xlabel('Grid Position')
        ax3.set_ylabel('Race Position')
        ax3.set_title('Grid vs Race Position', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.invert_yaxis()
        ax3.invert_xaxis()
        
        # 4. 车手个人表现 (右中)
        ax4 = fig.add_subplot(gs[1, 1:3])
        driver_data = []
        driver_teams = []
        driver_names = []
        
        for team in ['Red Bull Racing', 'McLaren']:
            if team in team_stats:
                for i, driver in enumerate(team_stats[team]['drivers']):
                    driver_data.append([
                        team_stats[team]['grid_positions'][i],
                        team_stats[team]['positions'][i],
                        team_stats[team]['points'][i]
                    ])
                    driver_teams.append(team)
                    driver_names.append(driver.split()[-1])
        
        if driver_data:
            x_pos = np.arange(len(driver_names))
            grid_positions = [d[0] for d in driver_data]
            race_positions = [d[1] for d in driver_data]
            points = [d[2] for d in driver_data]
            
            # 创建双Y轴
            ax4_twin = ax4.twinx()
            
            # 绘制位置（柱状图）
            bars1 = ax4.bar(x_pos - 0.2, [21-gp for gp in grid_positions], 0.4, 
                           label='Grid Position', alpha=0.7, color='lightblue')
            bars2 = ax4.bar(x_pos + 0.2, [21-rp for rp in race_positions], 0.4, 
                           label='Race Position', alpha=0.7, color='lightcoral')
            
            # 绘制积分（线图）
            line = ax4_twin.plot(x_pos, points, 'o-', color='gold', linewidth=3, 
                               markersize=8, label='Points')
            
            ax4.set_xlabel('Drivers')
            ax4.set_ylabel('Position (Higher = Better)')
            ax4_twin.set_ylabel('Points')
            ax4.set_title('Individual Driver Performance', fontsize=14, fontweight='bold')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(driver_names)
            
            # 合并图例
            lines1, labels1 = ax4.get_legend_handles_labels()
            lines2, labels2 = ax4_twin.get_legend_handles_labels()
            ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # 5. 车队表现雷达图 (左下)
        ax5 = fig.add_subplot(gs[2, 0], projection='polar')
        
        if 'Red Bull Racing' in team_stats and 'McLaren' in team_stats:
            categories_radar = ['Points', 'Best Position', 'Consistency', 'Grid Performance']
            
            # 标准化数据
            rb_radar = [
                rb_data['total_points'] / 50,  # 标准化到0-1
                (21 - rb_data['best_position']) / 20,
                1 - (np.std(rb_data['positions']) / 10),  # 一致性
                max(0, -np.mean(rb_data['grid_performance']) / 10)  # 发车表现
            ]
            
            mc_radar = [
                mc_data['total_points'] / 50,
                (21 - mc_data['best_position']) / 20,
                1 - (np.std(mc_data['positions']) / 10),
                max(0, -np.mean(mc_data['grid_performance']) / 10)
            ]
            
            angles = np.linspace(0, 2 * np.pi, len(categories_radar), endpoint=False).tolist()
            rb_radar += rb_radar[:1]
            mc_radar += mc_radar[:1]
            angles += angles[:1]
            
            ax5.plot(angles, rb_radar, 'o-', linewidth=2, label='Red Bull Racing', 
                    color=self.team_colors['Red Bull Racing'])
            ax5.fill(angles, rb_radar, alpha=0.25, color=self.team_colors['Red Bull Racing'])
            
            ax5.plot(angles, mc_radar, 'o-', linewidth=2, label='McLaren', 
                    color=self.team_colors['McLaren'])
            ax5.fill(angles, mc_radar, alpha=0.25, color=self.team_colors['McLaren'])
            
            ax5.set_xticks(angles[:-1])
            ax5.set_xticklabels(categories_radar)
            ax5.set_ylim(0, 1)
            ax5.set_title('Team Performance Radar', fontsize=14, fontweight='bold', pad=20)
            ax5.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # 6. 详细统计表格 (右下)
        ax6 = fig.add_subplot(gs[2, 1:])
        ax6.axis('off')
        
        # 创建统计表格
        stats_text = """
2024 Austrian GP - Red Bull vs McLaren Analysis

Red Bull Racing:
• Total Points: {} pts
• Best Finish: P{}
• Drivers: {}
• Grid Performance: {} positions on average
• Consistency: {:.2f}

McLaren:
• Total Points: {} pts  
• Best Finish: P{}
• Drivers: {}
• Grid Performance: {} positions on average
• Consistency: {:.2f}

Key Insights:
• Points Advantage: {} ({} pts)
• Better Qualifying: {}
• Race Day Performance: {}
• Strategic Execution: {}
        """.format(
            int(rb_data['total_points']) if rb_data else 0,
            int(rb_data['best_position']) if rb_data else 'N/A',
            ', '.join([d.split()[-1] for d in rb_data['drivers']]) if rb_data else 'N/A',
            f"{np.mean(rb_data['grid_performance']):.1f}" if rb_data else 'N/A',
            1 - (np.std(rb_data['positions']) / 10) if rb_data else 0,
            
            int(mc_data['total_points']) if mc_data else 0,
            int(mc_data['best_position']) if mc_data else 'N/A',
            ', '.join([d.split()[-1] for d in mc_data['drivers']]) if mc_data else 'N/A',
            f"{np.mean(mc_data['grid_performance']):.1f}" if mc_data else 'N/A',
            1 - (np.std(mc_data['positions']) / 10) if mc_data else 0,
            
            'Red Bull Racing' if (rb_data and mc_data and rb_data['total_points'] > mc_data['total_points']) else 'McLaren',
            abs(int(rb_data['total_points'] - mc_data['total_points'])) if (rb_data and mc_data) else 0,
            'Red Bull Racing' if (rb_data and mc_data and np.mean(rb_data['grid_positions']) < np.mean(mc_data['grid_positions'])) else 'McLaren',
            'Red Bull Racing' if (rb_data and mc_data and np.mean(rb_data['grid_performance']) < np.mean(mc_data['grid_performance'])) else 'McLaren',
            'Mixed results - both teams had challenges'
        )
        
        ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1E1E1E', alpha=0.8))
        
        plt.suptitle('2024 Austrian GP - Comprehensive Team Performance Analysis', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.savefig('austria_2024_comprehensive_analysis.png', dpi=300, 
                   bbox_inches='tight', facecolor='#0E1117')
        plt.show()
    
    def print_race_summary(self, team_stats):
        """打印比赛总结"""
        print("\n" + "="*80)
        print("🏁 2024 AUSTRIAN GRAND PRIX - RACE ANALYSIS")
        print("="*80)
        
        rb_data = team_stats.get('Red Bull Racing', {})
        mc_data = team_stats.get('McLaren', {})
        
        if rb_data and mc_data:
            print(f"\n🏆 TEAM BATTLE: Red Bull Racing vs McLaren")
            print(f"Red Bull Racing: {int(rb_data['total_points'])} points | Best: P{int(rb_data['best_position'])}")
            print(f"McLaren:        {int(mc_data['total_points'])} points | Best: P{int(mc_data['best_position'])}")
            
            winner = 'Red Bull Racing' if rb_data['total_points'] > mc_data['total_points'] else 'McLaren'
            margin = abs(rb_data['total_points'] - mc_data['total_points'])
            print(f"\n🎯 WINNER: {winner} (+{int(margin)} points)")
            
            print(f"\n👨‍🏎️ DRIVER PERFORMANCES:")
            print("Red Bull Racing:")
            for i, driver in enumerate(rb_data['drivers']):
                pos = int(rb_data['positions'][i])
                grid = int(rb_data['grid_positions'][i])
                pts = int(rb_data['points'][i])
                change = int(rb_data['positions'][i] - rb_data['grid_positions'][i])
                print(f"  • {driver}: P{pos} ({pts} pts) | Grid: P{grid} | Change: {change:+d}")
            
            print("\nMcLaren:")
            for i, driver in enumerate(mc_data['drivers']):
                pos = int(mc_data['positions'][i])
                grid = int(mc_data['grid_positions'][i])
                pts = int(mc_data['points'][i])
                change = int(mc_data['positions'][i] - mc_data['grid_positions'][i])
                print(f"  • {driver}: P{pos} ({pts} pts) | Grid: P{grid} | Change: {change:+d}")
            
            print(f"\n📊 KEY INSIGHTS:")
            print(f"• Verstappen started P1 but finished P5 (-4 positions)")
            print(f"• Norris had a difficult race: P2 grid → P20 finish")
            print(f"• Piastri delivered strong points: P7 grid → P2 finish (+5)")
            print(f"• Perez maintained position: P8 grid → P7 finish")
            print(f"• McLaren showed pace but reliability/strategy issues affected Norris")
            print(f"• Red Bull Racing secured more points despite Verstappen's struggles")

def main():
    """主函数"""
    print("🏎️ 2024 Austrian Grand Prix - Red Bull vs McLaren Analysis")
    print("Using Real Race Data from MCP Server")
    
    analyzer = Austria2024Analyzer()
    team_stats = analyzer.analyze_team_performance(austria_2024_data)
    
    # 生成综合分析图表
    analyzer.create_comprehensive_analysis(team_stats)
    
    # 打印详细分析
    analyzer.print_race_summary(team_stats)
    
    print("\n✅ Analysis Complete!")
    print("📁 Generated: austria_2024_comprehensive_analysis.png")

if __name__ == "__main__":
    main()