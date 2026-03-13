import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import code
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from cartopy.io.shapereader import Reader
import cartopy.feature as cfeature
import h5py
import csv

matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 7}
matplotlib.rcParams.update(font)

def plot_legend(power_output,region_colors,ax):
    # 创建颜色代理对象和标签
    color_proxies = []
    labels = []
    sorted_regions = sorted(power_output.items(), key=lambda x: x[1], reverse=False)
    for i, (region, output) in enumerate(sorted_regions):
        proxy = mpatches.Rectangle((0, 0), 1, 1, facecolor=region_colors[region], edgecolor='black')
        color_proxies.append(proxy)
        labels.append(f"{region.split('_')[0]}: {output:.1f}") # 保留两位小数

    # 在地图上添加图例
    legend = ax.legend(color_proxies, labels, loc='lower left', title='Power Output')
    legend.set_zorder(1000)  # 设置图例的绘制顺序,确保它位于地图之上    

def plot_southsea(ax):
    # south sea
    #  南海
    # SHP = 'Z:/script_share_py/NCL-Chinamap-master/cnmap/'
    SHP=r'C:\Users\shihr\Documents\MATLAB\all type figure\中国基础数据map'
    shpfilename = os.path.join(SHP, '中国行政区_包含南海九段线.shp') # 替换为你的shapefile路径

    pos1 = ax.get_position()
    pos2 = [pos1.x1 - ((pos1.x1 - pos1.x0) / 7), pos1.y0, pos1.width / 7,pos1.height / 5]
    proj_n = ccrs.LambertConformal(central_latitude=90, central_longitude=115)
    ax_n = fig.add_axes(pos2, projection=proj_n)
    ax_n.set_extent([105, 120, 0, 20], ccrs.PlateCarree())
    ax_n.add_geometries(Reader(shpfilename).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='k',linewidth=1)

    # ax_n.add_geometries(Reader(os.path.join(SHP, 'cnhimap.shp')).geometries(),ccrs.PlateCarree(),facecolor='none',edgecolor='k',linewidth=1)
    # ax_n.add_feature(cfeature.OCEAN.with_scale('50m'))
    # ax_n.add_feature(cfeature.LAND.with_scale('50m'))
    # ax_n.add_feature(cfeature.RIVERS.with_scale('50m'))
    # ax_n.add_feature(cfeature.LAKES.with_scale('50m'))



def plot_province_map(region_colors,ax,title,fig_title,mean_value):
    # 读取中国省份数据
    SHP=r'C:\Users\shihr\Documents\MATLAB\all type figure\中国基础数据map'
    shpfilename = os.path.join(SHP, '中国行政区.shp') # 替换为你的shapefile路径
    provinces = gpd.read_file(shpfilename)
    # reader = shpreader.Reader(shpfilename)
    # provinces = reader.records()

    # 定义每个电网区域包含的省份
    grid_regions = {
    'HB': ['北京市', '天津市', '河北', '山西', '内蒙古', '山东'],
    'DB': ['辽宁', '吉林', '黑龙江'],
    'HD': ['上海', '江苏', '浙江', '安徽', '福建'],
    'HZ': ['河南', '湖北', '湖南', '江西','重庆', '四川'],
    'XB': ['陕西', '甘肃', '青海', '宁夏', '新疆'],
    'XZ': [ '西藏'],
    'NF': ['广东', '广西', '海南', '贵州', '云南']
    }

    # 创建一个新的 GeoDataFrame,包含省份名称和对应颜色
    provinces_with_colors = provinces.assign(
        color=[
            region_colors.get(
                '_'.join([region, title]) if region else 'white',
                'white'
            )
            for name in provinces['NAME']
            for region in [next((r for r in grid_regions if name in grid_regions[r]), None)]
        ]
    )

    provinces_with_colors = provinces_with_colors.to_crs("EPSG:4326")
    # provinces_with_colors = provinces_with_colors.to_crs(ccrs.PlateCarree())
    for idx, row in provinces_with_colors.iterrows():
        color = row['color']
        geometry = row['geometry']
        ax.add_geometries([geometry], crs=ccrs.PlateCarree(), facecolor=color, edgecolor='black', linewidth=0.5)

    # 设置地图范围
    ax.text(89,50,mean_value,fontsize = 8, transform=ccrs.PlateCarree())
    ax.set_extent([80, 130, 17, 52], crs=ccrs.PlateCarree())
    # # 移除坐标轴
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(fig_title)

    # # 显示图形
    # plt.show()

