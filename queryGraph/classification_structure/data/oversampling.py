#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/23
# @Author  : hehl
# @Software: PyCharm
# @File    : oversampling.py
import csv

data_info = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
'''过采样数据'''
with open("C:/Users/hehl/Downloads/candidates/candgen_CompQ/stru_train_oversampling.tsv", "w", encoding="utf-8",
          newline="") as d:
    d_w = csv.writer(d)
    print(data_info)
    with open("C:/Users/hehl/Downloads/candidates/candgen_CompQ/stru_train.tsv", "r", encoding="utf-8") as f:
        for line in f.readlines():
            data = line.strip().split("\t")
            data_info[int(data[1])] += 1
            if data[1] == "1":
                for i in range(42):
                    d_w.writerow([data[0], data[1]])
            elif data[1] == "2":
                for i in range(2):
                    d_w.writerow([data[0], data[1]])
            elif data[1] == "3":
                for i in range(38):
                    d_w.writerow([data[0], data[1]])
            elif data[1] == "4":
                for i in range(12):
                    d_w.writerow([data[0], data[1]])
            else:
                for i in range(2):
                    d_w.writerow([data[0], data[1]])

with open("C:/Users/hehl/Downloads/candidates/candgen_CompQ/stru_train_oversampling.tsv", "r", encoding="utf-8") as f:
    for line in f.readlines():
        data = line.strip().split(",")
        data_info[int(data[1])] += 1

print(data_info)
#
# #
# '''数据集划分'''
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
#
# df = pd.read_csv("train.csv",header=0,names=["sentence","labels"])
# print(type(df["sentence"]))
#
# messages_train, messages_test, y_train, y_test = train_test_split(np.array(df["sentence"]), np.array(df["labels"]),test_size=0.25, random_state=1000)
#
# mess_train = pd.DataFrame(messages_train, columns=['message'])
# label_train = pd.DataFrame(y_train, columns=['label'])
# mess_test = pd.DataFrame(messages_test, columns=['message'])
# label_test = pd.DataFrame(y_test, columns=['label'])
#
#
# #"不能这样划分数据 会导致验证集里的数据训练集也有"
# train_data = 'train_data.csv'
# test_data = 'dev_data.csv'
# pd.concat([mess_train,label_train,], axis=1).to_csv(train_data, index=False, encoding='utf-8')
# pd.concat([mess_test,label_test], axis=1).to_csv(test_data, index=False, encoding='utf-8')
#
# # 加载数据，查看条数
# df_train = pd.read_csv(train_data, sep=',', encoding='utf-8')
# df_test = pd.read_csv(test_data, sep=',', encoding='utf-8')
# print('训练集大小',len(df_train),'测试集大小',len(df_test))


import pandas as pd
import os
from sklearn.utils import shuffle

data = pd.read_csv('C:/Users/hehl/Downloads/candidates/candgen_CompQ/stru_train_oversampling.tsv')
data = shuffle(data)  # 打乱
data.to_csv('C:/Users/hehl/Downloads/candidates/candgen_CompQ/stru_train_oversamplingshuffle.tsv', index=False,
            sep="\t")
