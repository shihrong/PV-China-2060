import os
import h5py
import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

# 设置字体和格式
matplotlib.rcParams["axes.unicode_minus"] = False
font = {"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 7}
matplotlib.rcParams.update(font)

# 区域格点 ID 映射
egrid = {
    "HD": [10131, 10132, 10133, 10134, 10135],
    "HZ": [10141, 10142, 10143, 10136, 10150, 10151],
    "NF": [10144, 10145, 10146, 10152, 10153],
    "DB": [10121, 10122, 10123],
    "HB": [10111, 10112, 10113, 10114, 10115, 10137],
    "XB": [10161, 10162, 10163, 10164, 10165],
    "XZ": [10154],
}
regions_names = [
    "Eastern",
    "Central",
    "Southern",
    "Northeastern",
    "Northern",
    "Northwestern",
    "Xizang",
]

## 1. 读取地理位置数据用于制作掩膜 (Mask)
f_geo = h5py.File("geo_china_loc.hdf5", "r")
loc = f_geo["china_loc"][:]
f_geo.close()

## 2. 读取模拟数据并计算差值
f1 = h5py.File("GHI_PV_v2.hdf5", "r")
f2 = h5py.File("GHI_PV_2060_MRI.hdf5", "r")

# Ensemble forcing
dghi_ens = f1["ghi_hr_avg"][:] - f1["ghi_bs_avg"][:]
dpv_ens = (f1["PV_hr_avg"][:] - f1["PV_bs_avg"][:]) / 1000 * 100

# MRI forcing
dghi_mri = f2["ghi_hr_avg"][:] - f2["ghi_bs_avg"][:]
dpv_mri = (f2["PV_hr_avg"][:] - f2["PV_bs_avg"][:]) / 1000 * 100

f1.close()
f2.close()


## 3. 定义带 R² 计算和拟合线的散点绘制函数
def plot_scatter(ax, data_x, data_y, xlabel, ylabel, title_str):
    """计算各区域空间平均，在 ax 上绘制散点、1:1线、拟合线，并计算 R²"""
    x_regional = []
    y_regional = []

    # 遍历区域，计算空间平均值
    for (region_code, grid_id), region_name in zip(egrid.items(), regions_names):
        mask = np.isin(loc, grid_id)
        x_mean = np.nanmean(data_x[mask])
        y_mean = np.nanmean(data_y[mask])

        x_regional.append(x_mean)
        y_regional.append(y_mean)

        # 在散点旁边标注区域名称
        ax.text(
            x_mean,
            y_mean,
            f" {region_name}",
            fontsize=6,
            ha="left",
            va="center",
            alpha=0.8,
        )

    x_regional = np.array(x_regional)
    y_regional = np.array(y_regional)

    # ------------------ 计算 R² ------------------
    correlation_matrix = np.corrcoef(x_regional, y_regional)
    r_squared = correlation_matrix[0, 1] ** 2
    print(f"{title_str} - Regional R²: {r_squared:.4f}")

    # ------------------ 线性拟合 ------------------
    slope, intercept = np.polyfit(x_regional, y_regional, 1)

    # ------------------ 绘图控制 ------------------
    # 绘制散点
    ax.scatter(
        x_regional,
        y_regional,
        color="darkblue",
        edgecolors="black",
        linewidths=0.5,
        s=25,
        alpha=0.85,
        zorder=4,
    )

    # 计算坐标轴范围（留出 15% 的边距给文本腾出空间）
    all_vals = np.concatenate([x_regional, y_regional])
    min_val, max_val = min(all_vals), max(all_vals)
    margin = (max_val - min_val) * 0.15 if max_val != min_val else 1
    lims = [min_val - margin, max_val + margin]

    # 1:1 参考线 (黑色虚线)
    ax.plot(lims, lims, "k--", alpha=0.4, lw=0.8, label="1:1 line", zorder=1)

    # 最佳拟合线 (红色实线)
    x_fit = np.linspace(lims[0], lims[1], 100)
    y_fit = slope * x_fit + intercept
    ax.plot(
        x_fit,
        y_fit,
        color="crimson",
        linestyle="-",
        lw=1,
        label="Best fit",
        zorder=2,
    )

    # 限制轴范围
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    # 在图内左上角标注 R²
    ax.text(
        0.05,
        0.92,
        f"$R^2$ = {r_squared:.3f}",
        transform=ax.transAxes,
        fontsize=7,
        fontweight="bold",
        va="top",
        ha="left",
    )

    # 设置标签
    ax.set_xlabel(xlabel, fontsize=7)
    ax.set_ylabel(ylabel, fontsize=7)
    ax.grid(True, linestyle=":", alpha=0.5, zorder=0)


## 4. 开始画图 (1行2列)
width_inches = 14 / 2.54
height_inches = 6.5 / 2.54
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(width_inches, height_inches))
plt.subplots_adjust(
    wspace=0.35, left=0.10, right=0.95, bottom=0.18, top=0.88
)

# =====================================================
# (a) ΔGHI
# =====================================================
plot_scatter(
    axs[0],
    dghi_ens,
    dghi_mri,
    xlabel="Ensemble forcing $\Delta$GHI (W m$^{-2}$)",
    ylabel="MRI forcing $\Delta$GHI (W m$^{-2}$)",
    title_str="(a) $\Delta$GHI",
)
axs[0].set_title("(a) $\Delta$GHI", fontsize=8, fontweight="bold")

# =====================================================
# (b) ΔPVPOT
# =====================================================
plot_scatter(
    axs[1],
    dpv_ens,
    dpv_mri,
    xlabel="Ensemble forcing $\Delta$PVPOT (%)",
    ylabel="MRI forcing $\Delta$PVPOT (%)",
    title_str="(b) $\Delta$PV",
)
axs[1].set_title("(b) $\Delta$PV", fontsize=8, fontweight="bold")

# 保存图片
plt.savefig("./figures/FigS8_scatter_regional_with_R2.png", bbox_inches="tight", dpi=600)
plt.close()
