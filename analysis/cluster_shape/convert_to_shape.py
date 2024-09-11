import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import argparse

def plot_pixel_matrix(pixel_matrices, decimal_numbers, title="Pixel Matrices"):
    # 确保pixel_matrices是列表，即使只有一个元素
    if not isinstance(pixel_matrices, list):
        pixel_matrices = [pixel_matrices]

    fig, axes = plt.subplots(1, len(pixel_matrices), figsize=(6 * len(pixel_matrices), 6))

    # 设置画布背景为白色
    fig.patch.set_facecolor('white')

    # 创建浅蓝色的颜色映射
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["#ffffff", "#1f77b4"])

    # 如果只有一个子图，axes不是数组，所以处理这个情况
    if len(pixel_matrices) == 1:
        axes = [axes]

    for ax, pixel_matrix, decimal_number in zip(axes, pixel_matrices, decimal_numbers):
        ax.imshow(pixel_matrix, cmap=cmap, interpolation='none')

        # 添加边框：只对非零像素添加边框
        for i in range(len(pixel_matrix)):
            for j in range(len(pixel_matrix[i])):
                if pixel_matrix[i][j] != 0:
                    rect = patches.Rectangle((j - 0.5, i - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='none')
                    ax.add_patch(rect)

        ax.set_xticks([])  # 去掉x轴刻度
        ax.set_yticks([])  # 去掉y轴刻度
        ax.set_aspect('equal', adjustable='box')  # 保证像素是方形

        # 隐藏图像的边框线
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # 在每个子图上方添加十进制数字
        ax.set_title(f"{decimal_number}", loc='left')

    plt.suptitle(title)
    plt.show()

def converter(decimal_numbers):
    pixel_matrices = []

    for decimal_representation in decimal_numbers:
        print("Decimal value:", decimal_representation)

        # 从十进制数字恢复布尔矩阵
        recovered_matrix = [[False] * 8 for _ in range(8)]
        for i in range(8):
            for j in range(8):
                recovered_matrix[i][j] = (decimal_representation & (1 << (i * 8 + j))) != 0

        # 打印恢复的矩阵，用 'x' 表示 True，用 'o' 表示 False
        for row in recovered_matrix:
            print(" ".join('x' if val else 'o' for val in row))

        # 添加到矩阵列表中
        pixel_matrices.append(recovered_matrix)

    # 绘制所有恢复的像素矩阵
    plot_pixel_matrix(pixel_matrices, decimal_numbers, title="Recovered Pixel Matrices")


if __name__ == "__main__":
    # 输入多个十进制数字
    parser = argparse.ArgumentParser(description='Convert decimal numbers to boolean matrices.')
    parser.add_argument('decimals', type=int, nargs='+', help='The decimal numbers to convert.')
    args = parser.parse_args()

    # 调用函数
    converter(args.decimals)