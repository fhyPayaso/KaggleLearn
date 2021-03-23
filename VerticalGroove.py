from dataclasses import dataclass
from math import *



@dataclass()
class GrooveData:
    is_vertical: bool
    index: int
    start: int
    end: int


# 横向花纹沟基类
class VerticalGroove:
    def __init__(self, width, height, center_index):
        """
        纵向花纹沟基类
        :param width: 花纹沟宽度
        :param height: 花纹沟纵向范围
        :param center_index: 花纹沟中间的位置
        """
        self.width = width
        self.height = height
        self.groove_data = []
        self.center_index = center_index

    def get_groove_data(self):
        return self.groove_data


# 直线类型纵沟
class VerticalStraightLineGroove(VerticalGroove):

    def __init__(self, width, height, center_index):
        super(VerticalStraightLineGroove, self).__init__(width, height, center_index)
        self.build_groove_data()

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
        self.center_index_list = []
        self.build_guide_line()
        self.build_groove_data()

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
        self.build_guide_line()
        self.build_groove_data()

    def build_guide_line(self):
        cur_height = 0
        self.center_index_list.append([cur_height, self.center_index])
        while cur_height < self.height:
            end_height = cur_height + self.segment_length
            # 生成单个片段
            cur_center_index = self.center_index_list[-1][1]
            for h in range(cur_height, end_height):
                # 将距离映射到一个周期内
                theta = 2 * 3.14 * (h - cur_height) / self.segment_length
                diff = self.omega * sin(theta)  # 正弦函数变化
                self.center_index_list.append([h, cur_center_index + diff])
            cur_height = end_height

    def build_groove_data(self):
        for pos in self.center_index_list:
            data = GrooveData(True, pos[0], pos[1] - self.width / 2, pos[1] + self.width / 2)
            self.groove_data.append(data)
