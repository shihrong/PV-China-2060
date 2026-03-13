# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:17:38 2024

@author: huang
"""

# import geopandas as gpd
from shapely.geometry import Point
import h5py
import numpy as np
import code
import shapefile
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import matplotlib.patches as mpatches


df = pd.read_csv('./2060_scenarios_power_region.csv')

# 读取不确定性上下限的数据
# f_low = pd.read_excel('./2060_scenarios_power_region_uncertainty_l_66th.xlsx')
# df_up = pd.read_excel('./2060_scenarios_power_region_uncertainty_u_66th.xlsx')

# PVp std from 2060_scenarios_PVp_std_region.csv
std_PVp = {'hb-bs':0.4/1000,'cs-bs':0.5/1000,'hr-bs':0.7/1000} # units:PVp 除上1000就是PVp单位
capacity_s = {'hb':2917,'cs':3461,'hr':4583} # units:GW
# PVp std from 2060_scenarios_PVp_std_region.csv
df_std = pd.read_csv('./2060_scenarios_PVp_std_region.csv')
# 排除 df_std 中 region 为 'all' 的行
df_std = df_std[df_std['region'] != 'all']
# 进行乘法运算
std_hb_bs = df_std['std_hb-bs']/1000 * df['Ca_hb'] # PVp/1000
std_cs_bs = df_std['std_cs-bs']/1000 * df['Ca_cs'] # PVp/1000
std_hr_bs = df_std['std_hr-bs']/1000 * df['Ca_hr'] # PVp/1000
# 分别求和
sum_std_hb_bs = std_hb_bs.sum()
sum_std_cs_bs = std_cs_bs.sum()
sum_std_hr_bs = std_hr_bs.sum()


print(f"std_hb-bs 的求和结果: {sum_std_hb_bs}")
print(f"std_cs-bs 的求和结果: {sum_std_cs_bs}")
print(f"std_hr-bs 的求和结果: {sum_std_hr_bs}")

## plot bar
matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 9,
        'axes.linewidth': 0.5,
        'hatch.linewidth': 0.3}
matplotlib.rcParams.update(font)

# 设置图形大小
## 画图
width_inches = 20 / 2.54  # 转换成英寸
height_inches = 8 / 2.54
fig, axs = plt.subplots(1,2,figsize=(width_inches, height_inches))

regions = df['region']
# factors = ['d_Power','Ca_ind','Ae_ind','both']
factors = ['Ae_ind','both']
# legends = ['Capacity induced','Aerosol induced']
# legends = ['PV potential changes','Capacity changes']  # 24/08/12
legends = ['PV potential changes','Additional Capacity changes']  # 24/12/4

# titles = ['$\mathrm{\Delta Power\ outputs}$','Aerosol_induced']
titles = ['Aerosol-induced power generation increase','Aerosol-induced power generation increase']# 24/08/12

catogories = ['HB-BS','CS-BS','HR-BS']

##### axs[0] ############
#画power和ecnomics 用Δpvp全国平均值 0.19 0.23 0.36%, 假设不确定性能传递，region都是0.15%
#画区域用区域数据region

# 年均运行时间：1500h
# t_year = 1500 # h
t_year = 365*24 # h, 24小时全天运行，全年无休
price = 0.09 # 每度电$kwh

# 推荐色板（Set2，色盲友好，适合高水平期刊）
colors = plt.get_cmap('Set2').colors[:3]
hatches = ['.....', '////']  # 斜线和点，密一些

bottom = np.zeros(len(catogories))  
for i, factor in enumerate(factors):
    values = [df[f'{factor}_hb'].sum()*t_year, df[f'{factor}_cs'].sum()*t_year, df[f'{factor}_hr'].sum()*t_year]
    for j, v in enumerate(values):
        axs[0].bar(
            catogories[j], v, bottom=bottom[j],
            label=legends[i] if j==0 else "",
            color=colors[j],
            hatch=hatches[i],
            # alpha=0.7,
            edgecolor='k',
            linewidth=0.5
        )
        bottom[j] += v
print(bottom)



power_error = [sum_std_hb_bs * t_year,
               sum_std_cs_bs * t_year,
               sum_std_hr_bs * t_year]

print(power_error)

axs[0].errorbar(
    catogories,
    bottom,  # 当前堆叠后的总值
    yerr=power_error,  # 误差范围
    fmt='none',  # 不绘制点，只绘制误差条
    ecolor='#333366',  # 误差条颜色
    capsize=4  # 误差条帽子的长度
)
print(bottom)
print(power_error)
# Plotting the line chart for total value
factor = 'Ae_both'
p_values = [df[f'{factor}_hb'].sum()*t_year*price*1e6 /1e9, 
            df[f'{factor}_cs'].sum()*t_year*price*1e6 /1e9,
            df[f'{factor}_hr'].sum()*t_year*price*1e6 /1e9 ]  # GWh *e6 /e9 = billion/year

p_error = [    sum_std_hb_bs * t_year* price*1e6 /1e9,
               sum_std_cs_bs * t_year* price*1e6 /1e9,
               sum_std_hr_bs * t_year* price*1e6 /1e9]


for i in [0,1,2]:
    # axs[0].text(i, bottom[i]+error_up[i], f'$ {p_values[i]:.2f}[{p_error_down[i]:.1f},{p_error_up[i]:.1f}]', ha='center', va='bottom', color='red')
    # axs[0].text(i, bottom[i]+error_up[i], f'$ {p_values[i]:.2f}', ha='center', va='bottom', color='red')
    axs[0].text(i, bottom[i]+power_error[i], f'$ {p_values[i]:.2f} ± {p_error[i]:.2f}', ha='center', va='bottom', color='#333366')

print(p_values)
print(p_error)


# 添加右侧的额外坐标轴并设置标签
ax2 = axs[0].twinx()
ax2.set_ylabel('Extra Gain [US billion yr$^{-1}$]', color='#333366')
ax2.set_yticks([])  # 如果不需要实际的坐标值，可以移除刻度

# ax2.plot(labels, totals, color='red', marker='o', linestyle=':', linewidth=2,markersize = 12)
# 将legend显示在子图上方，水平放置
handles, labels = axs[0].get_legend_handles_labels()
legend_handles = [
    mpatches.Patch(facecolor='white', edgecolor='k', hatch=hatches[i], label=legends[i],linewidth=0.5)
    for i in range(len(legends))
]
axs[0].legend(handles=legend_handles, labels=labels, loc='upper left', bbox_to_anchor=(0.01, 0.99), ncol=1,edgecolor='none',facecolor='none')
# axs[0].set_xlabel(titles[0])
axs[0].set_ylabel('Power generation increase [TWh]')
axs[0].set_ylim(0, 72000)
# axs[0].set_yscale('log')

########### axs[1,2] #################################################################
# 创建底部偏移量
bottom = np.zeros(len(catogories))  
factor = 'Ae_both'
totals = [df[f'{factor}_hb'].sum(), df[f'{factor}_cs'].sum() ,df[f'{factor}_hr'].sum() ]

region_names = ['Eastern', 'Central', 'Southern', 'Northeastern','Northern','Northwestern', 'Xizang']
# # 推荐的7色（ColorBrewer Set2，色盲友好，Nature/Science常用）
# region_colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#b3b3b3']  # 为每个区域分配一个颜色
for k, region in enumerate(region_names):
    values = [ df[f'{factor}_hb'].iloc[k],df[f'{factor}_cs'].iloc[k],df[f'{factor}_hr'].iloc[k] ]
    percentages = [v / t * 100 for v, t in zip(values, totals)]
    axs[1].bar(catogories, percentages, bottom=bottom, label=region)
    bottom += np.array(percentages)
# Plotting the line chart for total value
# ax2 = axs[1].twinx()
# ax2.plot(catogories, totals, color='red', marker='o', linestyle=':', linewidth=2,markersize = 8)
axs[1].set_ylim(0, 100)
# axs[1].set_xlabel(titles[1])
axs[1].set_ylabel('Percentage [%]')
# ax2.set_ylabel('Power [GW]')
# ax2.yaxis.label.set_color('red')
# ax2.tick_params(axis='y', colors='red')
# ax2.set_ylim(0, 7)

# 将第三张子图的legend显示在子图上方，水平放置
handles, labels = axs[1].get_legend_handles_labels()
axs[1].legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=4,edgecolor='none',facecolor='none',
               handletextpad=0.5,  # 减少句柄和文本之间的间距
               handlelength=0.6,  # 缩短线/标记的长度
             columnspacing=0.4)  # 减少列间距)

#调整子图布局
# 调整子图之间的水平间距
plt.subplots_adjust(wspace=0.4)  # 增大wspace的值增加子图之间的距离
plt.savefig(f'./figures/Fig4_bar_power_uncertainty_PVp_std.png', dpi=600,bbox_inches='tight')
plt.close()