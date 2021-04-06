import numpy as np


class RandomData:
    def __init__(self, range_left_col=30, range_right_col=60):
        """
        轮胎花纹沟数据随机类
        横沟宽度随机时，需要制定范围
        :param range_left_col:  随机宽度范围下限
        :param range_right_col: 随机宽度范围上限
        """
        self.height = 0  # 花纹沟高度
        self.width = 0  # 花纹沟宽度
        self.angle = 0  # 横向花纹沟倾斜角度(可正可负)
        self.margin = 0  # 两个花纹沟间距
        # -------------------------------- #
        self.arc_radius = 0  # 圆弧横沟半径
        self.arc_angle = 0  # 圆弧横沟角度
        self.arc_lr = 1  # 圆弧横沟横向方向(1: 从左到右，-1，从右到左)
        self.arc_tb = 1  # 圆弧横沟纵向方向(1: 从上到下，-1，从下到上)
        # 初始化基本信息
        self.random_for_horizontal_base(range_left_col, range_right_col)

    @staticmethod
    def angle_map(angle):
        return angle * 3.1415926 / 180

    def random_for_horizontal_base(self, range_left_col, range_right_col):
        self.height = np.random.randint(10, 30)
        self.width = np.random.randint(range_left_col, range_right_col)
        self.margin = np.random.randint(50, 100)

    def random_for_horizontal_straight(self):
        """
        构建直线横沟参数
        :return:
        """
        self.angle = 0

    def random_for_horizontal_lean(self):
        self.angle = np.random.randint(10, 40)
        if np.random.randint(0, 2) == 0:
            self.angle *= 1
        else:
            self.angle *= -1

    def random_for_horizontal_arc(self):
        """
        构建圆弧类型横向花纹沟的参数
        :return:
        """
        self.arc_radius = np.random.randint(150, 250)
        self.arc_angle = self.angle_map(np.random.randint(10, 30))
        if np.random.randint(0, 2) == 0:
            self.arc_lr = 1
        else:
            self.arc_lr = -1
        if np.random.randint(0, 2) == 0:
            self.arc_tb = 1
        else:
            self.arc_tb = -1
