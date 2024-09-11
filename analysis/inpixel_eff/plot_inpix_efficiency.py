import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches as pat
import os

def plot_inpix(varname, data, fname_out, chip, hfunit, region, vcasb = 0):
    # 行和列的数量
    unique_columns = 9
    total_entries = 81
    unique_rows = total_entries // unique_columns

    # 根据 varname 决定使用哪一组数据
    if varname == "meancluster":
        var = np.array(data.get('clustersize', [])).reshape(unique_rows, unique_columns)
        errlow = np.array(data.get('errorlow', [])).reshape(unique_rows, unique_columns)
        errup = np.array(data.get('errorup', [])).reshape(unique_rows, unique_columns)
        tot_var = np.mean(var)
        var_range = (1, 1.8)
        offset = 1.35
    else:
        var = np.array(data.get('efficiency', [])).reshape(unique_rows, unique_columns) * 100
        errlow = np.array(data.get('errorlow', [])).reshape(unique_rows, unique_columns) * 100
        errup = np.array(data.get('errorup', [])).reshape(unique_rows, unique_columns) * 100
        tot_var = data.get('total_efficiency', 0) * 100
        var_range = (90, 100)
        offset = 90
    
    scale = (var_range[1] - var_range[0]) / (100. - 90.)

    c = ["#56B4E9", "#E69F00", "#009E73"]

    # 根据 hfunit 设置 d 值
    if hfunit == "bb":
        d = 18.0 / 2
        inpix_len = 18.0 / 9
    elif hfunit == "tb":
        d = 22.5 / 2
        inpix_len = 22.5 / 9
    else:
        raise ValueError("Unexpected hfunit value. Should be either 'bb' or 'tb'.")

    na = 4
    head_length = 0.35
    head_width = 0.4
    circle_coo = (d / 2, 0)

    fig, ax = plt.subplots(1, 2, figsize=(10.5, 4))
    plt.subplots_adjust(wspace=0.5, top=0.98, left=0.1, right=0.84, bottom=0.03)
    plt.sca(ax[0])
    im = plt.imshow(var, extent=[-d, d, -d, d], vmin=var_range[0], vmax=var_range[1], origin='lower', cmap='cividis')
    cb = plt.colorbar(im, pad=0.015, fraction=0.0480)
    for i in range(na):
        plt.arrow(0, i * inpix_len, 0, inpix_len, head_width=head_width, head_length=head_length, color=c[0], length_includes_head=True, zorder=100, clip_on=False)
        plt.arrow(i * inpix_len, d - inpix_len/2, inpix_len, 0, head_width=head_width, head_length=head_length, color=c[1], length_includes_head=True, zorder=100, clip_on=False)
        plt.arrow(d - i * inpix_len - inpix_len/2, d - i * inpix_len - inpix_len/2, -inpix_len, -inpix_len, head_width=head_width, head_length=head_length, color=c[2], length_includes_head=True, zorder=100, clip_on=False)

    plt.plot([0], [0], marker='.', color=c[0], zorder=99, clip_on=False)
    plt.plot([0], [d - inpix_len/2], marker='.', color=c[1], zorder=99, clip_on=False)
    plt.plot([d - inpix_len/2], [d - inpix_len/2], marker='.', color=c[2], zorder=99, clip_on=False)
    # ax[0].add_patch(pat.Circle(circle_coo, 2.4, color='white', alpha=0.33))
    # plt.annotate('Tracking\nresolution\n$\\sigma=2.4$ µm', circle_coo, color='white', horizontalalignment='center', verticalalignment='center')
    plt.annotate('A', (0, 0), color=c[0], fontweight="bold", xytext=(0, -4), textcoords='offset points', horizontalalignment='center', verticalalignment='top')
    plt.annotate('B', (0, d), color=c[1], fontweight="bold", xytext=(0, 2), textcoords='offset points', horizontalalignment='center', verticalalignment='bottom')
    plt.annotate('C', (d, d), color=c[2], fontweight="bold", xytext=(0, 2), textcoords='offset points', horizontalalignment='center', verticalalignment='bottom')
    cb.set_label("Average cluster size (pixels)" if varname == "meancluster" else "Detection efficiency (%)")
    plt.xticks(np.linspace(-d, d, 7))
    plt.yticks(np.linspace(-d, d, 7))
    plt.xlabel("In-pixel track intercept x (µm)")
    plt.ylabel("In-pixel track intercept y (µm)")
    plt.xlim(-d, d)
    plt.ylim(-d, d)

    pitch_size = 18.0 if hfunit == "bb" else 22.5
    half_unit_name = "Bottom half unit" if hfunit == "bb" else "Top half unit"
    

    # 在图像右侧添加文本信息
    ax[1].text(1.05, 0.85, f"{chip}",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center', fontweight='bold')
    ax[1].text(1.05, 0.80, f"{half_unit_name}, region {region}",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.75, f"Pitch: {pitch_size} $\\mathit{{µm}}$",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.70, "$I_{\\text{bias}} = 62$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.65, "$I_{\\text{biasn}} = 100$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.60, "$I_{\\text{reset}} = 10$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.55, "$I_{\\text{db}} = 50$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.50, "$V_{\\text{shift}} = 145$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.45, f"$V_{{\\text{{casb}}}} = {vcasb}$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.40, f"$V_{{\\text{{casn}}}}  104$ DAC",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')
    ax[1].text(1.05, 0.35, "T = 27 $^{\\circ}$C",
               transform=ax[1].transAxes, fontsize=8, verticalalignment='center')


    # 函数：生成路径
    def matrix_to_path(var, inpix_len):
        x = []
        y = []
        y_low = []
        y_up = []
        segments = []

        # AB路径：5段折线
        ab_coords = [(4, 4), (3, 4), (2, 4), (1, 4), (0, 4)]
        start_x = 0

        for i, (row, col) in enumerate(ab_coords):
            end_x = start_x + (inpix_len / 2 if i == 0 or i == len(ab_coords) - 1 else inpix_len)
            x_ab = np.linspace(start_x, end_x, 100, endpoint=False)
            y_ab = np.full_like(x_ab, var[row, col])
            y_ab_low = np.full_like(x_ab, errlow[row, col])
            y_ab_up = np.full_like(x_ab, errup[row, col])
            x.append(x_ab)
            y.append(y_ab)
            y_low.append(y_ab_low)
            y_up.append(y_ab_up)
            segments.append((x_ab, y_ab, y_ab_low, y_ab_up, c[0]))
            start_x = end_x

        # BC路径：5段折线
        bc_coords = [(0, 4), (0, 5), (0, 6), (0, 7), (0, 8)]
        start_x = 4 * inpix_len

        for row, col in bc_coords:
            end_x = start_x + (inpix_len / 2 if col == 4 or col == 8 else inpix_len)
            x_bc = np.linspace(start_x, end_x, 100, endpoint=False)
            y_bc = np.full_like(x_bc, var[row, col])
            y_bc_low = np.full_like(x_bc, errlow[row, col])
            y_bc_up = np.full_like(x_bc, errup[row, col])
            x.append(x_bc)
            y.append(y_bc)
            y_low.append(y_bc_low)
            y_up.append(y_bc_up)
            segments.append((x_bc, y_bc, y_bc_low, y_bc_up, c[1]))
            start_x = end_x

        # CA路径：5段折线
        ca_coords = [(0, 8), (1, 7), (2, 6), (3, 5), (4, 4)]
        start_x = 8 * inpix_len

        for i, (row, col) in enumerate(ca_coords):
            length = (inpix_len / 2 if i == 0 or i == len(ca_coords) - 1 else inpix_len) * np.sqrt(2)
            end_x = start_x + length
            x_ca = np.linspace(start_x, end_x, 100, endpoint=False)
            y_ca = np.full_like(x_ca, var[row, col])
            y_ca_low = np.full_like(x_ca, errlow[row, col])
            y_ca_up = np.full_like(x_ca, errup[row, col])
            x.append(x_ca)
            y.append(y_ca)
            y_low.append(y_ca_low)
            y_up.append(y_ca_up)
            segments.append((x_ca, y_ca, y_ca_low, y_ca_up, c[2]))
            start_x = end_x

        return np.concatenate(x), np.concatenate(y), np.concatenate(y_low), np.concatenate(y_up), segments

    x, y, y_low, y_up, segments = matrix_to_path(var, inpix_len)

    plt.sca(ax[1])
    start_idx = 0
    for seg_x, seg_y, seg_y_low, seg_y_up, color in segments:
        end_idx = start_idx + len(seg_y)
        
        # 绘制误差带和曲线
        plt.fill_between(seg_x, seg_y - seg_y_low, seg_y + seg_y_up, color=color, alpha=0.3)
        plt.plot(seg_x, seg_y, color=color)
        
        # 在每个段的末尾与下一段的起始点之间绘制密集的点
        if end_idx < len(y):  # 确保不会超出数组范围
            x_dense = np.linspace(seg_x[-1], seg_x[-1], 10)  # 保持x值不变
            y_dense = np.linspace(seg_y[-1], y[end_idx], 10)  # 在当前y和下一段y之间插入点
            plt.plot(x_dense, y_dense, color=color, marker='.', markersize=0, linestyle='-')
        
        start_idx = end_idx

    plt.xlim(x[0] - 0.1, x[-1])
    plt.xticks([0, 4 * inpix_len, 8 * inpix_len, 8 * inpix_len + 4 * inpix_len * np.sqrt(2)])
    plt.ylim(var_range)
    plt.grid(axis='both')
    plt.xlabel("Distance along the path (µm)")
    plt.ylabel("Average cluster size (pixels)" if varname == "meancluster" else "Detection efficiency (%)")
    secax = ax[1].secondary_xaxis('top')
    secax.set_xticks([0, 4 * inpix_len, 8 * inpix_len, 8 * inpix_len + 4 * inpix_len * np.sqrt(2)])
    #secax.set_xticklabels(['A', 'B', 'C', 'A'], fontweight="bold", color='black')
    for i,t in enumerate(secax.set_xticklabels(['A','B','C','A'],fontweight="bold")):
      t.set_color(c[i%3])

    plt.axhline(tot_var, linestyle='dotted', color='grey')
    # plt.text(14.5, tot_var, f"Total efficiency", ha='center', va='bottom', color='grey')
    # 如果varname是meancluster，那么是"Average cluster size"，否则是"Total efficiency"
    # 写上总效率的值或者平均簇大小的值
    plt.text(14.5, tot_var, f"Average cluster size {tot_var:.2f}" if varname == "meancluster" else f"Total efficiency {tot_var:.2f} %" , ha='center', va='bottom', color='grey')
    # plt.text(14.5, tot_var, f"{tot_var:.2f}", ha='center', va='top', color='grey')
    # plt.annotate("Stat. error", xy=(14.5, tot_var),
    #          verticalalignment="center", zorder=9,
    #          bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.5))

    ax[1].add_patch(pat.Rectangle((0.5, offset + 1.5 * scale), 11, 3 * scale, facecolor="white", edgecolor="grey", linewidth=0.5, zorder=9))
    ax[1].add_patch(pat.Rectangle((1, offset + 2 * scale), 1, 2 * scale, color=c[0], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((2, offset + 2 * scale), 1, 2 * scale, color=c[1], alpha=0.3, zorder=9))
    ax[1].add_patch(pat.Rectangle((3, offset + 2 * scale), 1, 2 * scale, color=c[2], alpha=0.3, zorder=9))
    plt.annotate("Stat. error", xy=(4.5, offset + 3 * scale),
             verticalalignment="center", zorder=9,
             bbox=dict(boxstyle="round,pad=0.3", edgecolor="none", facecolor="white", alpha=0.5))

    asp = np.diff(ax[1].get_xlim())[0] / np.diff(ax[1].get_ylim())[0]
    ax[1].set_aspect(asp * 0.95)

    plt.savefig(fname_out + ".pdf")
    plt.savefig(fname_out + ".png")
    plt.close()

def process_json_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(input_directory, filename)

            # 解析文件名以提取相关信息
            name_parts = filename.split('_')
            moss_name = name_parts[0] + "_" + name_parts[1] + "_" + name_parts[2]
            hfunit = name_parts[3].lower().strip()  # convert to lowercase and remove extra spaces
            region = name_parts[4].replace('region', '')
            vcasb = name_parts[5].replace('VCASB', '')
            varname = "meancluster" if "clustersize" in filename else "efficiencies"

            # Debugging output to check the values
            print(f"moss={moss_name}, hfunit={hfunit}, region={region}, vcasb={vcasb}, varname={varname}")

            # Check if hfunit is valid
            if hfunit not in ["bb", "tb"]:
                print(f"Skipping file {filename} due to unexpected hfunit value: {hfunit}")
                continue

            # 打开 JSON 文件
            with open(file_path) as f:
                data = json.load(f)

            # 创建输出文件名
            output_file = os.path.join(output_directory, f"{moss_name}_{hfunit}_region{region}_VCASB{vcasb}_{varname}")
            
            # 调用绘图函数
            plot_inpix(varname, data, output_file, moss_name, hfunit, region, vcasb)

if __name__ == "__main__":
    input_directory = "./json_files_inpixel"
    output_directory = "./plots"
    process_json_files(input_directory, output_directory)