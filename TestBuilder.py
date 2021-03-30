import numpy as np
import cv2
from CocoEncoder import *


class Pattern:
    def __init__(self):
        self.segmentation = []
        self.bbox = []
        self.area = 0
        self.type = 0


class MiniData:
    def __init__(self, width, height, index):
        self.width = width
        self.height = height
        self.id = index
        self.file_name = "tyre_{}.png".format(index)
        self.render_pattern_list = []
        self.image = np.zeros([width, height], np.uint8)

    def build_image(self):
        col_size = np.random.randint(200, 300)
        row_size = self.height - 20

        start_row = 10
        start_col = int((self.width / 2) - (col_size / 2))
        # start_col = 200

        # size = np.random.randint(100, 300)
        type = np.random.randint(3)

        type = 0

        pattern = Pattern()
        pattern.bbox = [start_col, start_row, col_size, row_size]
        seg = []

        for i in range(start_col, start_col + col_size):
            seg.append([start_row, i])
        for i in range(start_row, start_row + row_size):
            seg.append([i, start_col + col_size - 1])

        if type == 0:
            pattern.type = 1
            for col in range(start_col, start_col + col_size):
                for row in range(start_row, start_row + row_size):
                    pattern.area += 1
                    self.image[row, col] = 255

            for i in range(start_col + col_size, start_col, -1):
                seg.append([start_row + row_size - 1, i])
            for i in range(start_row + row_size, start_row, -1):
                seg.append([i, start_col])

        else:
            pattern.type = 2
            for col in range(start_col, start_col + col_size):
                diff_col = col - start_col
                cur_row_size = int(row_size / col_size * diff_col)
                for row in range(start_row, start_row + cur_row_size):
                    pattern.area += 1
                    self.image[row, col] = 255
            for col in range(start_col + col_size, start_col, -1):
                diff_col = start_col + col_size - col
                cur_row_diff = int(row_size / col_size * diff_col)
                seg.append([start_row + row_size - cur_row_diff, col])

        new_seg = []
        for pix in seg:
            new_seg.append([pix[1], pix[0]])
            # self.image[pix[0], pix[1]] = 128

        pattern.segmentation.append(np.array(new_seg).flatten())
        self.render_pattern_list.append(pattern)

    def save_image(self, path):
        cv2.imwrite("{}/{}".format(path, self.file_name), self.image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        print("{} build done".format(self.file_name))


def gen_json(image_list, json_path):
    encoder = CocoEncoder()
    # label_list = ['obj1', 'obj2']
    label_list = ['obj1']
    encoder.parse_image_list(image_list, label_list)
    encoder.save_json(json_path)


if __name__ == '__main__':

    base_path = "/home/cglab/workspace/AdelaiDet/datasets/coco/{}"

    image_list_train = []
    image_list_val = []

    for i in range(1, 11):
        data = MiniData(512, 512, i)
        data.build_image()
        data.save_image(base_path.format("train2017"))
        image_list_train.append(data)

        val_data = MiniData(512, 512, i)
        val_data.build_image()
        val_data.save_image(base_path.format("val2017"))
        image_list_val.append(val_data)

    gen_json(image_list_train, base_path.format("annotations/instances_train2017.json"))
    gen_json(image_list_val, base_path.format("annotations/instances_val2017.json"))
