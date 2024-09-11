#include <iostream>
#include <vector>
#include <cstdint>

uint64_t convertToUint64(const std::vector<std::vector<bool>>& pixelMatrix) {
    uint64_t result = 0;
    int size = 8; // 我们处理的最大行数和列数

    for (int i = 0; i < size; ++i) {
        if (i >= pixelMatrix.size()) break; // 如果行超出，停止处理
        for (int j = 0; j < size; ++j) {
            if (j >= pixelMatrix[i].size()) break; // 如果列超出，停止处理
            if (pixelMatrix[i][j]) {
                result |= (1ULL << (i * size + j));
            }
        }
    }
    return result;
}

int testBits() {
    // 示例矩阵，大小可能不一
    std::vector<std::vector<bool>> pixelMatrix = {
        {1, 1},
        {1, 1}
        // {1, 0, 1},
        // {0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0},
        // {0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1},
        // {1, 0, 0, 0, 1, 0, 1, 0},
        // {0, 0, 1, 0, 1}
    };

    // 打印矩阵
    for (const auto& row : pixelMatrix) {
        for (bool pixel : row) {
            std::cout << pixel << " ";
        }
        std::cout << std::endl;
    }

    uint64_t decimalRepresentation = convertToUint64(pixelMatrix);

    std::cout << "Decimal value: " << decimalRepresentation << std::endl;


    // 从十进制数字恢复布尔矩阵
    bool recovered_matrix[8][8];
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            recovered_matrix[i][j] = (decimalRepresentation & (1ULL << (i * 8 + j))) != 0;
        }
    }

    // 打印恢复的矩阵
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            std::cout << recovered_matrix[i][j] << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}
