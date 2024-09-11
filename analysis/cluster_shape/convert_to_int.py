import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.colors as mcolors

class PixelMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8x8 Pixel Matrix")

        self.pixel_matrix = [[0 for _ in range(8)] for _ in range(8)]
        self.buttons = [[None for _ in range(8)] for _ in range(8)]

        for i in range(8):
            for j in range(8):
                button = tk.Button(root, text=' ', width=4, height=2, command=lambda i=i, j=j: self.toggle_pixel(i, j))
                button.grid(row=i, column=j)
                self.buttons[i][j] = button

        self.complete_button = tk.Button(root, text='Complete', command=self.complete)
        self.complete_button.grid(row=8, column=0, columnspan=8)

    def toggle_pixel(self, i, j):
        # Toggle the pixel value
        self.pixel_matrix[i][j] = 1 - self.pixel_matrix[i][j]
        # Update button appearance
        self.buttons[i][j].configure(text='x' if self.pixel_matrix[i][j] else ' ')

    def complete(self):
        # When the complete button is pressed, show the matrix and plot
        self.show_matrix()
        self.plot_pixel_matrix(self.pixel_matrix)

    def show_matrix(self):
        print("Pixel Matrix:")
        for row in self.pixel_matrix:
            print(" ".join('x' if val else 'o' for val in row))

    def plot_pixel_matrix(self, pixel_matrix):
        fig, ax = plt.subplots(figsize=(6, 6))

        cmap = mcolors.LinearSegmentedColormap.from_list("", ["#ffffff", "#1f77b4"])
        ax.imshow(pixel_matrix, cmap=cmap, interpolation='none')

        for i in range(len(pixel_matrix)):
            for j in range(len(pixel_matrix[i])):
                if pixel_matrix[i][j] != 0:
                    rect = patches.Rectangle((j - 0.5, i - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='none')
                    ax.add_patch(rect)

        plt.title("Pixel Matrix")
        plt.xticks([])
        plt.yticks([])
        ax.set_aspect('equal', adjustable='box')
        plt.show()

        decimal_representation = self.convert_to_uint64(pixel_matrix)
        print("Decimal value:", decimal_representation)

    def convert_to_uint64(self, pixel_matrix):
        result = 0
        size = 8
        for i in range(size):
            for j in range(size):
                if pixel_matrix[i][j]:
                    result |= (1 << (i * size + j))
        return result

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelMatrixApp(root)
    root.mainloop()