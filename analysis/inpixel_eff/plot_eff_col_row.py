import json
import matplotlib.pyplot as plt

# 从JSON文件中读取数据
with open('json_files_inpixel/babyMOSS-2_3_W04E2_tb_region0_VCASB68_highstat_col_row_eff.json', 'r') as file:
    data = json.load(file)

# 提取行和列的相关数据
row_indices = data['row']
row_eff = data['row_eff']
row_eff_errorup = data['row_eff_errorup']
row_eff_errorlow = data['row_eff_errorlow']

column_indices = data['column']
column_eff = data['column_eff']
column_eff_errorup = data['column_eff_errorup']
column_eff_errorlow = data['column_eff_errorlow']

# 设置变量值用于显示在右侧的文本
chip = "Chip XYZ"
half_unit_name = "Half Unit A"
region = "3"
pitch_size = 75  # 微米
vcasb = 76

# 创建两个子图：一个用于row，一个用于column
fig, axs = plt.subplots(1, 2, figsize=(18, 6))

# 绘制row效率数据
axs[0].errorbar(row_indices, row_eff, yerr=[row_eff_errorlow, row_eff_errorup], fmt='o', ecolor='r', capsize=3, label='Row Efficiency')
axs[0].set_title('Row Efficiency')
axs[0].set_xlabel('Row Index')
axs[0].set_ylabel('Efficiency')
axs[0].set_ylim(0, 1.1)
axs[0].grid(True)

# 绘制column效率数据
axs[1].errorbar(column_indices, column_eff, yerr=[column_eff_errorlow, column_eff_errorup], fmt='o', ecolor='b', capsize=3, label='Column Efficiency')
axs[1].set_title('Column Efficiency')
axs[1].set_xlabel('Column Index')
axs[1].set_ylabel('Efficiency')
axs[1].set_ylim(0, 1.1)
axs[1].grid(True)

# 在图像右侧添加文本信息
axs[1].text(1.05, 0.85, f"{chip}",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center', fontweight='bold')
axs[1].text(1.05, 0.80, f"{half_unit_name}, region {region}",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.75, f"Pitch: {pitch_size} $\\mathit{{µm}}$",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.70, "$I_{\\text{bias}} = 62$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.65, "$I_{\\text{biasn}} = 100$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.60, "$I_{\\text{reset}} = 10$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.55, "$I_{\\text{db}} = 50$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.50, "$V_{\\text{shift}} = 145$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.45, f"$V_{{\\text{{casb}}}} = {vcasb}$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.40, "$V_{\\text{casn}}  = 104$ DAC",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')
axs[1].text(1.05, 0.35, "T = 27 $^{\\circ}$C",
            transform=axs[1].transAxes, fontsize=8, verticalalignment='center')

# 调整布局并显示图表
plt.tight_layout()
plt.show()