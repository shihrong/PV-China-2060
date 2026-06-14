import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib
import h5py
import pandas as pd
import seaborn as sns

matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 7}
matplotlib.rcParams.update(font)

path_names = ['hb','cs','hr']
title = ['(a) HB-BS','(b) CS-BS','(c) HR-BS']

egrid = {
'HD': [10131, 10132, 10133, 10134, 10135],
'HZ': [10141, 10142, 10143, 10136,10150, 10151],
'NF': [10144, 10145, 10146, 10152, 10153],
'DB': [10121, 10122, 10123],
'HB': [10111, 10112, 10113, 10114,10115, 10137],
'XB': [10161, 10162, 10163, 10164, 10165],
'XZ': [ 10154]
}
regions_names = ['Eastern', 'Central', 'Southern', 'Northeastern', 'Northern', 'Northwestern', 'Xizang']

## 读数据
f = h5py.File('geo_china_loc.hdf5', 'r')  
longitude =  f['longitude'][:]
latitude =  f['latitude'][:]
loc = f['china_loc'][:]
china_mask = np.isin(loc, sum(egrid.values(), []))

## 画图
width_inches = 14 /2.54 # 调整宽度
height_inches = 18 / 2.54    
fig, axs = plt.subplots(
    nrows=3,      # 3 行
    ncols=1,     # 3 列
    figsize=(width_inches, height_inches))
plt.subplots_adjust(wspace=0.3, hspace=0.01, left=0.08, right=0.88, bottom=0.15, top=0.85)

f1 = h5py.File('GHI_PV_v2.hdf5', 'r')
print("Keys in f1:", list(f1.keys()))

for j, path_name in enumerate(path_names):
    print(f"Processing {path_name}")
    data = []
    region_keys = list(egrid.keys())
    for i, region_name in enumerate(region_keys):
        mask = np.isin(loc, egrid[region_name])
        delta_ghi = (f1[f'ghi_{path_name}_avg'][:] - f1['ghi_bs_avg'][:])[mask]
        delta_ghi = delta_ghi[~np.isnan(delta_ghi)]  # remove nans
        print(f"Region {region_name}: {len(delta_ghi)} points")
        for val in delta_ghi:
            data.append({'region': regions_names[i], 'delta_ghi': val})

    df = pd.DataFrame(data)
    print(f"Total data points for {path_name}: {len(df)}")
    ax = axs[j]
    sns.violinplot(data=df, x='region', y='delta_ghi', ax=ax, palette='Set2', inner='box')
    ax.text(0.5, 0.95, title[j], transform=ax.transAxes, ha='center', va='top', fontsize=10)
    ax.set_ylabel('ΔGHI [Wm$^{-2}$]')
    ax.set_xlabel('Region')
    ax.tick_params(axis='x', rotation=45)

plt.savefig('./figures/violin_delta_GHI_regions.png', bbox_inches='tight', dpi=600)
plt.close()