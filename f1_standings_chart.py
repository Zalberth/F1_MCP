#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1 2025赛季车手积分排名图表生成器
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib import font_manager
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 2025年F1车手积分数据
driver_data = [
    {"name": "奥斯卡·皮亚斯特里", "team": "McLaren", "points": 284, "wins": 6, "color": "#FF8000"},
    {"name": "兰多·诺里斯", "team": "McLaren", "points": 275, "wins": 5, "color": "#FF8000"},
    {"name": "马克斯·维斯塔潘", "team": "Red Bull", "points": 187, "wins": 2, "color": "#1E41FF"},
    {"name": "乔治·拉塞尔", "team": "Mercedes", "points": 172, "wins": 1, "color": "#00D2BE"},
    {"name": "夏尔·勒克莱尔", "team": "Ferrari", "points": 151, "wins": 0, "color": "#DC143C"},
    {"name": "刘易斯·汉密尔顿", "team": "Ferrari", "points": 109, "wins": 0, "color": "#DC143C"},
    {"name": "安德烈亚·基米·安东内利", "team": "Mercedes", "points": 64, "wins": 0, "color": "#00D2BE"},
    {"name": "亚历山大·阿尔本", "team": "Williams", "points": 54, "wins": 0, "color": "#005AFF"},
    {"name": "尼科·胡肯伯格", "team": "Sauber", "points": 37, "wins": 0, "color": "#00FF00"},
    {"name": "埃斯特班·奥康", "team": "Haas", "points": 27, "wins": 0, "color": "#FFFFFF"}
]

def create_f1_standings_chart():
    """创建F1车手积分排名图表"""
    
    # 设置图表样式
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    # 提取数据
    names = [driver["name"] for driver in driver_data]
    points = [driver["points"] for driver in driver_data]
    teams = [driver["team"] for driver in driver_data]
    wins = [driver["wins"] for driver in driver_data]
    colors = [driver["color"] for driver in driver_data]
    
    # 创建水平条形图
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, points, color=colors, alpha=0.8, height=0.7)
    
    # 添加边框
    for bar in bars:
        bar.set_edgecolor('white')
        bar.set_linewidth(1.5)
    
    # 设置y轴标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{i+1}. {name}" for i, name in enumerate(names)], 
                       fontsize=11, color='white', fontweight='bold')
    
    # 反转y轴，使第一名在顶部
    ax.invert_yaxis()
    
    # 设置x轴
    ax.set_xlabel('积分 (Points)', fontsize=14, color='white', fontweight='bold')
    ax.set_xlim(0, max(points) * 1.15)
    
    # 设置网格
    ax.grid(True, alpha=0.3, color='gray', linestyle='--')
    ax.set_axisbelow(True)
    
    # 添加积分和胜场数标签
    for i, (point, win, team) in enumerate(zip(points, wins, teams)):
        # 积分标签
        ax.text(point + 5, i, f'{point}分', 
                va='center', ha='left', fontsize=10, 
                color='white', fontweight='bold')
        
        # 胜场数标签（如果有胜场）
        if win > 0:
            ax.text(point + 25, i, f'🏆{win}胜', 
                    va='center', ha='left', fontsize=9, 
                    color='gold')
        
        # 车队标签
        ax.text(5, i, team, 
                va='center', ha='left', fontsize=8, 
                color='lightgray', style='italic')
    
    # 设置标题
    ax.set_title('2025年F1世界锦标赛车手积分榜\nF1 2025 Drivers\' Championship Standings', 
                 fontsize=18, color='white', fontweight='bold', pad=20)
    
    # 添加副标题
    fig.text(0.5, 0.92, '前10名车手积分排名', 
             ha='center', fontsize=12, color='lightgray')
    
    # 添加图例说明
    legend_text = "🏆 = 分站赛胜利数量 | 颜色代表车队"
    fig.text(0.5, 0.02, legend_text, 
             ha='center', fontsize=10, color='lightgray')
    
    # 调整布局
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.08)
    
    # 保存图表
    plt.savefig('/Users/zhaomuhua/Desktop/LAB_AI/DATA_F1_MCP/f1_2025_standings.png', 
                dpi=300, bbox_inches='tight', facecolor='#0E1117')
    
    # 显示图表
    plt.show()
    
    print("✅ F1 2025车手积分排名图表已生成并保存为 'f1_2025_standings.png'")

def create_comparison_chart():
    """创建前三名车手对比图"""
    
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('#0E1117')
    
    # 前三名数据
    top3_names = ["皮亚斯特里", "诺里斯", "维斯塔潘"]
    top3_points = [284, 275, 187]
    top3_wins = [6, 5, 2]
    top3_colors = ["#FF8000", "#FF8000", "#1E41FF"]
    
    # 积分对比柱状图
    bars1 = ax1.bar(top3_names, top3_points, color=top3_colors, alpha=0.8)
    ax1.set_title('前三名积分对比', fontsize=16, color='white', fontweight='bold')
    ax1.set_ylabel('积分', fontsize=12, color='white')
    ax1.grid(True, alpha=0.3)
    
    # 添加积分标签
    for bar, point in zip(bars1, top3_points):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{point}', ha='center', va='bottom', 
                fontsize=12, color='white', fontweight='bold')
    
    # 胜场数对比柱状图
    bars2 = ax2.bar(top3_names, top3_wins, color=top3_colors, alpha=0.8)
    ax2.set_title('前三名胜场数对比', fontsize=16, color='white', fontweight='bold')
    ax2.set_ylabel('胜场数', fontsize=12, color='white')
    ax2.grid(True, alpha=0.3)
    
    # 添加胜场数标签
    for bar, win in zip(bars2, top3_wins):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{win}', ha='center', va='bottom', 
                fontsize=12, color='white', fontweight='bold')
    
    # 设置样式
    for ax in [ax1, ax2]:
        ax.set_facecolor('#0E1117')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
    
    plt.tight_layout()
    plt.savefig('/Users/zhaomuhua/Desktop/LAB_AI/DATA_F1_MCP/f1_2025_top3_comparison.png', 
                dpi=300, bbox_inches='tight', facecolor='#0E1117')
    plt.show()
    
    print("✅ F1 2025前三名对比图表已生成并保存为 'f1_2025_top3_comparison.png'")

if __name__ == "__main__":
    print("🏎️ 正在生成F1 2025赛季车手积分排名图表...")
    
    # 生成主要排名图表
    create_f1_standings_chart()
    
    # 生成前三名对比图表
    create_comparison_chart()
    
    print("\n🎉 所有图表生成完成！")
    print("📁 图表文件保存位置:")
    print("   - f1_2025_standings.png (完整排名图)")
    print("   - f1_2025_top3_comparison.png (前三名对比图)")