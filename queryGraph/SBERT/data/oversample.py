#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/16
# @Author  : hehl
# @Software: PyCharm
# @File    : oversample.py


import csv

with open('SBERT_CQ_train_NoCons.tsv', 'r') as f:
    lines = f.readlines()
#
# first_part = lines[:47884]
# second_part = lines[47884:]

# with open('CQ_train_NoCons.tsv', 'w') as f:
#     f.writelines(first_part)
#
# with open('../../../bertorch_main/data/score/CQ_val_NoCons.tsv', 'w') as f:
#     f.writelines(second_part)


data_info = {0: 0, 1: 0, 2: 0}
'''过采样数据'''
with open("SBERT_CQ_train_NoCons_oversampling.tsv", "w", encoding="utf-8", newline="") as d:
    with open("SBERT_CQ_train_NoCons.tsv", "r", encoding="utf-8") as f:
        for line in f.readlines():
            data = line.strip().split("\t")
            lable = data[3]
            # if str(data[3]) == "0.7": lable = "2"
            data_info[int(lable)] += 1
            if lable == "1":
                for i in range(36):
                    d.write(data[0] + "\t" + data[1] + "\t" + data[2] + "\t" + data[3] + "\n")
            elif lable == "2":
                for i in range(45):
                    d.write(data[0] + "\t" + data[1] + "\t" + data[2] + "\t" + data[3] + "\n")
            else:
                d.write(data[0] + "\t" + data[1] + "\t" + data[2] + "\t" + data[3] + "\n")
print(data_info)
data_info = {0: 0, 1: 0, 2: 0}
with open("SBERT_CQ_train_NoCons_oversampling.tsv", "r", encoding="utf-8") as f:
    for line in f.readlines():
        data = line.strip().split("\t")
        lable = str(data[3])
        if str(data[3]) == "0.7": lable = "2"
        data_info[int(lable)] += 1

print(data_info)

import random

# 读取txt文件内容
with open("SBERT_CQ_train_NoCons_oversampling.tsv", "r") as f:
    lines = f.readlines()
# 打乱行顺序
random.shuffle(lines)
# 将打乱后的内容写回文件
with open("SBERT_CQ_train_NoCons_oversamplingshuffle.tsv", "w") as f:
    f.writelines(lines)

data_info = {0: 0, 1: 0, 2: 0}

with open("SBERT_CQ_train_NoCons_oversamplingshuffle.tsv", "r",
          encoding="utf-8") as f:
    for line in f.readlines():
        data = line.strip().split("\t")
        lable = str(data[3])
        if str(data[3]) == "0.7": lable = "2"
        data_info[int(lable)] += 1

print(data_info)

############################################################################################################################################################

#
# data_info = {0: 0, 1: 0}
# '''过采样数据'''
# with open("SBERT_CQ_val_NoCons_oversampling.tsv","w",encoding="utf-8",newline="") as d:
#
#     with open("../../../bertorch_main/data/score/CQ_val_NoCons.tsv", "r", encoding="utf-8") as f:
#         for line in f.readlines():
#             data = line.strip().split("\t")
#             lable = data[3]
#             data_info[int(lable)] += 1
#             if lable == "1":
#                 for i in range(38):
#                     d.write(data[0]+"\t"+data[1]+"\t"+data[2]+"\t"+data[3]+"\n")
#             else:
#                 d.write(data[0]+"\t"+data[1]+"\t"+data[2]+"\t"+data[3]+"\n")
# print(data_info)
# data_info = {0: 0,  1: 0}
# with open("SBERT_CQ_val_NoCons_oversampling.tsv","r",encoding="utf-8") as f:
#     for line in f.readlines():
#         data = line.strip().split("\t")
#         lable = str(data[3])
#         data_info[int(lable)] += 1
#
# print(data_info)
#
# import random
#
# # 读取txt文件内容
# with open("SBERT_CQ_val_NoCons_oversampling.tsv", "r") as f:
#     lines = f.readlines()
# # 打乱行顺序
# random.shuffle(lines)
# # 将打乱后的内容写回文件
# with open("SBERT_CQ_val_NoCons_oversamplingshuffle.tsv", "w") as f:
#     f.writelines(lines)
#
#
# data_info = {0: 0, 1: 0}
#
# with open("SBERT_CQ_val_NoCons_oversamplingshuffle.tsv","r",encoding="utf-8") as f:
#     for line in f.readlines():
#         data = line.strip().split("\t")
#         lable = str(data[3])
#         data_info[int(lable)] += 1
#
# print(data_info)
#
