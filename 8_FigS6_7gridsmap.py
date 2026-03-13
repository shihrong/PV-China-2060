import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import os
import numpy as np
import geopandas as gpd
import matplotlib
import matplotlib.patches as mpatches
from cartopy.io.shapereader import Reader

# 设置中文字体和负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
font = {'font.family': 'Times New Roman',
        'mathtext.fontset': 'stix',
        'font.size': 12}
matplotlib.rcParams.update(font)


def plot_legend(region_colors, ax):
    """创建电网区域图例"""
    color_proxies = []
    labels = []
    # 按区域名称排序
    sorted_regions = sorted(region_colors.items(), key=lambda x: x[0])
    
    for region, color in sorted_regions:
        proxy = mpatches.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='none')
        color_proxies.append(proxy)
        # 区域名称映射
        region_names = {
            'HB': 'Northern',
            'DB': 'Northeastern',
            'HD': 'Eastern',
            'HZ': 'Central',
            'XB': 'Northwestern',
            'XZ': 'Xizang',
            'NF': 'Southern'
        }
        labels.append(f"{region_names.get(region, region)}")

    # 添加图例
    legend = ax.legend(
        color_proxies, labels, 
        loc='lower center',          # 图例锚点位置
        bbox_to_anchor=(0.5, -0.2),  # 相对于ax的位置（x居中，y在ax下方）
        frameon=False,                # 保留边框
        ncol=4,                       # 4列横向排列
        fontsize=7,                   # 缩小字体
        columnspacing=0.4,            # 列间距
        handletextpad=0.1,              # 颜色块和文字间距,
        handlelength=0.6  # 缩短线/标记的长度
    )
    legend.set_zorder(1000)

def plot_southsea(fig, main_ax):
    """绘制南海九段线小地图"""
    # 请替换为你的shapefile路径
    SHP = r'C:\Users\shihr\Documents\MATLAB\all type figure\中国基础数据map'
    shpfilename = os.path.join(SHP, '中国行政区_包含南海九段线.shp')
    
    # 获取主图位置
    main_pos = main_ax.get_position()
    
    # 计算小地图位置（在主图的右下角）
    width_ratio = 0.18  # 小地图宽度比例
    height_ratio = 0.15  # 小地图高度比例
    x_pos = main_pos.x1 - main_pos.width * width_ratio  # 距离右侧边缘
    y_pos = main_pos.y0  # 与主图底部对齐
    
    # 创建小地图的投影和位置
    proj_n = ccrs.LambertConformal(central_latitude=20, central_longitude=115)
    
    # 在fig上创建新的axes作为小地图
    ax_n = fig.add_axes(
        [x_pos, y_pos, main_pos.width * width_ratio, main_pos.height * height_ratio], 
        projection=proj_n
    )
    
    # 设置小地图范围（南海区域）
    ax_n.set_extent([105, 122, 3, 23], ccrs.PlateCarree())
    
    # 添加中国边界
    try:
        ax_n.add_geometries(
            Reader(shpfilename).geometries(),
            ccrs.PlateCarree(), 
            facecolor='none', 
            edgecolor='k', 
            linewidth=0.3
        )
    except Exception as e:
        print(f"读取南海shapefile时出错: {e}")
        # 如果读取失败，画一个简单的矩形框
        ax_n.add_patch(mpatches.Rectangle(
            (105, 3), 17, 20, 
            fill=False, edgecolor='k', linewidth=1,
            transform=ccrs.PlateCarree()
        ))
    
    # 隐藏小地图坐标轴
    ax_n.set_xticks([])
    ax_n.set_yticks([])
    
    # 添加小地图边框
    for spine in ax_n.spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(0.3)

def plot_seven_grids_map(fig, ax):
    """绘制七个电网区域的分布图"""
    
    # 读取中国省份shapefile
    SHP = r'C:\Users\shihr\Documents\MATLAB\all type figure\中国基础数据map'
    shpfilename = os.path.join(SHP, '中国行政区.shp')
    
    try:
        provinces = gpd.read_file(shpfilename)
        provinces = provinces.to_crs("EPSG:4326")  # 转换为WGS84坐标系
    except Exception as e:
        print(f"读取省份shapefile时出错: {e}")
        return
    
    # 定义七个电网区域及其包含的省份
    grid_regions = {
        'HB': ['北京市', '天津市', '河北', '山西', '内蒙古', '山东'],
        'DB': ['辽宁', '吉林', '黑龙江'],
        'HD': ['上海', '江苏', '浙江', '安徽', '福建'],
        'HZ': ['河南', '湖北', '湖南', '江西', '重庆', '四川'],
        'XB': ['陕西', '甘肃', '青海', '宁夏', '新疆'],
        'XZ': ['西藏'],
        'NF': ['广东', '广西', '海南', '贵州', '云南']
    }
    
    # 为每个区域分配不同的颜色
    region_colors = {
        'HB': '#1f77b4',  # 蓝色
        'DB': '#ff7f0e',  # 橙色
        'HD': '#2ca02c',  # 绿色
        'HZ': '#d62728',  # 红色
        'XB': '#9467bd',  # 紫色
        'XZ': '#8c564b',  # 棕色
        'NF': '#e377c2'   # 粉色
    }
    
    # 为每个省份匹配对应的区域颜色
    def get_region_color(province_name):
        """根据省份名称获取对应的区域颜色"""
        for region, province_list in grid_regions.items():
            if province_name in province_list:
                return region_colors[region]
        return 'white'  # 未匹配到的省份用白色
    
    # 添加颜色列
    provinces['color'] = provinces['NAME'].apply(get_region_color)
    
    # 绘制各省份（按区域着色）
    for idx, row in provinces.iterrows():
        ax.add_geometries(
            [row['geometry']], 
            crs=ccrs.PlateCarree(), 
            facecolor=row['color'], 
            edgecolor='black', 
            linewidth=0.5
        )
    
    # 设置主图范围和样式
    ax.set_extent([80, 130, 17, 52], crs=ccrs.PlateCarree())
    ax.set_xticks([])
    ax.set_yticks([])
    
    # 绘制南海小地图（传入fig和主图的ax）
    plot_southsea(fig, ax)
    
    # 添加图例
    plot_legend(region_colors, ax)


# 主程序执行
if __name__ == "__main__":
    # 创建输出目录
    if not os.path.exists('./figures'):
        os.makedirs('./figures')
    
    width_inches = 7 / 2.54  # 转换成英寸
    height_inches = 7 / 2.54
    fig, ax = plt.subplots(1,1,figsize=(width_inches, height_inches),subplot_kw={'projection':  ccrs.LambertConformal(central_latitude=34, central_longitude=110)})
    
    # 绘制七区域电网分布图
    plot_seven_grids_map(fig, ax)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)  # 设置线宽为2，可以根据需要调整
    # 保存图片
    output_path = './figures/map_7grids.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    
    print(f"七区域电网分布图已保存至 {output_path}")