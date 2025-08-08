#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1赛车发车名次 vs 最终完赛名次对比图 - 支持任意年份和赛道
使用FastF1库获取真实比赛数据
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
import seaborn as sns
import fastf1
import argparse
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置图表样式
plt.style.use('dark_background')
sns.set_palette("husl")

# 启用FastF1缓存
fastf1.Cache.enable_cache('fastf1_cache')

class F1GridVsFinishAnalysis:
    def __init__(self, year, gp_name):
        self.year = year
        self.gp_name = gp_name
        self.session = None
        self.df = None
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
            'RB': '#6C98FF'
        }
        
    def load_race_data(self):
        """从FastF1加载比赛数据"""
        try:
            print(f"🏎️ 正在加载{self.year}年{self.gp_name}大奖赛数据...")
            
            # 加载比赛会话
            self.session = fastf1.get_session(self.year, self.gp_name, 'R')
            self.session.load()
            
            # 获取比赛结果
            results = self.session.results
            
            # 处理数据
            race_data = []
            for idx, row in results.iterrows():
                # 获取车队颜色
                team_name = row['TeamName']
                color = self.team_colors.get(team_name, '#FFFFFF')
                
                # 处理完赛位置
                finish_pos = row['Position']
                if pd.isna(finish_pos):
                    finish_pos = len(results) + 1  # 退赛车手排在最后
                
                race_data.append({
                    'driver': f"{row['FirstName']} {row['LastName']}",
                    'team': team_name,
                    'grid': row['GridPosition'],
                    'finish': int(finish_pos),
                    'points': row['Points'] if not pd.isna(row['Points']) else 0,
                    'color': color,
                    'status': row['Status']
                })
            
            self.df = pd.DataFrame(race_data)
            print(f"✅ 数据加载完成，共{len(self.df)}位车手参赛")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            sys.exit(1)
    
    def create_grid_vs_finish_chart(self):
        """创建发车名次 vs 最终完赛名次对比图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        fig.suptitle(f'🏁 {self.year}年{self.gp_name}大奖赛 - 发车名次 vs 最终完赛名次对比分析', 
                     fontsize=24, fontweight='bold', y=0.98)
        
        # 图1: 散点图 - 发车位置 vs 完赛位置
        self._plot_grid_vs_finish_scatter(ax1)
        
        # 图2: 位置变化条形图
        self._plot_position_changes(ax2)
        
        plt.tight_layout(rect=[0, 0, 1, 0.94])
        filename = f'{self.gp_name.lower()}_{self.year}_grid_vs_finish.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"✅ 图表已保存为: {filename}")
        plt.show()
    
    def _plot_grid_vs_finish_scatter(self, ax):
        """绘制发车位置 vs 完赛位置散点图"""
        # 处理退赛车手
        max_finish = len(self.df)
        df_finished = self.df[self.df['finish'] <= max_finish - 1].copy()
        df_retired = self.df[self.df['finish'] == max_finish].copy()
        
        # 绘制完赛车手
        for _, row in df_finished.iterrows():
            ax.scatter(row['grid'], row['finish'], 
                      color=row['color'], s=200, alpha=0.8, edgecolors='white', linewidth=2)
            ax.annotate(row['driver'].split()[-1], 
                       (row['grid'], row['finish']), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=10, color='white', fontweight='bold')
        
        # 绘制退赛车手
        retired_y = max_finish + 1
        for _, row in df_retired.iterrows():
            ax.scatter(row['grid'], retired_y, 
                      color=row['color'], s=200, alpha=0.6, 
                      marker='x', linewidth=3)
            ax.annotate(f"{row['driver'].split()[-1]} (退赛)", 
                       (row['grid'], retired_y), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=10, color='red', fontweight='bold')
        
        # 绘制对角线（无位置变化线）
        ax.plot([1, max_finish], [1, max_finish], 'white', linestyle='--', alpha=0.5, linewidth=2)
        
        ax.set_xlabel('发车位置 (排位赛名次)', fontsize=14, fontweight='bold')
        ax.set_ylabel('最终完赛位置', fontsize=14, fontweight='bold')
        ax.set_title('发车位置 vs 最终完赛位置', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, max_finish + 1)
        ax.set_ylim(0, max_finish + 2)
        
        # 添加图例说明
        ax.text(0.02, 0.98, '对角线 = 无位置变化\n对角线上方 = 失去位置\n对角线下方 = 获得位置', 
                transform=ax.transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
    
    def _plot_position_changes(self, ax):
        """绘制位置变化条形图"""
        # 计算位置变化
        max_finish = len(self.df)
        self.df['position_change'] = self.df['grid'] - self.df['finish']
        # 退赛车手特殊处理
        retired_mask = self.df['finish'] == max_finish
        self.df.loc[retired_mask, 'position_change'] = -(max_finish - self.df.loc[retired_mask, 'grid'])
        
        # 按位置变化排序
        df_sorted = self.df.sort_values('position_change', ascending=True)
        
        # 设置颜色：正值为绿色（获得位置），负值为红色（失去位置）
        colors = ['green' if x > 0 else 'red' if x < 0 else 'gray' for x in df_sorted['position_change']]
        
        bars = ax.barh(range(len(df_sorted)), df_sorted['position_change'], 
                      color=colors, alpha=0.7, edgecolor='white', linewidth=1)
        
        # 添加车手姓名
        ax.set_yticks(range(len(df_sorted)))
        ax.set_yticklabels([name.split()[-1] for name in df_sorted['driver']], fontsize=10)
        
        # 在条形图上添加数值
        for i, (bar, value) in enumerate(zip(bars, df_sorted['position_change'])):
            if value != 0:
                ax.text(value + (0.3 if value > 0 else -0.3), i, 
                       f'{int(value):+d}', ha='left' if value > 0 else 'right', 
                       va='center', fontweight='bold', fontsize=9)
        
        ax.set_xlabel('位置变化 (正值=获得位置, 负值=失去位置)', fontsize=14, fontweight='bold')
        ax.set_title('各车手位置变化分析', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=0, color='white', linestyle='-', alpha=0.8)
    
    def _plot_team_performance(self, ax):
        """绘制车队表现分析"""
        # 按车队分组统计
        team_stats = self.df.groupby('team').agg({
            'points': 'sum',
            'position_change': 'mean',
            'driver': 'count'
        }).round(1)
        
        team_stats = team_stats.sort_values('points', ascending=True)
        
        # 创建双轴图
        ax2 = ax.twinx()
        
        # 绘制积分条形图
        bars1 = ax.barh(range(len(team_stats)), team_stats['points'], 
                       alpha=0.7, color='gold', label='车队积分')
        
        # 绘制平均位置变化散点图
        ax2.scatter(team_stats['position_change'], range(len(team_stats)), 
                   color='red', s=100, alpha=0.8, label='平均位置变化', marker='o')
        
        # 设置标签
        ax.set_yticks(range(len(team_stats)))
        ax.set_yticklabels(team_stats.index, fontsize=10)
        ax.set_xlabel('车队总积分', fontsize=12, fontweight='bold')
        ax2.set_xlabel('平均位置变化', fontsize=12, fontweight='bold')
        ax.set_title('车队表现分析', fontsize=16, fontweight='bold')
        
        # 添加数值标签
        for i, (bar, points) in enumerate(zip(bars1, team_stats['points'])):
            if points > 0:
                ax.text(points + 1, i, f'{points}分', 
                       va='center', fontweight='bold', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='x')
        ax2.axvline(x=0, color='white', linestyle='--', alpha=0.5)
    
    def _plot_points_analysis(self, ax):
        """绘制积分获得者分析"""
        points_scorers = self.df[self.df['points'] > 0].copy()
        
        # 创建积分条形图
        bars = ax.bar(range(len(points_scorers)), points_scorers['points'], 
                     color=[row['color'] for _, row in points_scorers.iterrows()],
                     alpha=0.8, edgecolor='white', linewidth=2)
        
        # 设置标签
        ax.set_xticks(range(len(points_scorers)))
        ax.set_xticklabels([name.split()[-1] for name in points_scorers['driver']], 
                          rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('获得积分', fontsize=12, fontweight='bold')
        ax.set_title('积分区完赛车手 (前10名)', fontsize=16, fontweight='bold')
        
        # 添加积分数值
        for bar, points in zip(bars, points_scorers['points']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(points)}', ha='center', va='bottom', 
                   fontweight='bold', fontsize=10)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, max(points_scorers['points']) * 1.1)
    
    def print_race_summary(self):
        """打印比赛总结"""
        print("\n" + "="*80)
        print(f"🏁 {self.year}年{self.gp_name}大奖赛 - 发车名次 vs 最终完赛名次分析")
        print("="*80)
        
        # 最大赢家和输家
        max_finish = len(self.df)
        self.df['position_change'] = self.df['grid'] - self.df['finish']
        retired_mask = self.df['finish'] == max_finish
        self.df.loc[retired_mask, 'position_change'] = -(max_finish - self.df.loc[retired_mask, 'grid'])
        
        biggest_gainer = self.df.loc[self.df['position_change'].idxmax()]
        biggest_loser = self.df.loc[self.df['position_change'].idxmin()]
        
        print(f"\n🏆 比赛冠军: {biggest_gainer['driver'] if biggest_gainer['finish'] == 1 else self.df[self.df['finish'] == 1]['driver'].iloc[0]}")
        print(f"📈 最大赢家: {biggest_gainer['driver']} (P{int(biggest_gainer['grid'])} → P{int(biggest_gainer['finish'])}, +{int(biggest_gainer['position_change'])}位)")
        print(f"📉 最大输家: {biggest_loser['driver']} (P{int(biggest_loser['grid'])} → P{int(biggest_loser['finish'])}, {int(biggest_loser['position_change'])}位)")
        
        # 杆位表现
        pole_sitter = self.df[self.df['grid'] == 1].iloc[0]
        print(f"\n🥇 杆位车手: {pole_sitter['driver']} → 最终P{int(pole_sitter['finish'])}")
        
        # 车队积分榜
        print("\n🏁 车队积分榜:")
        team_points = self.df.groupby('team')['points'].sum().sort_values(ascending=False)
        for i, (team, points) in enumerate(team_points.head(5).items(), 1):
            print(f"  {i}. {team}: {int(points)}分")
        
        # 退赛情况
        max_finish = len(self.df)
        retired_drivers = self.df[self.df['finish'] == max_finish]
        if not retired_drivers.empty:
            print(f"\n❌ 退赛车手: {', '.join(retired_drivers['driver'])}")
        
        print("\n💡 关键洞察:")
        print(f"• 共有{len(self.df[self.df['points'] > 0])}位车手获得积分")
        print(f"• 平均位置变化: {self.df['position_change'].mean():.1f}位")
        print(f"• 最激烈的位置争夺发生在中游集团")
        
        if not retired_drivers.empty:
            print(f"• {len(retired_drivers)}位车手未能完赛")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='F1赛车发车名次 vs 最终完赛名次对比分析')
    parser.add_argument('--year', type=int, default=2024, help='比赛年份 (默认: 2024)')
    parser.add_argument('--gp', type=str, default='Hungary', help='大奖赛名称 (默认: Hungary)')
    
    args = parser.parse_args()
    
    print(f"🏎️ 开始分析{args.year}年{args.gp}大奖赛数据...")
    
    analyzer = F1GridVsFinishAnalysis(args.year, args.gp)
    
    # 加载数据
    analyzer.load_race_data()
    
    # 打印比赛总结
    analyzer.print_race_summary()
    
    # 生成图表
    print("\n📊 正在生成对比分析图表...")
    analyzer.create_grid_vs_finish_chart()
    
    print("\n✅ 分析完成!")

if __name__ == "__main__":
    main()