# def plot_colormap(power_output,py_cmap):
#     # 按电力出力从小到大排序电网区域
#     sorted_regions = sorted(power_output.items(), key=lambda x: x[1], reverse=False)
#     # 获取viridis颜色映射
#     # cmap = plt.get_cmap('YlOrBr')
#     cmap = plt.get_cmap(py_cmap)

#     # 为每个电网区域分配一种颜色
#     colors = []
#     for i in range(len(sorted_regions)):
#         colors.append( cmap(i / (len(sorted_regions) - 1)))

#     # 为每个电网区域分配一种颜色
#     region_colors = {region: color for (region, _), color in zip(sorted_regions, colors)}
#     return region_colors


def plot_colormap(power_output, py_cmap):
    # 按电力出力从小到大排序电网区域
    sorted_regions = sorted(power_output.items(), key=lambda x: x[1], reverse=False)

    # 找到最大绝对值和最小负值
    max_abs = max(abs(value) for value in power_output.values())
    vmin = -max_abs
    vmax = max_abs

    # 获取指定的颜色映射
    if py_cmap == 'bwr':
        cmap = plt.get_cmap('bwr')
        # cmap = shiftedColorMap(cmap, vmin=vmin, vmax=vmax)
    else:
        cmap = plt.get_cmap(py_cmap)
    
    # 为每个电网区域分配一种颜色
    colors = []
    for i, (region, value) in enumerate(sorted_regions):
        if py_cmap == 'bwr':
            # 根据值在 vmin 和 vmax 范围内线性取值
            color_val = (value - vmin) / (vmax - vmin)
            # color = cmap(color_val)
        else:
            # 所有值映射到从浅到深的颜色范围
            color_val = i / (len(sorted_regions) - 1)
        colors.append(cmap(color_val))
    
    # 为每个电网区域分配一种颜色
    region_colors = {region: color for (region, _), color in zip(sorted_regions, colors)}
    
    # 添加颜色条
    if py_cmap == 'bwr':
        # 确保 vmin、vcenter 和 vmax 的值符合升序排列
        vcenter = 0
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vmax=vmax, vcenter=vcenter)
    else:
        norm = mcolors.Normalize(vmin=min(power_output.values()), vmax=max(power_output.values()))
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    # cbar = plt.colorbar(sm, cax=cbar_ax, orientation='vertical')
    # cbar.ax.set_title(units[i], rotation=0, y=1.01, fontsize=10)
    
    return region_colors, sm

