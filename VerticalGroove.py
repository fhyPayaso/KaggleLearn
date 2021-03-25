from dataclasses import dataclass
from math import *
import numpy as np


@dataclass()
class GrooveData:
    is_vertical: bool
    index: int
    start: int
    end: int


class Groove:
    def __init__(self):
        # 0表示纵沟,1表示横沟
        self.type = 0
        self.groove_data = []  # 初始化生成的列链码
        self.render_groove_data = []  # 最终渲染生成的列链码
        self.bbox = []  # 元素包围框

        self.segmentation = []  # 轮廓像素点
        self.area = 0  # 花纹面积


# 纵向花纹沟基类
class VerticalGroove(Groove):
    def __init__(self, width, height, center_index):
        super(VerticalGroove, self).__init__()
        """
        纵向花纹沟基类
        :param width: 花纹沟宽度
        :param height: 花纹沟纵向范围
        :param center_index: 花纹沟中间的位置
        """
        self.width = width
        self.height = height
        self.center_index = center_index
        self.type = 0

    def get_groove_data(self):
        return self.groove_data

    def build_bbox(self):
        l = np.iinfo(np.int).max
        r = np.iinfo(np.int).min
        for groove in self.groove_data:
            l = min(l, groove.start)
            r = max(r, groove.end)
        self.bbox = [l, 0, r - l, self.height]

    def build_segmentation(self):
        left_points = []
        right_points = []
        for data in self.render_groove_data:
            if data.index < 0 or data.index >= self.height:
                continue
            self.area += abs(data.end - data.start)
            left_points.append([data.index, data.start])
            right_points.append([data.index, data.end])
        head_row = self.render_groove_data[0]
        end_row = self.render_groove_data[-1]
        # 下边界
        i = end_row.start
        while i < end_row.end:
            left_points.append([end_row.index, i])
            i += 1

        # 右边界
        right_points.reverse()
        left_points.extend(right_points)
        # 上边界
        i = head_row.end
        while i > head_row.start:
            left_points.append([head_row.index, i])
            i -= 1
        self.segmentation.append(np.array(left_points).flatten())

# 直线类型纵沟
class VerticalStraightLineGroove(VerticalGroove):

    def __init__(self, width, height, center_index):
        super(VerticalStraightLineGroove, self).__init__(width, height, center_index)
        self.type = 1
        self.build_groove_data()
        self.build_bbox()

    def build_groove_data(self):
        # 对于每个高度生成一个行链码
        for h in range(self.height):
            data = GrooveData(True, h,
                              self.center_index - self.width / 2,
                              self.center_index + self.width / 2)
            self.groove_data.append(data)


# 折线类型纵沟
class VerticalPolylineGroove(VerticalGroove):
    def __init__(self, width, height, center_index, angle, segment_length):
        """
        折线类型纵沟
        :param width: 花纹沟宽度
        :param height: 花纹沟纵向范围
        :param center_index: 花纹沟中间位置
        :param angle: 折线角度
        :param segment_length: 每个折长度
        """
        super(VerticalPolylineGroove, self).__init__(width, height, center_index)
        self.angle = angle * 3.1415 / 180
        self.segment_length = segment_length
        self.type = 2
        self.fix_center_init_index()
        self.center_index_list = []
        self.build_guide_line()
        self.build_groove_data()
        self.build_bbox()

    def fix_center_init_index(self):
        """
        修正初始化的中间点
        :return:
        """
        all_width = self.width + tan(self.angle) * self.segment_length
        self.center_index = self.center_index - all_width / 2 + self.width / 2

    def build_guide_line(self):
        cur_height = 0
        dir = 0  # 当前折线方向
        self.center_index_list.append([cur_height, self.center_index])
        while cur_height < self.height:
            end_height = cur_height + self.segment_length
            # 生成单个片段
            cur_center_index = self.center_index_list[-1][1]
            for h in range(cur_height, end_height):
                diff = (h - cur_height) * tan(self.angle)
                if dir == 0:
                    self.center_index_list.append([h, cur_center_index + diff])
                elif dir == 1:
                    self.center_index_list.append([h, cur_center_index - diff])
            dir = 0 if dir == 1 else 1
            cur_height = end_height

    def build_groove_data(self):
        for pos in self.center_index_list:
            data = GrooveData(True, pos[0], pos[1] - self.width / 2, pos[1] + self.width / 2)
            self.groove_data.append(data)


# 波浪线类型纵沟
class VerticalWavylineGroove(VerticalGroove):
    def __init__(self, width, height, center_index, omega, segment_length):
        """
        折线类型纵沟
        :param width: 花纹沟宽度
        :param height: 花纹沟纵向范围
        :param center_index: 花纹沟中间位置
        :param omega: 控制正弦函数的峰值
        :param segment_length: 每个周期长度
        """
        super(VerticalWavylineGroove, self).__init__(width, height, center_index)
        self.omega = omega
        self.segment_length = segment_length
        self.center_index_list = []
        self.type = 3
        self.build_guide_line()
        self.build_groove_data()
        self.build_bbox()

    def build_guide_line(self):
        cur_height = 0
        self.center_index_list.append([cur_height, self.center_index])
        while cur_height < self.height:
            end_height = cur_height + self.segment_length
            # 生成单个片段
            for h in range(cur_height, end_height):
                # 将距离映射到一个周期内
                theta = 2 * 3.14 * (h - cur_height) / self.segment_length
                diff = self.omega * sin(theta)  # 正弦函数变化
                self.center_index_list.append([h, self.center_index + diff])
            cur_height = end_height

    def build_groove_data(self):
        for pos in self.center_index_list:
            data = GrooveData(True, pos[0], pos[1] - self.width / 2, pos[1] + self.width / 2)
            self.groove_data.append(data)
