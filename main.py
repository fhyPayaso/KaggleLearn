import numpy as np
import cv2
from matplotlib import pyplot as plt

from TyreImage import *
from CocoEncoder import *


def datesets_builder(image_num, image_path, json_path):
    image_list = []
    for i in range(image_num):
        image = TyreImage(i + 1, 800)
        image.render_bbox()
        image.save(image_path)
        image_list.append(image)
    encoder = CocoEncoder()
    label_list = ['StraightLine', 'Polyline', 'Wavyline', 'HorizontalLine']
    encoder.parse_image_list(image_list, label_list)
    encoder.save_json(json_path)


if __name__ == '__main__':
    train_num = 20
    val_num = 10

    train_image_path = "./datasets/coco/train"
    train_json_path = "./datasets/coco/annotations/pattern_train.json"

    val_image_path = "./datasets/coco/val"
    val_json_path = "./datasets/coco/annotations/pattern_val.json"

    datesets_builder(train_num, train_image_path, train_json_path)
    datesets_builder(val_num, val_image_path, val_json_path)

# if __name__ == '__main__':
#     img = cv2.imread('./data/data2.jpeg', 0)
#     # img = cv2.imread('./data/tyre.png', 0)
#     # img = cv2.GaussianBlur(img, (3, 3), 0)
#
#     edges = cv2.Canny(img, 100, 200)
#
#     plt.subplot(1, 2, 1)
#     plt.imshow(img, cmap='gray')
#     plt.title('original')
#     plt.xticks([])
#     plt.yticks([])
#
#     plt.subplot(1, 2, 2)
#     plt.imshow(edges, cmap='gray')
#     plt.title('edge')
#     plt.xticks([])
#     plt.yticks([])
#
#     plt.show()