def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero.

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower offset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center for the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the middle of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highest point in the colormap's range.
          Defaults to 1.0 (no upper offset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # Regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # Shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = mcolors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap
# egrid = ['DB','HB','XB','XZ','HZ','HD','NF']
egrid = {
'HD': [10131, 10132, 10133, 10134, 10135],
'HZ': [10141, 10142, 10143, 10136,10150, 10151],
'NF': [10144, 10145, 10146, 10152, 10153],
'DB': [10121, 10122, 10123],
'HB': [10111, 10112, 10113, 10114,10115, 10137],
'XB': [10161, 10162, 10163, 10164, 10165],
'XZ': [ 10154]
}
# var_names = ['ghi','ghi_c','AOD','COD']
# var_names = ['PV', 'ghi','T2','U10']
var_names = ['ghi','ghi','ghi','AOD','COD']
# var_names = ['LWP','QNCLOUD']

path_names = ['hb','cs','hr']
title = ['HB-BS','CS-BS','HR-BS']
# Scenarios = ['BS','HB','CS','HR']
units = ['GHI [Wm$^{-2}$]','ARI [Wm$^{-2}$]','ACI [Wm$^{-2}$]','AOD','COD']
# units = ['LWP [g/m$^{2}$]','NDROP [$10^{10}$/m$^{2}$]']
# units = ['NDROP [$10^{10}$/m$^{2}$]']
# units = ['GHI$_{ACI}$ [Wm$^{-2}$]']
# units = ['GHI$_{ARI}$ [Wm$^{-2}$]']

# units = ['GHI [Wm$^{-2}$]','GHI_c [Wm$^{-2}$]','AOD','COD']
# path_names = ['bau']
# py_cmap = ['OrRd','bwr']
py_cmap = ['bwr','bwr']

## 读数据
f = h5py.File('geo_china_loc.hdf5', 'r')  
longitude =  f['longitude'][:]
latitude =  f['latitude'][:]
loc = f['china_loc'][:]

# 创建一个新的CSV文件,写入标题行
fieldnames = ['region'] + var_names
df = pd.DataFrame(columns=fieldnames)
# df.to_csv('2060_region_data.csv', index=False)
## 画图
width_inches = 16 / 2.54  # 转换成英寸
height_inches = 20 / 2.54
fig, axs = plt.subplots(
    nrows=len(var_names),      # 5 行
    ncols=len(path_names),     # 3 列,
    figsize=(width_inches, height_inches),subplot_kw={'projection':  ccrs.LambertConformal(central_latitude=34, central_longitude=110)})
axs = axs.reshape(len(var_names), len(path_names))  # 保证 2 维索引
plt.subplots_adjust(wspace=0.02, hspace=0.01, left=0.12, right=0.88, bottom=0.08, top=0.92)

for i, var_name in enumerate(var_names):

    data = {}
    for j,path_name in enumerate(path_names):
        f3 = h5py.File('GHI_2060_noACI.hdf5', 'r')
        f2 = h5py.File('GHI_2060_ARIoff.hdf5', 'r')

        # f1 = h5py.File('LWP_QNCLOUD.hdf5', 'r')  
        f1 = h5py.File('GHI_PV_2060_v2.hdf5', 'r')  

        print(f'{var_name}_{path_name}_avg')
        if i == 1: # ARI
            tmp =  f1[f'{var_name}_{path_name}_avg'][:] - f2[f'{var_name}_{path_name}_avg'][:] - (f1[f'{var_name}_bs_avg'][:] - f2[f'{var_name}_bs_avg'][:])
        elif i == 2: # ACI
            tmp =  f1[f'{var_name}_{path_name}_avg'][:] - f3[f'{var_name}_{path_name}_avg'][:] - (f1[f'{var_name}_bs_avg'][:] - f3[f'{var_name}_bs_avg'][:])
        else:
            tmp =  f1[f'{var_name}_{path_name}_avg'][:] - f1[f'{var_name}_bs_avg'][:] 



        for region_name,grid_id in egrid.items():
            # print(f"Key: {region_name}, Value: {grid_id}")
            mask = np.isin(loc, grid_id)   # 选出每个region 的mask
            data[f'{region_name}_{title[j]}'] = np.nanmean(tmp[mask])

    # code.interact(local=locals())
    print(min(data.values()))
    print(max(data.values()))
    # 保存 data 数据
    # 将数据字典写入CSV文件

    # 将当前列的数据添加到DataFrame中
    if i == 0:
         df['region'] = list(data.keys())
    df[var_name] = list(data.values())

    # region_colors,py_cmap = plot_colormap(power_output=data,py_cmap=None)
    # code.interact(local=locals())


    for j,path_name in enumerate(path_names):
        # code.interact(local=locals())


        ax = axs[i, j]                       # 取到对应子图

        region_colors,sm = plot_colormap(power_output=dict(list(data.items())),py_cmap=py_cmap[1])

        mean_value = np.mean(list(data.values())[j*7:j*7+7])# 计算平均值
        
        # # code.interact(local=locals())
        if i ==0:
            mean_value1 = f'avg={mean_value:.2f}'  # 保留两位小数,只有PV显示
            title1 = title[j]

        else:
            mean_value1 = f'avg={mean_value:.2f}'  # 保留两位小数,只有PV显示
            # mean_value1 = ''  # 保留两位小数
            title1 = ''
            # print(mean_value)
        # # code.interact(local=locals())

        plot_province_map(region_colors,ax=ax,title=title[j],fig_title = title1,mean_value=mean_value1)
        # 画南海
        plot_southsea(ax=ax)


        # 将diff的colorbar放在最右边
        if j == len(path_names)-1:
            cbar_ax = fig.add_axes([0.92, ax.get_position().y0, 0.015, ax.get_position().height*0.9])
            cbar = plt.colorbar(sm, cax=cbar_ax, orientation='vertical')        
            cbar.set_label(units[i], rotation=0,  fontsize=7)  # 设置标题及其位置和字体大小
            cbar.ax.yaxis.set_label_coords(0.55, 1.13)  # (x, y) 相对位置
            cbar.ax.tick_params(labelsize=7)
            if i == 0:
                cbar.set_ticks([-5, 0, 5])  
            if i == 1:
                cbar.set_ticks([-1, 0, 1])  
            if i == 2:
                cbar.set_ticks([-4, 0, 4])  
                        
            # 调整颜色条位置
            cbar.ax.yaxis.set_ticks_position('right')
            cbar.ax.yaxis.set_label_position('right')

    # 设置紧凑布局
    # plt.tight_layout()
    # plt.savefig(f'./figures/map_{var_name}_ACIoff_on_diff_v2.png', bbox_inches='tight')
plt.savefig(f'./figures/Fig3_map_ACI_ARI_diff.png', bbox_inches='tight', dpi=600)

plt.close()
    # print(power_grid)

# df.to_csv('2060_region_data_diff_.csv', index=False)
# save the mean of HB-BS PV