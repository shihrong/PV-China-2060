import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as ticker
import code

matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 9,
        'axes.linewidth': 0.5}
matplotlib.rcParams.update(font)

scenarios = ['HB', 'CS', 'HR']
scenarios_name = ['HB-BS', 'CS-BS', 'HR-BS']

data = {}
df = pd.DataFrame(data)

# file_path = '2060_region_data_contribution_cal.csv'
file_path = '2060_region_contribute_shapely.csv'

df1 = pd.read_csv(file_path)

# df['Scenario'] = df1['region'].str.slice(-2)
df['Scenario'] = df1['region'].str.slice(-5)

df['Region'] = df1['region'].str.slice(0, 2)
# df['GHI_Contribution'] = df1['GHI_Contribution']
# df['T_Contribution'] = df1['T_Contribution']
# df['UV_Contribution'] = df1['UV_Contribution']
df['GHI_Contribution'] = df1['phi_G']
df['T_Contribution'] = df1['phi_T']
df['UV_Contribution'] = df1['phi_W']
# df_non_bs = df[df['Scenario'] != 'BS']
df_non_bs = df
# code.interact(local=locals())

regions_names = ['Eastern', 'Central', 'Southern', 'Northeastern', 'Northern', 'Northwestern', 'Xizang']
def plot_contributions_bar(ax, data, factor, factor_label):
    regions = data['Region'].unique()
    x = np.arange(len(regions))
    width = 0.22

    # 推荐色板（Set2，色盲友好，适合高水平期刊）
    colors = plt.get_cmap('Set2').colors[:3]

    for i, scenario in enumerate(scenarios_name):
        scenario_data = data[data['Scenario'] == scenario]
        values = scenario_data[factor].values
        ax.bar(x + i * width - width, values, width=width, label=scenarios_name[i], color=colors[i], edgecolor='k',linewidth=0.5)

    ax.set_xticks([])
    ax.set_xticklabels([])

    for i in range(1, len(regions_names)):
        ax.axvline(i - 0.5, color='gray', linestyle='-', linewidth=0.8, alpha=0.7, ymin=0, ymax=1)

    ax.set_ylabel(factor_label + ' Contribution')
    ax.grid(axis='y', linestyle='--', linewidth=0.5)
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3, 3))
    ax.yaxis.set_major_formatter(formatter)


width_inches = 18 / 2.54
height_inches = 15 / 2.54
fig, axes = plt.subplots(3, 1, figsize=(width_inches, height_inches), sharex=True)

plot_contributions_bar(axes[0], df_non_bs, 'GHI_Contribution', 'GHI')
plot_contributions_bar(axes[1], df_non_bs, 'T_Contribution', 'T2')
plot_contributions_bar(axes[2], df_non_bs, 'UV_Contribution', 'WS')

# # 去掉中间子图的上下边界线
# axes[1].spines['top'].set_visible(False)
# axes[1].spines['bottom'].set_visible(False)
# axes[2].spines['top'].set_visible(False)
# axes[0].spines['bottom'].set_visible(False)

handles, labels = axes[0].get_legend_handles_labels()
axes[0].legend(
    handles, labels,
    loc='upper right',
    ncol=1,
    bbox_to_anchor=(1.0, 0.95),
    frameon=False
)
# 在每个区域下方自定义显示区域名
y_min = axes[2].get_ylim()[0]
y_offset = 0.05 * (axes[2].get_ylim()[1] - axes[2].get_ylim()[0])
for i, name in enumerate(regions_names):
    axes[2].text(i, y_min - y_offset, name, ha='center', va='top', fontsize=9)


plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig('./figures/Fig2_GHI_T_U_contribution_region_bar_shapely.png', dpi=600, bbox_inches='tight')
plt.close()