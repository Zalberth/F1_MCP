#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1赛车性能对比分析工具
通过Fast F1数据对比不同车队赛车的性能差异
示例：2025年红牛环赛道 - 红牛 vs 迈凯轮性能对比
"""

import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('dark_background')

# 启用FastF1缓存
fastf1.Cache.enable_cache('./f1_cache')

class F1PerformanceComparison:
    """
    F1赛车性能对比分析类
    """
    
    def __init__(self, year, gp, session='R'):
        self.year = year
        self.gp = gp
        self.session_type = session
        self.session = None
        self.team_colors = {
            'Red Bull Racing': '#1E41FF',
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
        
    def load_session_data(self):
        """加载会话数据"""
        try:
            self.session = fastf1.get_session(self.year, self.gp, self.session_type)
            self.session.load()
            print(f"✅ 成功加载 {self.year} {self.gp} {self.session_type} 数据")
            return True
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return False
    
    def get_team_data(self, team1, team2):
        """获取两个车队的数据"""
        if not self.session:
            return None, None
            
        team1_data = self.session.laps[self.session.laps['Team'] == team1]
        team2_data = self.session.laps[self.session.laps['Team'] == team2]
        
        return team1_data, team2_data
    
    def compare_lap_times(self, team1, team2, save_path='lap_times_comparison.png'):
        """对比圈速性能"""
        team1_data, team2_data = self.get_team_data(team1, team2)
        
        if team1_data is None or team2_data is None:
            print("❌ 无法获取车队数据")
            return
        
        # 过滤有效圈速
        team1_valid = team1_data[team1_data['LapTime'].notna()]
        team2_valid = team2_data[team2_data['LapTime'].notna()]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('#0E1117')
        
        # 1. 圈速分布对比
        team1_times = team1_valid['LapTime'].dt.total_seconds()
        team2_times = team2_valid['LapTime'].dt.total_seconds()
        
        ax1.hist(team1_times, bins=20, alpha=0.7, color=self.team_colors.get(team1, '#FF0000'), 
                label=team1, density=True)
        ax1.hist(team2_times, bins=20, alpha=0.7, color=self.team_colors.get(team2, '#00FF00'), 
                label=team2, density=True)
        ax1.set_xlabel('圈速 (秒)')
        ax1.set_ylabel('密度')
        ax1.set_title('圈速分布对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 圈速进化趋势
        for driver in team1_valid['Driver'].unique():
            driver_data = team1_valid[team1_valid['Driver'] == driver]
            ax2.plot(driver_data['LapNumber'], driver_data['LapTime'].dt.total_seconds(), 
                    color=self.team_colors.get(team1, '#FF0000'), alpha=0.7, linewidth=2)
        
        for driver in team2_valid['Driver'].unique():
            driver_data = team2_valid[team2_valid['Driver'] == driver]
            ax2.plot(driver_data['LapNumber'], driver_data['LapTime'].dt.total_seconds(), 
                    color=self.team_colors.get(team2, '#00FF00'), alpha=0.7, linewidth=2)
        
        ax2.set_xlabel('圈数')
        ax2.set_ylabel('圈速 (秒)')
        ax2.set_title('圈速进化趋势')
        ax2.grid(True, alpha=0.3)
        
        # 添加图例
        ax2.plot([], [], color=self.team_colors.get(team1, '#FF0000'), label=team1, linewidth=3)
        ax2.plot([], [], color=self.team_colors.get(team2, '#00FF00'), label=team2, linewidth=3)
        ax2.legend()
        
        # 3. 最快圈速对比
        team1_fastest = team1_times.min()
        team2_fastest = team2_times.min()
        team1_avg = team1_times.mean()
        team2_avg = team2_times.mean()
        
        categories = ['最快圈速', '平均圈速']
        team1_values = [team1_fastest, team1_avg]
        team2_values = [team2_fastest, team2_avg]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax3.bar(x - width/2, team1_values, width, label=team1, 
                       color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = ax3.bar(x + width/2, team2_values, width, label=team2, 
                       color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        ax3.set_xlabel('性能指标')
        ax3.set_ylabel('时间 (秒)')
        ax3.set_title('关键性能指标对比')
        ax3.set_xticks(x)
        ax3.set_xticklabels(categories)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        for bar in bars2:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        # 4. 圈速一致性对比（标准差）
        team1_std = team1_times.std()
        team2_std = team2_times.std()
        
        consistency_data = [team1_std, team2_std]
        colors = [self.team_colors.get(team1, '#FF0000'), self.team_colors.get(team2, '#00FF00')]
        
        bars = ax4.bar([team1, team2], consistency_data, color=colors, alpha=0.8)
        ax4.set_ylabel('圈速标准差 (秒)')
        ax4.set_title('圈速一致性对比\n(标准差越小越稳定)')
        ax4.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, value in zip(bars, consistency_data):
            ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.001,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.suptitle(f'{self.year} {self.gp} - {team1} vs {team2} 圈速性能对比', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#0E1117')
        plt.show()
        
        # 打印统计信息
        print(f"\n📊 {team1} vs {team2} 圈速统计:")
        print(f"{team1}: 最快 {team1_fastest:.3f}s, 平均 {team1_avg:.3f}s, 标准差 {team1_std:.3f}s")
        print(f"{team2}: 最快 {team2_fastest:.3f}s, 平均 {team2_avg:.3f}s, 标准差 {team2_std:.3f}s")
        print(f"最快圈速差距: {abs(team1_fastest - team2_fastest):.3f}s")
    
    def compare_sector_performance(self, team1, team2, save_path='sector_comparison.png'):
        """对比扇区性能"""
        team1_data, team2_data = self.get_team_data(team1, team2)
        
        if team1_data is None or team2_data is None:
            return
        
        # 获取扇区时间数据
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        sector_names = ['第一扇区', '第二扇区', '第三扇区']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('#0E1117')
        
        # 扇区时间对比
        team1_sectors = []
        team2_sectors = []
        
        for sector in sectors:
            team1_sector = team1_data[sector].dropna().dt.total_seconds()
            team2_sector = team2_data[sector].dropna().dt.total_seconds()
            team1_sectors.append(team1_sector.mean())
            team2_sectors.append(team2_sector.mean())
        
        x = np.arange(len(sector_names))
        width = 0.35
        
        bars1 = axes[0,0].bar(x - width/2, team1_sectors, width, label=team1, 
                             color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = axes[0,0].bar(x + width/2, team2_sectors, width, label=team2, 
                             color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        axes[0,0].set_xlabel('扇区')
        axes[0,0].set_ylabel('平均时间 (秒)')
        axes[0,0].set_title('扇区时间对比')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(sector_names)
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                axes[0,0].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                              f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        # 扇区性能雷达图
        angles = np.linspace(0, 2 * np.pi, len(sector_names), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        # 标准化数据（越小越好，所以用倒数）
        team1_normalized = [(1/t) for t in team1_sectors]
        team2_normalized = [(1/t) for t in team2_sectors]
        team1_normalized += team1_normalized[:1]
        team2_normalized += team2_normalized[:1]
        
        ax_radar = plt.subplot(2, 2, 2, projection='polar')
        ax_radar.plot(angles, team1_normalized, 'o-', linewidth=2, 
                     label=team1, color=self.team_colors.get(team1, '#FF0000'))
        ax_radar.fill(angles, team1_normalized, alpha=0.25, 
                     color=self.team_colors.get(team1, '#FF0000'))
        ax_radar.plot(angles, team2_normalized, 'o-', linewidth=2, 
                     label=team2, color=self.team_colors.get(team2, '#00FF00'))
        ax_radar.fill(angles, team2_normalized, alpha=0.25, 
                     color=self.team_colors.get(team2, '#00FF00'))
        
        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(sector_names)
        ax_radar.set_title('扇区性能雷达图\n(外圈表示更好的性能)', pad=20)
        ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # 扇区时间差异
        sector_diff = [t2 - t1 for t1, t2 in zip(team1_sectors, team2_sectors)]
        colors = ['green' if diff < 0 else 'red' for diff in sector_diff]
        
        bars = axes[1,0].bar(sector_names, sector_diff, color=colors, alpha=0.7)
        axes[1,0].set_ylabel(f'时间差异 (秒)\n负值表示{team1}更快')
        axes[1,0].set_title('扇区时间差异')
        axes[1,0].axhline(y=0, color='white', linestyle='--', alpha=0.5)
        axes[1,0].grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar, diff in zip(bars, sector_diff):
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., 
                          height + (0.01 if height > 0 else -0.01),
                          f'{diff:+.3f}', ha='center', 
                          va='bottom' if height > 0 else 'top', fontsize=10)
        
        # 扇区一致性对比
        team1_sector_std = []
        team2_sector_std = []
        
        for sector in sectors:
            team1_sector = team1_data[sector].dropna().dt.total_seconds()
            team2_sector = team2_data[sector].dropna().dt.total_seconds()
            team1_sector_std.append(team1_sector.std())
            team2_sector_std.append(team2_sector.std())
        
        x = np.arange(len(sector_names))
        bars1 = axes[1,1].bar(x - width/2, team1_sector_std, width, label=team1, 
                             color=self.team_colors.get(team1, '#FF0000'), alpha=0.8)
        bars2 = axes[1,1].bar(x + width/2, team2_sector_std, width, label=team2, 
                             color=self.team_colors.get(team2, '#00FF00'), alpha=0.8)
        
        axes[1,1].set_xlabel('扇区')
        axes[1,1].set_ylabel('标准差 (秒)')
        axes[1,1].set_title('扇区一致性对比')
        axes[1,1].set_xticks(x)
        axes[1,1].set_xticklabels(sector_names)
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.suptitle(f'{self.year} {self.gp} - {team1} vs {team2} 扇区性能对比', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='#0E1117')
        plt.show()
    
    def compare_telemetry_performance(self, team1, team2, driver1, driver2, lap_number=None):
        """对比遥测性能数据"""
        if not self.session:
            return
        
        # 获取车手数据
        try:
            driver1_laps = self.session.laps.pick_driver(driver1)
            driver2_laps = self.session.laps.pick_driver(driver2)
            
            if lap_number:
                lap1 = driver1_laps[driver1_laps['LapNumber'] == lap_number].iloc[0]
                lap2 = driver2_laps[driver2_laps['LapNumber'] == lap_number].iloc[0]
            else:
                # 选择最快圈
                lap1 = driver1_laps.pick_fastest()
                lap2 = driver2_laps.pick_fastest()
            
            # 获取遥测数据
            tel1 = lap1.get_telemetry()
            tel2 = lap2.get_telemetry()
            
            # 创建对比图
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.patch.set_facecolor('#0E1117')
            
            # 速度对比
            axes[0,0].plot(tel1['Distance'], tel1['Speed'], 
                          color=self.team_colors.get(team1, '#FF0000'), 
                          label=f'{driver1} ({team1})', linewidth=2)
            axes[0,0].plot(tel2['Distance'], tel2['Speed'], 
                          color=self.team_colors.get(team2, '#00FF00'), 
                          label=f'{driver2} ({team2})', linewidth=2)
            axes[0,0].set_xlabel('距离 (m)')
            axes[0,0].set_ylabel('速度 (km/h)')
            axes[0,0].set_title('速度对比')
            axes[0,0].legend()
            axes[0,0].grid(True, alpha=0.3)
            
            # 油门对比
            axes[0,1].plot(tel1['Distance'], tel1['Throttle'], 
                          color=self.team_colors.get(team1, '#FF0000'), 
                          label=f'{driver1} ({team1})', linewidth=2)
            axes[0,1].plot(tel2['Distance'], tel2['Throttle'], 
                          color=self.team_colors.get(team2, '#00FF00'), 
                          label=f'{driver2} ({team2})', linewidth=2)
            axes[0,1].set_xlabel('距离 (m)')
            axes[0,1].set_ylabel('油门开度 (%)')
            axes[0,1].set_title('油门使用对比')
            axes[0,1].legend()
            axes[0,1].grid(True, alpha=0.3)
            
            # 刹车对比
            axes[1,0].plot(tel1['Distance'], tel1['Brake'], 
                          color=self.team_colors.get(team1, '#FF0000'), 
                          label=f'{driver1} ({team1})', linewidth=2)
            axes[1,0].plot(tel2['Distance'], tel2['Brake'], 
                          color=self.team_colors.get(team2, '#00FF00'), 
                          label=f'{driver2} ({team2})', linewidth=2)
            axes[1,0].set_xlabel('距离 (m)')
            axes[1,0].set_ylabel('刹车 (布尔值)')
            axes[1,0].set_title('刹车使用对比')
            axes[1,0].legend()
            axes[1,0].grid(True, alpha=0.3)
            
            # RPM对比
            if 'RPM' in tel1.columns and 'RPM' in tel2.columns:
                axes[1,1].plot(tel1['Distance'], tel1['RPM'], 
                              color=self.team_colors.get(team1, '#FF0000'), 
                              label=f'{driver1} ({team1})', linewidth=2)
                axes[1,1].plot(tel2['Distance'], tel2['RPM'], 
                              color=self.team_colors.get(team2, '#00FF00'), 
                              label=f'{driver2} ({team2})', linewidth=2)
                axes[1,1].set_xlabel('距离 (m)')
                axes[1,1].set_ylabel('引擎转速 (RPM)')
                axes[1,1].set_title('引擎转速对比')
                axes[1,1].legend()
                axes[1,1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            lap_info = f"第{lap_number}圈" if lap_number else "最快圈"
            plt.suptitle(f'{self.year} {self.gp} - {driver1} vs {driver2} 遥测数据对比 ({lap_info})', 
                        fontsize=16, fontweight='bold', y=0.98)
            plt.savefig(f'telemetry_comparison_{driver1}_{driver2}.png', 
                       dpi=300, bbox_inches='tight', facecolor='#0E1117')
            plt.show()
            
            # 打印圈速信息
            print(f"\n🏁 圈速对比:")
            print(f"{driver1} ({team1}): {lap1['LapTime']}")
            print(f"{driver2} ({team2}): {lap2['LapTime']}")
            
        except Exception as e:
            print(f"❌ 遥测数据对比失败: {e}")
    
    def generate_comprehensive_report(self, team1, team2):
        """生成综合性能报告"""
        print(f"\n🏎️ 正在生成 {team1} vs {team2} 综合性能报告...")
        
        # 1. 圈速对比
        print("\n📊 1. 圈速性能对比")
        self.compare_lap_times(team1, team2)
        
        # 2. 扇区对比
        print("\n📊 2. 扇区性能对比")
        self.compare_sector_performance(team1, team2)
        
        # 3. 获取代表性车手进行遥测对比
        team1_data, team2_data = self.get_team_data(team1, team2)
        if team1_data is not None and team2_data is not None:
            driver1 = team1_data['Driver'].iloc[0]
            driver2 = team2_data['Driver'].iloc[0]
            print(f"\n📊 3. 遥测数据对比 ({driver1} vs {driver2})")
            self.compare_telemetry_performance(team1, team2, driver1, driver2)
        
        print(f"\n✅ {team1} vs {team2} 性能对比分析完成！")

def main():
    """主函数 - 示例：2025年红牛环 红牛 vs 迈凯轮"""
    print("🏁 F1赛车性能对比分析工具")
    print("=" * 50)
    
    # 注意：2025年数据可能还不可用，这里使用2024年作为示例
    # 实际使用时请根据数据可用性调整年份
    year = 2024  # 可以改为2025当数据可用时
    gp = 'Austria'  # 红牛环
    
    # 创建分析对象
    analyzer = F1PerformanceComparison(year, gp, 'R')
    
    # 加载数据
    if analyzer.load_session_data():
        # 对比红牛和迈凯轮
        team1 = 'Red Bull Racing'
        team2 = 'McLaren'
        
        # 生成综合报告
        analyzer.generate_comprehensive_report(team1, team2)
    else:
        print("❌ 无法加载数据，请检查年份和赛事设置")
        print("💡 提示：2025年数据可能还不可用，建议使用2024年数据")

if __name__ == "__main__":
    main()