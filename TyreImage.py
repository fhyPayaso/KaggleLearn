import numpy as np
import cv2
from VerticalGroove import *
from HorizontalGroove import *

IMAGE_SIZE = 512


class TyreImage:
    def __init__(self, index, center_size):
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
        self.center_size = center_size
        self.file_name = "tyre_{}.png".format(index)  # 图片文件名
        self.pattern_list = []  # 花纹列表
        self.horizontal_group_list = []  # 横向花纹组列表
        self.render_pattern_list = []  # 真正渲染出来的花纹
        # 真实图片数据
        self.image = np.zeros([self.height, self.width], np.uint8)
        self.image_start = 0  # 轮胎开始列
        self.image_end = 0  # 轮胎结束列

        # 初始化方法
        self.__init_empty_image()
        self.__build_vertical_pattern_list()
        self.__build_horizontal_pattern_list()

    def __init_empty_image(self):
        """
        构建轮胎初始图片
        :param center_size: 轮胎部分宽度
        :return:
        """
        self.image_start = 10
        self.image_end = self.width - 10
        # self.image_start = int(self.width / 2 - self.center_size / 2)
        # self.image_end = int(self.width / 2 + self.center_size / 2)
        # for w in range(self.width):
        #     if self.image_start <= w <= self.image_end:
        #         continue
        #     for h in range(self.height):
        #         self.image[h, w] = 255

    def __build_vertical_pattern_list(self):
        """
        首先构建图片纵向花纹, 纵向花纹一般呈现对称分布
        构建时分为单双两种类型:
            单数类型, 3或5(中间沟不宜过大)
            双数类型, 4或6
        :return:
        """
        image_center = (self.image_start + self.image_end) / 2
        # pattern_num = 1
        pattern_num = np.random.randint(1, 5)
        margin = np.random.randint(30, 50)
        center_diff = margin  # 当前与轮胎中心的距离
        # 若为单数,先生成中间的(中间花纹宽度不能过大)
        if pattern_num % 2 == 1:  # 单数类型
            # pattern_num -= 1
            pattern_width = np.random.randint(20, 40)
            groove = self.__gen_vertical_pattern_pair(pattern_width, image_center)
            center_diff += groove[0].bbox[2] / 2
            self.pattern_list.extend(groove)
        pattern_num /= 2
        # 从中间向两侧对称生成
        for i in range(0, int(pattern_num)):
            pattern_width = np.random.randint(40, 60)
            groove = self.__gen_vertical_pattern_pair(pattern_width, image_center, center_diff, 2)
            center_diff += (margin + groove[0].bbox[2])
            self.pattern_list.extend(groove)
        # 构建之后直接渲染到图片上
        self.__render_vertical_pattern()

    def __gen_vertical_pattern_pair(self, pattern_width, image_center, diff=0, groove_num=1):
        """
        生成单个或一对纵向花纹
        :param pattern_width: 纵向花纹宽度
        :param image_center: 轮胎图片中心点
        :param diff: 当前花纹距离中心点距离
        :param groove_num: 花纹数量，只能为1或2
        :return: 单个花纹或花纹对
        """
        # 计算每段长度(对直线不生效)
        segment_length = int(self.height / np.random.randint(5, 20))
        # 随机生成纵沟种类
        groove_type = np.random.randint(1, 4)
        # groove_type = 1
        # 随机生成角度
        angle = np.random.randint(10, 20)
        # 随机生成振幅
        omega = np.random.randint(2, 10)
        pattern_pair = []
        center_index = image_center
        for i in range(groove_num):
            if groove_num == 2 and i == 0:
                center_index = image_center + diff + pattern_width / 2
            elif groove_num == 2 and i == 1:
                center_index = image_center - diff - pattern_width / 2

            # # 检测中间点
            # for _h in range(0, 1000):
            #     self.image[_h, int(center_index)] = 255
            if groove_type == 1:
                pattern_pair.append(VerticalStraightLineGroove(
                    pattern_width, IMAGE_SIZE, center_index))
            elif groove_type == 2:
                pattern_pair.append(VerticalPolylineGroove(
                    pattern_width, IMAGE_SIZE, center_index, angle, segment_length))
            else:
                pattern_pair.append(VerticalWavylineGroove(
                    pattern_width, IMAGE_SIZE, center_index, omega, segment_length))
        return pattern_pair

    def __render_vertical_pattern(self):
        """
        过滤并渲染纵向花纹
        :return:
        """
        for groove in self.pattern_list:
            left = groove.bbox[0]
            right = left + groove.bbox[2]
            if left < self.image_start or right >= self.image_end:
                continue
            for data in groove.get_groove_data():
                if data.index < 0 or data.index >= self.height:
                    continue
                for w in range(int(data.start), int(data.end)):
                    self.image[data.index, w] = 255
                # self.image[data.index, int(data.start)] = 255
                # self.image[data.index, int(data.end)] = 255
                groove.render_groove_data.append(data)

            groove.build_bbox()
            groove.build_segmentation()
            self.render_pattern_list.append(groove)

    def __build_horizontal_pattern_list(self):
        """
        构建横向花纹
        :return:
        """
        self.render_pattern_list.sort(key=lambda p: p.bbox[0])
        start_index = self.image_start
        v_groove_num = len(self.render_pattern_list)
        for i in range(v_groove_num + 1):
            if i < v_groove_num:
                groove = self.render_pattern_list[i]
                end_index = groove.bbox[0] + groove.bbox[2] / 2
                next_start = groove.bbox[0] + groove.bbox[2] / 2
            else:
                end_index = self.image_end
                next_start = self.image_end

            # print(start_index, end_index)
            # 在start~end范围内构建横沟
            all_range = end_index - start_index
            if all_range < 50:
                start_index = next_start
                continue

            # 在两个纵沟之间有多少个种类的横沟(1,2)
            type_num = np.random.randint(1, 3)
            # 斜直线沟倾斜角度的方向
            for cur_type in range(type_num):
                # 随机横沟种类之一
                h_groove_type = np.random.randint(4, 7)
                # h_groove_type = 6
                # 随机数据类
                random_data = RandomData(range_left_col=30, range_right_col=int(all_range))
                groove_group = HorizontalGrooveGroup(start_index, end_index,
                                                     h_groove_type, random_data)
                self.horizontal_group_list.append(groove_group)
            start_index = next_start
        self.__render_horizontal_pattern()

    def __render_horizontal_pattern(self):
        """
        过滤并渲染横向花纹
        :return:
        """
        render_group_list = []
        for group in self.horizontal_group_list:
            # 组过滤
            if group.groove_start < self.image_start or group.groove_end > self.image_end:
                continue
            for groove in group.groove_group:
                # 花纹过滤
                if groove.bbox[1] < 0 or groove.bbox[1] + groove.bbox[3] >= IMAGE_SIZE:
                    continue
                for data in groove.groove_data:
                    # # 列链码过滤
                    if data.end >= IMAGE_SIZE or data.start < 0:
                        continue
                    if data.index < self.image_start or data.index > self.image_end:
                        continue
                    for h in range(int(data.start), int(data.end)):
                        self.image[h, data.index] = 255
                    groove.render_groove_data.append(data)

                groove.build_bbox(True)
                groove.build_segmentation()
                self.render_pattern_list.append(groove)
            render_group_list.append(group)
        self.horizontal_group_list = render_group_list

    def render_bbox(self):
        """
        渲染包围框
        :return:
        """
        for groove in self.render_pattern_list:
            bbox = groove.bbox
            x_start = int(bbox[0])
            x_end = int(bbox[0] + bbox[2])
            y_start = int(bbox[1])
            y_end = int(bbox[1] + bbox[3])
            y_end = min(y_end, IMAGE_SIZE - 1)
            color = 128
            # 左右边界
            for y in range(y_start, y_end):
                self.image[y, x_start] = color
                self.image[y, x_end] = color
            # 上下边界
            for x in range(x_start, x_end):
                self.image[y_start, x] = color
                self.image[y_end, x] = color

    def render_segmentation(self):
        """
        渲染轮廓点
        :return:
        """
        for groove in self.render_pattern_list:
            segment = groove.segmentation[0]
            all_points_num = len(segment)
            # print("all_points_num:", all_points_num)
            for index in range(all_points_num):
                if index >= all_points_num - 1:
                    continue
                # print(segment[index], segment[index + 1])
                if index % 2 == 0:
                    x = min(int(segment[index]), IMAGE_SIZE - 1)
                    y = min(int(segment[index + 1]), IMAGE_SIZE - 1)
                    self.image[y, x] = 128

    def save(self, path):
        cv2.imwrite("{}/{}".format(path, self.file_name), self.image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        print("{} build done".format(self.file_name))
