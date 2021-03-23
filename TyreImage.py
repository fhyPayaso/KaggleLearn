import numpy as np
import cv2
from VerticalGroove import *

IMAGE_SIZE = 1000


class TyreImage:
    def __init__(self, index):
        """
        单张轮胎图片实体类
        :param index: 图片编号
        :param center_size:
        :param margin:
        """
        # 图片大小
        self.height = IMAGE_SIZE
        self.width = IMAGE_SIZE
        self.id = index  # 图片编号
        self.file_name = "tyre_{}.png".format(index)  # 图片文件名
        self.pattern_list = []  # 花纹列表
        self.render_pattern_list = []  # 真正渲染出来的花纹
        # 真实图片数据
        self.image = np.zeros([self.height, self.width], np.uint8)
        self.start = 0  # 轮胎开始列
        self.end = 0  # 轮胎结束列

    def init_empty_image(self, center_size):
        self.start = int(self.width / 2 - center_size / 2)
        self.end = int(self.width / 2 + center_size / 2)
        for w in range(self.width):
            if self.start <= w <= self.end:
                continue
            for h in range(self.height):
                self.image[h, w] = 255

    def build_pattern_list(self, margin):
        index = self.start + margin
        while index < self.end - margin:
            # 随机宽度
            pattern_width = np.random.randint(20, 100)
            # 随机选择中心点
            center_index = np.random.randint(
                index + pattern_width / 2,
                index + pattern_width)
            # 计算每段长度(对直线不生效)
            segment_length = int(self.height / np.random.randint(5, 20))
            groove = None
            # 随机生成纵沟种类
            groove_type = np.random.randint(1, 4)
            if groove_type == 1:
                groove = VerticalStraightLineGroove(pattern_width, IMAGE_SIZE, center_index)
            elif groove_type == 2:
                angle = np.random.randint(10, 60)
                groove = VerticalPolylineGroove(pattern_width, IMAGE_SIZE, center_index, angle, segment_length)
            elif groove_type == 3:
                omega = np.random.randint(2, 10)
                groove = VerticalWavylineGroove(pattern_width, IMAGE_SIZE, center_index, omega, segment_length)
            if groove is not None:
                self.pattern_list.append(groove)
                index = groove.bbox[0] + groove.bbox[2] + margin

    def render(self):

        for groove in self.pattern_list:
            left = groove.bbox[0]
            right = left + groove.bbox[2]
            if left < self.start or right >= self.end:
                continue
            for data in groove.get_groove_data():
                if data.index < 0 or data.index >= self.height:
                    continue
                self.image[data.index, int(data.start)] = 255
                self.image[data.index, int(data.end)] = 255
                groove.render_groove_data.append(data)
            groove.build_segmentation()
            self.render_pattern_list.append(groove)

    def save(self, path):
        cv2.imwrite("{}/{}".format(path, self.file_name), self.image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        print("{} build done".format(self.file_name))
