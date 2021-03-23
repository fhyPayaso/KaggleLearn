import numpy as np
import cv2
from matplotlib import pyplot as plt

if __name__ == '__main__':
    img = cv2.imread('./data/data2.jpeg', 0)
    # img = cv2.imread('./data/tyre.png', 0)
    # img = cv2.GaussianBlur(img, (3, 3), 0)

    edges = cv2.Canny(img, 100, 200)

    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('original')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(1, 2, 2)
    plt.imshow(edges, cmap='gray')
    plt.title('edge')
    plt.xticks([])
    plt.yticks([])

    plt.show()



    # cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
