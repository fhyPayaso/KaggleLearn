import json
import numpy as np

class_mapping = ['StraightLine', 'Polyline', 'Wavyline',
                 'HorizontalStraightLine', 'HorizontalLeadLine', 'HorizontalArcLine']


class ResultImage:
    def __init__(self, image_id):
        self.id = image_id
        self.instance_list = []  # 当前图片中的全部实体
        self.classify_list = []  # 当前包含的类
        for i in range(len(class_mapping)):
            class_instance_list = []
            self.classify_list.append(class_instance_list)

    def classify(self):
        for instance in self.instance_list:
            category_id = instance['category_id']
            self.classify_list[category_id - 1].append(instance)
        print("=================================================")
        print(self.id)
        for i in range(len(self.classify_list)):
            print(class_mapping[i])
            for instance in self.classify_list[i]:
                print(instance)


# 对结果进行分类
class InstancesClassifier:
    def __init__(self, json_result_path, image_val_path):
        self.result_json_path = json_result_path
        self.image_val_path = image_val_path
        json_res = json.load("/Users/fanhongyu/Desktop/CGLAB/TyreSegment/datasets/coco_instances_results.json")


if __name__ == '__main__':
    with open('/Users/fanhongyu/Desktop/CGLAB/TyreSegment/datasets/coco_instances_results.json', 'r',
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

