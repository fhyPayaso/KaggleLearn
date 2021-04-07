import json
import numpy as np

class_mapping = ['StraightLine', 'Polyline', 'Wavyline',
                 'HorizontalStraightLine', 'HorizontalLeadLine', 'HorizontalArcLine']


class ResultColRange:
    def __init__(self, start, end):
        self.start = int(start)
        self.end = int(end)
        self.class_num = 0  # 当前范围内有多少种类
        self.instance_list = []
        self.class_data = {
            4: [], 5: [], 6: []
        }

    def mapping_to_class(self):
        for instance in self.instance_list:
            self.class_data[instance['category_id']].append(instance)

    def info(self):
        for i in range(3, 6):
            print("{}:{}".format(class_mapping[i], self.class_data[i + 1]))

        print("range start:{} ~ end:{}, instance_num:{}".format(
            self.start, self.end, len(self.instance_list)))

    def classify(self):
        self.k_means(self.class_data[4])
        self.k_means(self.class_data[5])
        self.k_means(self.class_data[6])

    def k_means(self, mini_instance_list):
        """
        对筛选后的列表内部进行聚类分析
        :param mini_instance_list:
        :return:
        """
        if len(mini_instance_list) <= 1:
            return

        for instance in mini_instance_list:
            segmentation = instance['segmentation']
            counts = segmentation['counts']
            bbox = instance['bbox']
            num = 0
            for char in counts:
                # if char
                num += ord(char)
            print(num, 512 * 512, int(bbox[2] * bbox[3]))


class ResultImage:
    def __init__(self, image_id):
        self.id = image_id
        self.instance_list = []  # 当前图片中的全部实体
        self.classify_list = []  # 当前包含的类标签
        self.range_list = []  # 当前范围共有多少列
        # 每个类对应一个实例数组
        for i in range(len(class_mapping)):
            class_instance_list = []
            self.classify_list.append(class_instance_list)

    def classify(self):
        """
        先对一张图片内部的实例按照标签分类
        :return:
        """
        for instance in self.instance_list:
            category_id = instance['category_id']
            self.classify_list[category_id - 1].append(instance)
        print("<<<<============ Image {} : instance_num:{} ===============>>>>"
              .format(self.id, len(self.instance_list)))
        tot_num = 0
        horizontal_num = 0
        vertical_num = 0
        for i in range(len(self.classify_list)):
            tot_num += len(self.classify_list[i])
            if i < 3:
                vertical_num += len(self.classify_list[i])
            else:
                horizontal_num += len(self.classify_list[i])
            # print("{} :{} ".format(class_mapping[i], len(self.classify_list[i])))
        print("tot_num:{} horizontal_num:{} vertical_num:{}".format(
            tot_num, horizontal_num, vertical_num))
        print("------------------")

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

        # for bbox in bbox_list:
        #     print(bbox)

        pre_center_line = 0
        for i in range(len(bbox_list)):
            bbox = bbox_list[i]
            center_line = bbox[0] + bbox[2] / 2
            if center_line - pre_center_line < 5:
                continue
            col_range = ResultColRange(pre_center_line, center_line)
            self.range_list.append(col_range)
            pre_center_line = center_line
        self.range_list.append(ResultColRange(pre_center_line, 511))

        # 将横沟实例分配到每个列中
        for i in range(3, 6):
            for instance in self.classify_list[i]:
                b_start = instance['bbox'][0]
                b_end = b_start + instance['bbox'][2]
                for index in range(len(self.range_list)):
                    if b_start >= self.range_list[index].start and b_end <= self.range_list[index].end:
                        self.range_list[index].instance_list.append(instance)
                        break

        all_num = 0
        for cur_range in self.range_list:
            cur_range.mapping_to_class()
            cur_range.info()
            cur_range.classify()
            all_num += len(cur_range.instance_list)
        print("all_num:{}".format(all_num))


# 对结果进行分类
class InstancesClassifier:
    def __init__(self, json_result_path, image_val_path):
        self.result_json_path = json_result_path
        self.image_val_path = image_val_path
        json_res = json.load("/Users/fanhongyu/Desktop/CGLAB/TyreSegment/datasets/coco_instances_results.json")


if __name__ == '__main__':
    with open('/Users/fanhongyu/Desktop/CGLAB/TyreSegment/datasets/resdata/coco_instances_results.json', 'r',
              encoding='utf8')as fp:
        json_data = json.load(fp)
        obj_list = json_data
        print("实例数量:", len(obj_list))
        image_list = []
        for objet in obj_list:
            id = objet['image_id']
            if id > len(image_list):
                image_list.append(ResultImage(id))
            image_list[id - 1].instance_list.append(objet)

        for image in image_list:
            image.classify()
            image.build_range_list()
