from math import *
import numpy as np
import cv2
from VerticalGroove import *
from RandomData import *


# 横向花纹沟基类
class HorizontalGroove(Groove):
    """
    横向花纹主要类型分为 : 简单直线(包含倾斜角度), 简单曲线
    其中内部分为三种情况: 贯通类型，全封闭类型，半封闭类型(分左右)
    """

    def __init__(self, start_index, start, end, random_data):
        super(HorizontalGroove, self).__init__()
        self.random_data = random_data
        self.start_index = start_index  # 引导线起始点横坐标
        self.start = start  # 开始列
        self.end = end  # 结束列
        self.type = 0

    def build_bbox(self, is_render=False):
        top = np.iinfo(np.int).max
        bot = np.iinfo(np.int).min

        link_marks = self.groove_data
        if is_render:
            link_marks = self.render_groove_data

        for groove in link_marks:
            top = min(top, groove.start)
            bot = max(bot, groove.end)
        self.bbox = [self.start, top, self.end - self.start, bot - top]

    def build_segmentation(self):
        top_points = []
        bot_points = []
        for data in self.render_groove_data:
            self.area += abs(data.end - data.start)
            # if data.index % 10 == 0:  # 避免过度密集
            top_points.append([data.start, data.index])
            bot_points.append([data.end, data.index])
        start_col = self.groove_data[0]
        end_col = self.groove_data[-1]
        # 上边界
        top_points.reverse()
        # # 左边界
        i = start_col.start
        while i < start_col.end:
            top_points.append([i, start_col.index])
            i += 1
        # 下边界
        top_points.extend(bot_points)
        # 右边界
        i = end_col.end
        while i > end_col.start:
            top_points.append([i, end_col.index])
            i -= 1
        new_seg = []
        for pix in top_points:
            new_seg.append([pix[1], pix[0]])

        self.segmentation.append(np.array(new_seg).flatten())


# 直线横沟(不带角度)
class HorizontalStraightLineGroove(HorizontalGroove):
    def __init__(self, start_index, start, end, random_data):
        super().__init__(start_index, start, end, random_data)
        self.type = 4

    def build_none_link(self):
        # 由左向右构建多个列链码
        cur_h = self.start_index
        for w in range(self.start, self.end):
            data = GrooveData(False, w,
                              cur_h - self.random_data.height / 2,
                              cur_h + self.random_data.height / 2)
            self.groove_data.append(data)


# 斜线横沟(带角度)
class HorizontalLeanLineGroove(HorizontalGroove):
    def __init__(self, start_index, start, end, random_data):
        super().__init__(start_index, start, end, random_data)
        self.type = 5

    def build_none_link(self):
        # 由左向右构建多个列链码
        cur_h = self.start_index
        for w in range(self.start, self.end):
            data = GrooveData(False, w,
                              cur_h - self.random_data.height / 2,
                              cur_h + self.random_data.height / 2)
            self.groove_data.append(data)
            cur_h = self.start_index + tan(self.random_data.angle) * (w - self.start)


# 圆弧横沟
class HorizontalArcGroove(HorizontalGroove):
    def __init__(self, start_index, start, end, random_data):
        super().__init__(start_index, start, end, random_data)
        self.type = 6

    def build_none_link(self):
        # 由左向右构建多个列链码
        cur_h = self.start_index
        st = self.start
        en = self.end
        # 反向则调转两边
        if self.random_data.arc_lr == -1:
            st = self.end
            en = self.start
        # 圆弧对应的圆心点
        arc_center = [st, self.start_index + self.random_data.arc_radius * self.random_data.arc_tb]

        for w in range(st, en, self.random_data.arc_lr):
            data = GrooveData(False, w,
                              cur_h - self.random_data.height / 2,
                              cur_h + self.random_data.height / 2)
            val = pow(self.random_data.arc_radius, 2) - pow(w - arc_center[0], 2)
            if val >= 0:
                cur_h = arc_center[1] - sqrt(val) * self.random_data.arc_tb
                self.groove_data.append(data)
            else:
                break
        # 如果从右向左，需要倒置
        if self.random_data.arc_lr == -1:
            self.groove_data.reverse()


class HorizontalGrooveGroup:
    def __init__(self, start_col, end_col, groove_type, random_data):
        """
        从上到下的横沟花纹组
        :param start_col: 横沟组范围起始列
        :param end_col: 横沟组范围结束列
        :param groove_type: 花纹沟种类
        :param random_data: 随机数据
        """
        self.random_data = random_data
        self.groove_group = []
        self.groove_type = groove_type
        self.groove_start = int((start_col + end_col) / 2 -
                                self.random_data.width / 2)
        self.groove_end = int(self.groove_start + self.random_data.width)

        if self.groove_type == 4:
            self.random_data.random_for_horizontal_straight()
        elif self.groove_type == 5:
            self.random_data.random_for_horizontal_lean()
        elif self.groove_type == 6:
            self.random_data.random_for_horizontal_arc()

        self.build_groove_group()

    def build_groove_group(self):
        """
        构建一列的多个重复花纹(全包围)
        :return:
        """
        cur_h = self.random_data.margin + self.random_data.height / 2  # 开始高度
        # 由上至下构建多个相同花纹
        while cur_h < 512:
            # 构建花纹
            groove = None
            if self.groove_type == 4:
                groove = HorizontalStraightLineGroove(
                    cur_h, self.groove_start, self.groove_end, self.random_data)
            elif self.groove_type == 5:
                groove = HorizontalLeanLineGroove(
                    cur_h, self.groove_start, self.groove_end, self.random_data)
            elif self.groove_type == 6:
                groove = HorizontalArcGroove(
                    cur_h, self.groove_start, self.groove_end, self.random_data)

            if groove is not None:
                groove.build_none_link()
                groove.build_bbox()
                self.groove_group.append(groove)
            cur_h += self.random_data.margin + self.random_data.height
