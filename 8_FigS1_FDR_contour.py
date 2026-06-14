import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import numpy as np
import matplotlib.colors as mcolors
import h5py
import code
import matplotlib
import os
matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 9,
        'axes.linewidth': 0.5}
matplotlib.rcParams.update(font)


def plot_southsea(ax):
    # south sea
    #  南海
    # SHP = 'Z:/script_share_py/NCL-Chinamap-master/cnmap/'
    shpfilename = os.path.join('../../python script/中国基础数据map/', '中国行政区_包含南海九段线.shp') # 替换为你的shapefile路径

    pos1 = ax.get_position()
    pos2 = [pos1.x1 - ((pos1.x1 - pos1.x0) / 7), pos1.y0, pos1.width / 7,pos1.height / 5]
    proj_n = ccrs.LambertConformal(central_latitude=90, central_longitude=115)
    ax_n = fig.add_axes(pos2, projection=proj_n)
    ax_n.set_extent([105, 120, 0, 20], ccrs.PlateCarree())
    ax_n.add_geometries(Reader(shpfilename).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='k',linewidth=0.5)



var_names = ['PV','ghi']
path_names = ['hb', 'cs', 'hr']
title = ['HB-BS', 'CS-BS', 'HR-BS']
units = ['PV [%]', 'GHI [Wm$^{-2}$]']
cbarmax = [0.6, 6]
# py_cmap = ['OrRd', 'bwr']

# 读取数据
f = h5py.File('geo_china_loc.hdf5', 'r')  
longitude = f['longitude'][:]
latitude = f['latitude'][:]
loc = f['china_loc'][:]

f1 = h5py.File('GHI_PV_v2.hdf5', 'r')  
f2 = h5py.File('FDR_results.hdf5', 'r')

# 省界文件路径
shp = '../../python script/中国基础数据map/中国行政区.shp'
# code.interact(local=locals())
# 创建图形 - 一行三列
width_inches = 18 / 2.54  # 转换成英寸
height_inches = 10 / 2.54  # 稍微增加高度以适应colorbar
fig, axs = plt.subplots(2, 3, figsize=(width_inches, height_inches), 
                        subplot_kw={'projection': ccrs.LambertConformal(central_latitude=34, central_longitude=110)})
plt.subplots_adjust(wspace=0.02, hspace=0.01, left=0.12, right=0.88, bottom=0.08, top=0.92)
axs = axs.reshape(2, 3)  # 保证 2 维索引

for i, var_name in enumerate(var_names):

    # 中国区域掩码
    china_mask = loc > 0
    
    # 初始化用于colorbar的归一化范围
    all_diffs = []
    
    # 首先计算所有情景的数据范围，确保colorbar的一致性
    for j, path_name in enumerate(path_names):
        # 计算差值
        if var_name == 'PV':
            diff = f1[f'{var_name}_{path_name}_avg'][:] / 1000 * 100 - f1[f'{var_name}_bs_avg'][:] / 1000 * 100
        else:
            diff = f1[f'{var_name}_{path_name}_avg'][:] - f1[f'{var_name}_bs_avg'][:]
        
        # 应用中国区域掩码
        diff_plot = np.where(china_mask, diff, np.nan)
        all_diffs.append(diff_plot)
    
    # 计算所有数据的最大绝对值，用于colorbar
    all_diffs_array = np.concatenate([d[~np.isnan(d)].flatten() for d in all_diffs])
    vmax = np.nanmax(np.abs(all_diffs_array))
    vmax = cbarmax[i]
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    
    # 为每个情景创建子图
    for j, path_name in enumerate(path_names):
        ax = axs[i,j]
        
        # 计算差值
        if var_name == 'PV':
            diff = f1[f'{var_name}_{path_name}_avg'][:] / 1000 * 100 - f1[f'{var_name}_bs_avg'][:] / 1000 * 100
        else:
            diff = f1[f'{var_name}_{path_name}_avg'][:] - f1[f'{var_name}_bs_avg'][:]
        
        # 读取显著性数据
        sig_fdr = f2[f'{var_name}_{path_name}_sig_fdr'][:]
        
        # 应用中国区域掩码
        diff_plot = np.where(china_mask, diff, np.nan)
        sig_fdr_plot = np.where(china_mask, sig_fdr, False)
        
        # --- 绘制差值图 ---
        pcm = ax.pcolormesh(
            longitude, latitude, diff_plot,
            cmap='bwr', norm=norm,
            transform=ccrs.PlateCarree()
        )
        ax.set_extent([80, 130, 17, 52], crs=ccrs.PlateCarree())

        # --- 添加省界 ---
        ax.add_geometries(
            Reader(shp).geometries(),
            ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='gray',
            linewidth=0.3
        )

        plot_southsea(ax=ax)

        
        # --- 添加FDR显著性点 ---
        iy, ix = np.where(sig_fdr_plot)
        # code.interact(local=locals())
        if len(iy) > 0:
            step = 5  # 每隔10个点取1个，可调整
            iy_sparse = iy[::step]
            ix_sparse = ix[::step]
            ax.scatter(
                longitude[iy_sparse, ix_sparse], latitude[iy_sparse, ix_sparse],
                s=1.5, c='k', marker='x',
                linewidth = 0.3,
                transform=ccrs.PlateCarree(),
                zorder=5
            )

    
    # --- 添加colorbar ---
        if j == len(path_names) - 1:
            pos = ax.get_position()
            cbar_ax = fig.add_axes([0.92,  # 在第一个子图右侧
                            pos.y0,           # 与子图底部对齐
                            0.015,            # colorbar宽度
                            pos.height*0.9])      # colorbar高度与子图相同

            cbar = fig.colorbar(pcm, cax=cbar_ax)
            cbar.set_label('PV [%]' if var_name == 'PV' else 'GHI [W m$^{-2}$]', rotation=0, fontsize=7)
            cbar.ax.yaxis.set_label_coords(0.5, 1.1)  # (x, y) 相对位置
            # cbar_label.set_horizontalalignment('center')  # 水平居中
            # cbar_label.set_verticalalignment('bottom')    # 垂直底部对齐
            cbar.ax.tick_params(labelsize=7)
            if var_name == 'PV':
                cbar.set_ticks([-0.5, 0, 0.5])
            else:
                cbar.set_ticks([-5, 0, 5])  

    # --- 设置子图标题 ---
        if i == 0:
            ax.set_title(title[j])
    
# 调整布局
# plt.tight_layout(rect=[0, 0, 1, 0.92])  # 为suptitle留出空间

# 保存图片
output_filename = f'./figures/grid_FDR.png'
plt.savefig(output_filename, dpi=600, bbox_inches='tight')    
plt.close()
