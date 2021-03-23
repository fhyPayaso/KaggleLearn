import numpy as np
import cv2
from VerticalGroove import *

IMAGE_SIZE = 1000


def genGrooveImage(size):
    image = np.zeros([IMAGE_SIZE, IMAGE_SIZE], np.uint8)
    start = int(IMAGE_SIZE / 2 - size / 2)
    end = int(IMAGE_SIZE / 2 + size / 2)
    for w in range(IMAGE_SIZE):
        if start <= w <= end:
            continue
        for h in range(IMAGE_SIZE):
            image[h, w] = 255

    # 随机生成添加纵沟的数量
    groove_num = np.random.randint(2, 5)

    for i in range(groove_num):
        # 随机生成纵沟种类
        groove_type = np.random.randint(3)
        if groove_type == 0:
            pass
        elif groove_type == 1:
            pass
        elif groove_type == 2:
            pass

    cv2.imwrite("./dataout/test.png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])


if __name__ == '__main__':
    genGrooveImage(800, 1)
    # emptyImage = np.zeros([1000, 1000], np.uint8)
    #
    # groove_list = [
    #     VerticalStraightLineGroove(100, 1000, 100),
    #     VerticalPolylineGroove(80, 1000, 400, 30, 100),
    #     VerticalWavylineGroove(30, 1000, 700, 5, 100),
    # ]
    # for groove in groove_list:
    #     for data in groove.get_groove_data():
    #         if data.index < 0 or data.index >= 1000:
    #             continue
    #         emptyImage[data.index, int(data.start)] = 255
    #         emptyImage[data.index, int(data.end)] = 255
    #
    # cv2.imwrite("./dataout/cat.png", emptyImage, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
