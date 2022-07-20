# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
from os import getcwd
import random
import shutil

classes = ["phone", "person", "pad", "book"]  # 改成自己的类别   pad:2 ,person:1,book:3,phone:0(规律，这里的对应序号就是类别在这里的书写顺序)

def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_annotation(img_id, anno_dir=None, labels_dir=None):
    in_file = open(os.path.join(anno_dir, r'%s.xml' % img_id), encoding='UTF-8')
    out_file = open(os.path.join(labels_dir, r'%s.txt' % img_id), 'w')

    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):

        # Warning, 标注文件 .xml 的<object>没有<difficult>的标签. difficult 表明这个待检测目标很难识别
        if obj.find('difficult'):
            difficult = int(obj.find('difficult').text)
        else:
            difficult = 0
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xml_box = obj.find('bndbox')
        b = (float(xml_box.find('xmin').text),
             float(xml_box.find('xmax').text),
             float(xml_box.find('ymin').text),
             float(xml_box.find('ymax').text))
        b1, b2, b3, b4 = b

        # 标注越界修正
        b2 = w if b2 > w else b2
        b4 = h if b4 > h else b4

        b = (b1, b2, b3, b4)
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


def split_train_test_val(anno_dir=None, out_dir=None):
    if anno_dir is None or out_dir is None:
        raise ValueError("path error")

    trainval_percent = 1.0
    train_percent = 0.9

    xml_file_path = anno_dir
    txt_save_path = out_dir
    total_xml = os.listdir(xml_file_path)


    num = len(total_xml)
    list_index = range(num)
    tv = int(num * trainval_percent)
    tr = int(tv * train_percent)
    trainval = random.sample(list_index, tv)
    train = random.sample(trainval, tr)

    file_trainval = open(txt_save_path + '\\trainval.txt', 'w')
    file_test = open(txt_save_path + '\\test.txt', 'w')
    file_train = open(txt_save_path + '\\train.txt', 'w')
    file_val = open(txt_save_path + '\\val.txt', 'w')

    for i in list_index:
        name = total_xml[i][:-4] + '\n'
        if i in trainval:
            file_trainval.write(name)
            if i in train:
                file_train.write(name)
            else:
                file_val.write(name)
        else:
            file_test.write(name)

    file_trainval.close()
    file_train.close()
    file_val.close()
    file_test.close()


def check_dir(_dir=None):
    if not os.path.exists(_dir):
        os.makedirs(_dir)


ROOT = os.getcwd()
def run(remove_temp=True):
    """
    convert pascal VOC to yolov5 coco formation
    preparing:
        - Annotations *.xml  # labeled dir
        - images *.jpg      # raw images dir

    the script will generate one folder and train/test/val.txt
        - labels *.txt  # labeled dir
        - train.txt
        - test.txt
        - val.txt

    :param remove_temp: is remove temp files
    :return:
    """
    anno_dir = os.path.join(ROOT, "Annotations")
    images_dir = os.path.join(ROOT, "images")
    out_dir = os.path.join(ROOT, "./")
    temp_dir = os.path.join(ROOT, "temp")
    labels_dir = os.path.join(ROOT, "labels")
    check_dir(temp_dir)
    check_dir(labels_dir)

    split_train_test_val(anno_dir, temp_dir)

    dataTypes = ['train', 'val', 'test']
    for data_type in dataTypes:
        image_ids = open(os.path.join(temp_dir, r'%s.txt' % data_type)).read().strip().split()
        data_type_file = open(os.path.join(out_dir, r'%s.txt' % data_type), 'w')

        for image_id in image_ids:
            # image path
            data_type_file.write(os.path.join(images_dir, '%s.jpg\n' % image_id))
            convert_annotation(image_id, anno_dir=anno_dir, labels_dir=labels_dir)
        data_type_file.close()

    # delete temp folder
    if remove_temp:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("convert . ")
    run()
    print("end . ")
