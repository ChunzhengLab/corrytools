import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.colors as mcolors

def convert_to_uint64(pixel_matrix):
    result = 0
    size = 8  # 我们处理的最大行数和列数

    for i in range(size):
        if i >= len(pixel_matrix):
            break  # 如果行超出，停止处理
        for j in range(size):
            if j >= len(pixel_matrix[i]):
                break  # 如果列超出，停止处理
            if pixel_matrix[i][j]:
                result |= (1 << (i * size + j))

    return result

def plot_pixel_matrix(pixel_matrix, title="Pixel Matrix"):
    fig, ax = plt.subplots(figsize=(6, 6))

    # 创建浅蓝色的颜色映射
    cmap = mcolors.LinearSegmentedColormap.from_list("", ["#e6f0ff", "#1f77b4"])

    ax.imshow(pixel_matrix, cmap=cmap, interpolation='none')

    # 添加边框：只对非零像素添加边框
    for i in range(len(pixel_matrix)):
        for j in range(len(pixel_matrix[i])):
            if pixel_matrix[i][j] != 0:
                rect = patches.Rectangle((j - 0.5, i - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='none')
                ax.add_patch(rect)

    plt.title(title)
    plt.xticks([])  # 去掉x轴刻度
    plt.yticks([])  # 去掉y轴刻度
    ax.set_aspect('equal', adjustable='box')  # 保证像素是方形
    plt.show()

def test_bits():
    # 示例矩阵，大小可能不一
    pixel_matrix = [
        [1, 1]
        # [1, 1],
        # [1, 0, 1],
        # [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0]
    ]

    # 打印矩阵
    for row in pixel_matrix:
        print(" ".join(map(str, row)))

    # 将矩阵填充为8x8
    padded_matrix = [[0] * 8 for _ in range(8)]
    for i in range(min(8, len(pixel_matrix))):  # 确保不超过8行
        for j in range(min(8, len(pixel_matrix[i]))):  # 确保不超过8列
            padded_matrix[i][j] = pixel_matrix[i][j]

    # 绘制原始像素矩阵
    plot_pixel_matrix(padded_matrix, title="Original Pixel Matrix")

    decimal_representation = convert_to_uint64(padded_matrix)
    print("Decimal value:", decimal_representation)

    # 从十进制数字恢复布尔矩阵
    recovered_matrix = [[False] * 8 for _ in range(8)]
    for i in range(8):
        for j in range(8):
            recovered_matrix[i][j] = (decimal_representation & (1 << (i * 8 + j))) != 0

    # 打印恢复的矩阵，用 'x' 表示 True，用 'o' 表示 False
    for row in recovered_matrix:
        print(" ".join('x' if val else 'o' for val in row))

    # 绘制恢复的像素矩阵
    plot_pixel_matrix(recovered_matrix, title="Recovered Pixel Matrix")


if __name__ == "__main__":
    test_bits()