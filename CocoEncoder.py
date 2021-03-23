import argparse
import json
import matplotlib.pyplot as plt
import skimage.io as io
# import cv2
import numpy as np
import glob
import PIL.Image


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


class CocoEncoder:
    def __init__(self):
        self.images = []
        self.annotations = []
        self.categories = []
        self.coco_data = {}

    def parse_image_list(self, image_list, label_list):
        # 生成标签信息
        for label in label_list:
            self.categories.append(self.__parse_categories(label))
        # 对于每一个花纹，生成一组信息
        for image in image_list:
            self.images.append(self.__parse_image(image))
            self.annotations.extend(self.__parse_annotations(image))

        self.coco_data = {
            'images': self.images,
            'categories': self.categories,
            'annotations': self.annotations
        }

    def __parse_image(self, image):
        image = {
            "height": image.height,
            "width": image.width,
            "id": image.id,
            "file_name": image.file_name
        }
        return image

    def __parse_annotations(self, image):
        single_image_annotations = []
        for pattern in image.render_pattern_list:
            annotation = {
                "segmentation": pattern.segmentation,
                "iscrowd": 0,
                "image_id": image.id,
                "bbox": pattern.bbox,
                "area": pattern.area,
                "category_id": pattern.type,
                "id": len(single_image_annotations) + len(self.annotations) + 1
            }
            single_image_annotations.append(annotation)
        return single_image_annotations

    def __parse_categories(self, label):
        category = {
            'supercategory': 'Groove',
            'id': len(self.categories) + 1,
            'name': label
        }
        return category

    def save_json(self, path):
        # indent=4 更加美观显示
        json.dump(self.coco_data, open(path, 'w'), indent=4, cls=MyEncoder)
        print("json save done")
