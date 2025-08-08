#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1赛季车手位置变化分析 - 优化版本（合并同名车手）
只获取发车位置和完赛位置数据，减少数据下载量
合并同一车手在不同车队的数据
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import fastf1
import argparse
import sys
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表样式
plt.style.use('dark_background')
sns.set_palette("husl")

# 启用FastF1缓存
fastf1.Cache.enable_cache('fastf1_cache')

class F1SeasonAnalysisOptimized:
    def __init__(self, year):
        self.year = year
        self.season_data = []
        self.driver_stats = defaultdict(list)  # 按车手姓名合并数据
        self.driver_teams = {}  # 记录车手的主要车队
        self.team_colors = {
            'Red Bull Racing': '#4781D7',
            'Mercedes': '#00D7B6', 
            'Ferrari': '#ED1131',
            'McLaren': '#F47600',
            'Alpine': '#00A1E8',
            'AlphaTauri': '#6C98FF',
            'Aston Martin': '#229971',
            'Williams': '#1868DB',
            'Alfa Romeo': '#01C00E',
            'Haas F1 Team': '#9C9FA2',
            'Racing Bulls': '#6C98FF',
            'Kick Sauber': '#01C00E',
            'RB': '#6C98FF',
            'Sauber': '#01C00E'
        }
        
    @staticmethod
    def normalize_driver_name(first_name, last_name):
        """标准化车手姓名"""
        if "Antonelli" in str(last_name):
            return "Kimi Antonelli"
        return f"{first_name} {last_name}"
    
    def load_season_data_minimal(self):
        """只加载必要的位置数据，大幅减少数据下载量，合并同名车手"""
        try:
            print(f"🏎️ 正在加载{self.year}年F1赛季位置数据（优化版本 - 合并同名车手）...")
            
            # 获取赛季赛程
            schedule = fastf1.get_event_schedule(self.year)
            race_events = schedule[schedule['EventFormat'] != 'testing']
            
            total_races = len(race_events)
            print(f"📅 找到{total_races}场比赛")
            
            for idx, event in race_events.iterrows():
                try:
                    gp_name = event['EventName']
                    round_num = event['RoundNumber']
                    
                    print(f"📊 正在处理第{round_num}轮: {gp_name}...", end=" ")
                    
                    # 只加载比赛结果，不加载遥测数据
                    session = fastf1.get_session(self.year, gp_name, 'R')
                    # 只加载结果数据，跳过遥测数据
                    session.load(telemetry=False, weather=False, messages=False)
                    
                    results = session.results
                    
                    # 只提取必要的位置信息
                    for _, row in results.iterrows():
                        driver_name = self.normalize_driver_name(row['FirstName'], row['LastName'])
                        team_name = row['TeamName']
                        
                        # 处理完赛位置（未完赛认为是最后一名）
                        finish_pos = row['Position']
                        if pd.isna(finish_pos):
                            finish_pos = len(results) + 1
                        
                        grid_pos = row['GridPosition']
                        if pd.isna(grid_pos):
                            grid_pos = len(results) + 1
                        
                        # 计算位置变化
                        position_change = int(grid_pos) - int(finish_pos)
                        
                        # 记录车手的主要车队（参赛场次最多的车队）
                        if driver_name not in self.driver_teams:
                            self.driver_teams[driver_name] = {}
                        if team_name not in self.driver_teams[driver_name]:
                            self.driver_teams[driver_name][team_name] = 0
                        self.driver_teams[driver_name][team_name] += 1
                        
                        # 只保存必要数据
                        race_entry = {
                            'round': round_num,
                            'race': gp_name,
                            'driver': driver_name,
                            'team': team_name,
                            'grid': int(grid_pos),
                            'finish': int(finish_pos),
                            'position_change': position_change
                        }
                        
                        self.season_data.append(race_entry)
                        # 按车手姓名合并数据，不区分车队
                        self.driver_stats[driver_name].append(position_change)
                    
                    print("✅")
                    
                except Exception as e:
                    print(f"⚠️ 跳过: {e}")
                    continue
            
            print(f"\n✅ 数据加载完成，共处理{len(self.season_data)}条位置记录")
            print(f"📊 共有{len(self.driver_stats)}位不同车手参赛")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            sys.exit(1)
    
    def calculate_driver_averages(self):
        """计算每位车手的年度平均位置变化（合并同名车手数据）"""
        driver_averages = {}
        
        for driver, changes in self.driver_stats.items():
            if changes:
                avg_change = np.mean(changes)
                races_count = len(changes)
                total_change = sum(changes)
                
                # 获取车手的主要车队（参赛场次最多的车队）
                if driver in self.driver_teams:
                    main_team = max(self.driver_teams[driver].items(), key=lambda x: x[1])[0]
                else:
                    main_team = 'Unknown'
                
                driver_averages[driver] = {
                    'avg_change': avg_change,
                    'total_change': total_change,
                    'races_count': races_count,
                    'team': main_team,
                    'color': self.team_colors.get(main_team, '#FFFFFF')
                }
        
        return driver_averages
    
    def create_season_analysis_charts(self):
        """创建赛季分析图表"""
        driver_averages = self.calculate_driver_averages()
        
        # 创建图表
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.3, wspace=0.2)
        
        # 主标题
        fig.suptitle(f'🏁 {self.year}年F1赛季车手位置变化分析', 
                     fontsize=24, fontweight='bold', y=0.98)
        
        # 图1: 车手年度平均位置变化对比
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_driver_average_changes(ax1, driver_averages)
        
        # 图2: 车手总位置变化
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_total_position_changes(ax2, driver_averages)
        
        # 图3: 车队平均表现
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_team_performance(ax3, driver_averages)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        filename = f'f1_{self.year}_season_analysis_merged.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"✅ 图表已保存为: {filename}")
        plt.show()
    
    def _plot_driver_average_changes(self, ax, driver_averages):
        """绘制车手年度平均位置变化对比图"""
        # 按平均变化排序
        sorted_drivers = sorted(driver_averages.items(), 
                               key=lambda x: x[1]['avg_change'], reverse=True)
        
        drivers = [item[0].split()[-1] for item in sorted_drivers]  # 只显示姓氏
        avg_changes = [item[1]['avg_change'] for item in sorted_drivers]
        colors = [item[1]['color'] for item in sorted_drivers]
        
        # 创建条形图
        bars = ax.bar(range(len(drivers)), avg_changes, 
                     color=colors, alpha=0.8, edgecolor='white', linewidth=1)
        
        # 设置标签
        ax.set_xticks(range(len(drivers)))
        ax.set_xticklabels(drivers, rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('平均位置变化', fontsize=14, fontweight='bold')
        ax.set_title('车手年度平均位置变化对比 (正值=平均获得位置, 负值=平均失去位置)', 
                    fontsize=16, fontweight='bold')
        
        # 添加数值标签
        for bar, value in zip(bars, avg_changes):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., 
                   height + (0.1 if height >= 0 else -0.1),
                   f'{value:.1f}', ha='center', 
                   va='bottom' if height >= 0 else 'top',
                   fontweight='bold', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='white', linestyle='-', alpha=0.8)
        
        # 设置y轴范围
        max_abs = max(abs(min(avg_changes)), abs(max(avg_changes)))
        ax.set_ylim(-max_abs*1.2, max_abs*1.2)
    
    def _plot_total_position_changes(self, ax, driver_averages):
        """绘制车手总位置变化"""
        sorted_drivers = sorted(driver_averages.items(), 
                               key=lambda x: x[1]['total_change'], reverse=True)
        
        drivers = [item[0].split()[-1] for item in sorted_drivers[:15]]  # 显示前15名
        total_changes = [item[1]['total_change'] for item in sorted_drivers[:15]]
        colors = [item[1]['color'] for item in sorted_drivers[:15]]
        
        bars = ax.barh(range(len(drivers)), total_changes, 
                      color=colors, alpha=0.7, edgecolor='white', linewidth=1)
        
        ax.set_yticks(range(len(drivers)))
        ax.set_yticklabels(drivers, fontsize=10)
        ax.set_xlabel('总位置变化', fontsize=12, fontweight='bold')
        ax.set_title('车手赛季总位置变化 (前15名)', fontsize=14, fontweight='bold')
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, total_changes)):
            ax.text(value + (1 if value > 0 else -1), i, 
                   f'{int(value):+d}', ha='left' if value > 0 else 'right', 
                   va='center', fontweight='bold', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=0, color='white', linestyle='-', alpha=0.8)
    
    def _plot_team_performance(self, ax, driver_averages):
        """绘制车队平均表现（基于车手的主要车队）"""
        team_stats = defaultdict(list)
        
        for driver, stats in driver_averages.items():
            team_stats[stats['team']].append(stats['avg_change'])
        
        team_averages = {team: np.mean(changes) 
                        for team, changes in team_stats.items()}
        
        sorted_teams = sorted(team_averages.items(), 
                             key=lambda x: x[1], reverse=True)
        
        teams = [item[0] for item in sorted_teams]
        avg_changes = [item[1] for item in sorted_teams]
        colors = [self.team_colors.get(team, '#FFFFFF') for team in teams]
        
        bars = ax.barh(range(len(teams)), avg_changes, 
                      color=colors, alpha=0.7, edgecolor='white', linewidth=1)
        
        ax.set_yticks(range(len(teams)))
        ax.set_yticklabels([team.replace(' ', '\n') for team in teams], fontsize=9)
        ax.set_xlabel('车队平均位置变化', fontsize=12, fontweight='bold')
        ax.set_title('车队平均位置变化表现', fontsize=14, fontweight='bold')
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, avg_changes)):
            ax.text(value + (0.05 if value > 0 else -0.05), i, 
                   f'{value:.1f}', ha='left' if value > 0 else 'right', 
                   va='center', fontweight='bold', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=0, color='white', linestyle='-', alpha=0.8)
    
    def print_season_summary(self):
        """打印赛季总结（合并同名车手数据）"""
        driver_averages = self.calculate_driver_averages()
        
        print("\n" + "="*80)
        print(f"🏁 {self.year}年F1赛季车手位置变化分析总结（合并同名车手）")
        print("="*80)
        
        # 最佳和最差表现者
        best_performer = max(driver_averages.items(), key=lambda x: x[1]['avg_change'])
        worst_performer = min(driver_averages.items(), key=lambda x: x[1]['avg_change'])
        
        print(f"\n🏆 年度最佳位置提升者: {best_performer[0]}")
        print(f"   平均每场提升: {best_performer[1]['avg_change']:.2f}位")
        print(f"   参赛场次: {best_performer[1]['races_count']}场")
        print(f"   主要车队: {best_performer[1]['team']}")
        
        print(f"\n📉 年度位置变化最差: {worst_performer[0]}")
        print(f"   平均每场变化: {worst_performer[1]['avg_change']:.2f}位")
        print(f"   参赛场次: {worst_performer[1]['races_count']}场")
        print(f"   主要车队: {worst_performer[1]['team']}")
        
        # 检查换队车手
        print("\n🔄 换队车手统计:")
        multi_team_drivers = []
        for driver, teams in self.driver_teams.items():
            if len(teams) > 1:
                team_list = [f"{team}({count}场)" for team, count in teams.items()]
                multi_team_drivers.append(f"{driver}: {', '.join(team_list)}")
        
        if multi_team_drivers:
            for driver_info in multi_team_drivers:
                print(f"  • {driver_info}")
        else:
            print("  • 本赛季无车手换队")
        
        # 车队统计
        print("\n🏁 车队平均位置变化排行:")
        team_stats = defaultdict(list)
        for driver, stats in driver_averages.items():
            team_stats[stats['team']].append(stats['avg_change'])
        
        team_averages = {team: np.mean(changes) 
                        for team, changes in team_stats.items()}
        
        for i, (team, avg) in enumerate(sorted(team_averages.items(), 
                                              key=lambda x: x[1], reverse=True), 1):
            print(f"  {i}. {team}: {avg:.2f}位")
        
        # 整体统计
        all_changes = [race['position_change'] for race in self.season_data]
        print(f"\n📊 整体统计:")
        print(f"• 总比赛记录: {len(self.season_data)}条")
        print(f"• 参赛车手数: {len(self.driver_stats)}位")
        print(f"• 平均位置变化: {np.mean(all_changes):.2f}位")
        print(f"• 位置变化标准差: {np.std(all_changes):.2f}")
        print(f"• 最大单场提升: {max(all_changes)}位")
        print(f"• 最大单场下降: {min(all_changes)}位")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='F1赛季车手位置变化分析（合并同名车手）')
    parser.add_argument('--year', type=int, default=2024, 
                       help='分析年份 (默认: 2024)')
    
    args = parser.parse_args()
    
    print(f"🏎️ 开始分析{args.year}年F1赛季数据（合并同名车手版本）...")
    
    analyzer = F1SeasonAnalysisOptimized(args.year)
    
    # 加载最小化数据
    analyzer.load_season_data_minimal()
    
    # 打印赛季总结
    analyzer.print_season_summary()
    
    # 生成图表
    print("\n📊 正在生成赛季分析图表...")
    analyzer.create_season_analysis_charts()
    
    print("\n✅ 分析完成!")

if __name__ == "__main__":
    main()