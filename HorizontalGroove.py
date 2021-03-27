from math import *
import numpy as np
import cv2
from VerticalGroove import *


# 横向花纹沟基类
class HorizontalGroove(Groove):
    """
    横向花纹主要类型分为 : 简单直线(包含倾斜角度), 简单曲线
    其中内部分为三种情况: 贯通类型，全封闭类型，半封闭类型(分左右)
    """

    def __init__(self, height, start_index, angle, margin, start, end):
        super(HorizontalGroove, self).__init__()
        self.height = height
        self.start_index = start_index  # 引导线起始点横坐标
        self.angle = angle * 3.1415 / 180  # 引导线与水平线的夹角
        self.margin = margin  # 两个横沟间距
        self.start = start  # 开始列
        self.end = end  # 结束列
        self.type = 0

    def build_bbox(self):
        top = np.iinfo(np.int).max
        bot = np.iinfo(np.int).min
        for groove in self.groove_data:
            top = min(top, groove.start)
            bot = max(bot, groove.end)
        self.bbox = [self.start, top, self.end - self.start, bot - top]

    def build_segmentation(self):
        top_points = []
        bot_points = []
        for data in self.render_groove_data:
            self.area += abs(data.end - data.start)
            if data.index % 5 == 0:  # 避免过度密集
                top_points.append([data.start, data.index])
                bot_points.append([data.end, data.index])
        start_col = self.groove_data[0]
        end_col = self.groove_data[-1]
        # 上边界
        top_points.reverse()
        # # 左边界
        # i = start_col.start
        # while i < start_col.end:
        #     top_points.append([i, start_col.index])
        #     i += 1
        # 下边界
        top_points.extend(bot_points)
        # 右边界
        # i = end_col.end
        # while i > end_col.start:
        #     top_points.append([i, end_col.index])
        #     i -= 1
        self.segmentation.append(np.array(top_points).flatten())


class HorizontalStraightLineGroove(HorizontalGroove):
    def __init__(self, height, start_index, angle, margin, start, end):
        super().__init__(height, start_index, angle, margin, start, end)
        self.type = 4

    def build_none_link(self):
        # 由左向右构建多个列链码
        cur_h = self.start_index
        for w in range(self.start, self.end):
            data = GrooveData(False, w,
                              cur_h - self.height / 2,
                              cur_h + self.height / 2)
            self.groove_data.append(data)
            cur_h = self.start_index + tan(self.angle) * (w - self.start)


# 从上至下的一组花纹
class HorizontalGrooveGroup:
    def __init__(self, height, width, margin, angle):
        self.width = width  # 横沟宽度(从左到右的距离)
        self.height = height  # 横沟高度(上下两点到中心引导线的距离)
        self.angle = angle  # 引导线与水平线的夹角
        self.margin = margin  # 两个横沟间距
        self.groove_group = []
        self.groove_start = 0
        self.groove_end = 0

    def build_groove_group(self, start, end):
        """
        构建一列的多个重复花纹(全包围)
        :param start: 区域开始列
        :param end: 区域结束列
        :return:
        """
        cur_h = self.margin + self.height / 2  # 开始高度
        self.groove_start = int((start + end) / 2 - self.width / 2)
        self.groove_end = int(self.groove_start + self.width)
        # 由上至下构建多个相同花纹
        while cur_h < 1000:
            # 构建花纹
            groove = HorizontalStraightLineGroove(
                self.height, cur_h,
                self.angle, self.margin,
                self.groove_start, self.groove_end
            )
            groove.build_none_link()
            groove.build_bbox()
            self.groove_group.append(groove)
            cur_h += self.margin + self.height
