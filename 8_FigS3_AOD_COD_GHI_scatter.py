import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib
import h5py

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

## 读数据
f = h5py.File('geo_china_loc.hdf5', 'r')  
longitude =  f['longitude'][:]
latitude =  f['latitude'][:]
loc = f['china_loc'][:]
china_mask = np.isin(loc, sum(egrid.values(), []))
regions_names = ['Eastern', 'Central', 'Southern', 'Northeastern', 'Northern', 'Northwestern', 'Xizang']

## 画图
width_inches = 18 /2.54 # 调整宽度
height_inches = 6 / 2.54    
fig, axs = plt.subplots(
    nrows=1,      # 1 行
    ncols=len(path_names),     # 3 列
    figsize=(width_inches, height_inches))
plt.subplots_adjust(wspace=0.3, hspace=0.01, left=0.08, right=0.88, bottom=0.15, top=0.85)

f1 = h5py.File('GHI_PV_2060_v2.hdf5', 'r')
print("Keys in f1:", list(f1.keys()))

for j, path_name in enumerate(path_names):
    print(f"Processing {path_name}")
    AOD_diffs = []
    ghi_diffs = []
    COD_diffs = []
    for region_name, grid_id in egrid.items():
        mask = np.isin(loc, grid_id)
        AOD_diff = np.nanmean((f1[f'AOD_{path_name}_avg'][:] - f1['AOD_bs_avg'][:])[mask])
        ghi_diff = np.nanmean((f1[f'ghi_{path_name}_avg'][:] - f1['ghi_bs_avg'][:])[mask])
        COD_diff = np.nanmean((f1[f'COD_{path_name}_avg'][:] - f1['COD_bs_avg'][:])[mask])
        AOD_diffs.append(AOD_diff)
        ghi_diffs.append(ghi_diff)
        COD_diffs.append(COD_diff)

    ax = axs[j]
    sc = ax.scatter(AOD_diffs, ghi_diffs, c=COD_diffs, cmap='viridis', alpha=0.8)    
    for k, region_name in enumerate(regions_names):
        ax.text(AOD_diffs[k], ghi_diffs[k], region_name, fontsize=8, ha='right', va='bottom')    
        ax.set_xlabel('ΔAOD')
    ax.set_ylabel('ΔGHI [Wm$^{-2}$]')
    ax.set_title(title[j])

# 颜色条
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
cbar = plt.colorbar(sc, cax=cbar_ax)
cbar.set_label('ΔCOD')

plt.savefig('./figures/scatter_AOD_GHI_COD.png', bbox_inches='tight', dpi=600)
plt.close()