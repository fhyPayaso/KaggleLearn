import json
import numpy as np
import pycocotools.mask as mask_util

class_mapping = ['StraightLine', 'Polyline', 'Wavyline',
                 'HorizontalStraightLine', 'HorizontalLeadLine', 'HorizontalArcLine']


class ResultColRange:
    def __init__(self, class_index, start, end):
        self.class_index = class_index
        self.start = int(start)
        self.end = int(end)
        self.inner_class_num = 0  # 当前范围内有多少种类
        self.instance_list = []
        self.uf_table = []

    def info(self):
        print("range start:{} ~ end:{}, instance_num:{}".format(
            self.start, self.end, len(self.instance_list)))

    def build_index(self):

        pass

    def dfs(self, step):
        # find root
        if self.uf_table[step] == step:
            return step
        else:
            self.uf_table[step] = self.dfs(self.uf_table[step])
        return self.uf_table[step]

    def union_found(self, x, y):
        root_x = self.dfs(x)
        root_y = self.dfs(y)
        if root_x != root_y:
            self.uf_table[root_y] = root_x

    def do_classify(self):
        if len(self.instance_list) <= 1:
            return

        for i in range(len(self.instance_list)):
            self.uf_table.append(i)

        for i in range(len(self.instance_list)):
            for j in range(i, len(self.instance_list)):
                pass

        # print(self.__cal_iou(self.instance_list[0], self.instance_list[1]))

    def __cal_iou(self, obj1, obj2):
        # make two obj in same height, base on bbox center height

        center_height1 = int((obj1['top'] + obj1['bottom']) / 2)
        center_height2 = int((obj2['top'] + obj2['bottom']) / 2)
        diff_height = center_height1 - center_height2

        bbox = obj2['bbox']
        intersection = 0
        for row in range(obj2['top'], obj2['bottom']):
            for col in range(obj2['left'], obj2['right']):
                if obj2['mask'][row, col] == 1:
                    n_row = row + diff_height
                    if obj1['mask'][n_row, col] == 1:
                        intersection += 1
        # print(intersection, obj1['area'], obj2['area'])
        return intersection * 1.0 / (obj1['area'] + obj2['area'] - intersection)


class ResultImage:
    def __init__(self, image_id):
        self.id = image_id
        self.instance_list = []  # 当前图片中的全部实体
        self.classify_list = []  # 当前包含的类标签
        self.range_list = {4: [], 5: [], 6: []}  # 当前范围共有多少列
        # 每个类对应一个实例数组
        for i in range(len(class_mapping)):
            class_instance_list = []
            self.classify_list.append(class_instance_list)

    def build_class_label(self):
        """
        先对一张图片内部的实例按照标签分类
        :return:
        """
        for instance in self.instance_list:
            category_id = instance['category_id']
            self.classify_list[category_id - 1].append(instance)
        print("<<<<============ Image {} : instance_num:{} ===============>>>>"
              .format(self.id, len(self.instance_list)))

    def build_range_list(self):
        """
        将每个横沟实例根据列的范围进行初步分类
        :return:
        """
        bbox_list = []  # 获得纵沟的全部范围
        for i in range(3):
            for instance in self.classify_list[i]:
                bbox_list.append(instance['bbox'])
        bbox_list.sort(key=lambda bbox: bbox[0])

        for class_index in range(3, 6):
            # init range list for pre class
            pre_center_line = 0
            for i in range(len(bbox_list)):
                bbox = bbox_list[i]
                center_line = bbox[0] + bbox[2] / 2
                if center_line - pre_center_line < 5:
                    continue
                col_range = ResultColRange(pre_center_line, center_line)
                self.range_list[class_index].append(col_range)
                pre_center_line = center_line
            self.range_list[class_index].append(ResultColRange(pre_center_line, 511))
            # map objects to range list in current class
            for instance in self.classify_list[class_index]:
                for index in range(len(self.range_list[class_index])):
                    left_range = self.range_list[class_index][index].start
                    right_range = self.range_list[class_index][index].end
                    if instance['left'] >= left_range and instance['right'] <= right_range:
                        self.range_list[class_index][index].instance_list.append(instance)
                        break

    def do_classify(self):
        for class_index in range(3, 6):
            for cur_range in self.range_list[class_index]:
                cur_range.union_found_classify()


# 对结果进行分类
class InstancesClassifier:
    def __init__(self, json_result_path, image_val_path):
        self.result_json_path = json_result_path
        self.image_val_path = image_val_path
        self.image_list = []

        with open(json_result_path, 'r', encoding='utf8')as fp:
            obj_list = json.load(fp)
            for obj in obj_list:
                # build image
                image_id = obj['image_id']
                if image_id > len(self.image_list):
                    self.image_list.append(ResultImage(image_id))
                # build object
                new_obj = self.parse_build_obj(obj)
                self.image_list[image_id - 1].instance_list.append(new_obj)

    def parse_build_obj(self, obj):
        # decode segmentation RLE data
        segmentation = obj['segmentation']
        mask = mask_util.decode(segmentation)
        obj['mask'] = mask
        # parse bbox
        bbox = obj['bbox']
        obj['left'] = int(bbox[0])
        obj['right'] = int(bbox[0] + bbox[2])
        obj['top'] = int(bbox[1])
        obj['bottom'] = int(bbox[1] + bbox[3])
        # sum area
        obj['area'] = 0
        for row in range(obj['top'], obj['bottom']):
            for col in range(obj['left'], obj['right']):
                obj['area'] += mask[row, col]
        return obj

    def run(self):
        for image in self.image_list:
            image.build_class_label()
            image.build_range_list()
            image.do_classify()


if __name__ == '__main__':
    # base_dir = '/Users/fanhongyu/Desktop/CGLAB/TyreSegment'
    base_dir = '/home/cglab/workspace/TyrePatternSegment'
    sub_dir = 'datasets/resdata/coco_instances_results.json'
    classifier = InstancesClassifier('{}/{}'.format(base_dir, sub_dir), "")
    classifier.run()
