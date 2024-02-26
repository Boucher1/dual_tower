#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/17
# @Author  : hehl
# @Software: PyCharm
# @File    : classification.py


import pandas as pd
from sklearn.neural_network import MLPRegressor
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report,f1_score,accuracy_score
import sklearn
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
# 二分类，逻辑回归 癌症预测（根据细胞的属性特征）

# 构造列标签名字
# column_names = ['query', 'Class']
#
# # 读取数据  (如果不指定标签名，会默认把第一行数据当成标签名)
# data_train = pd.read_csv(
#     "classification_train.csv",
#     names=column_names)
# data_test = pd.read_csv(
#     "classification_test.csv",
#     names=column_names)
#
# print(type(data_test))
# vectorizer = TfidfVectorizer()
# X_train = vectorizer.fit_transform(data_train["query"])
# X_test = vectorizer.transform(data_test["query"])
#
#
#
# # 逻辑回归预测
# lg = LogisticRegression(C=1.0)  # 默认使用L2正则化避免过拟合，C=1.0表示正则力度(超参数，可以调参调优)
# lg.fit(X_train, data_train["Class"])
#
# # 回归系数
# print(lg.coef_)  # [[1.12796779  0.28741414  0.66944043 ...]]
#
# # 进行预测
# y_predict = lg.predict(X_test)
# print(y_predict)
#
# print("准确率：", lg.score(X_test, data_test["Class"]))  # 0.964912280702
#
# print("召回率：", classification_report(data_test["Class"].astype(str), y_predict.astype(str), labels=[1, 2], target_names=["一跳", "二跳"]))

'''
逻辑回归
准确率： 0.8901769371568029
召回率：               precision    recall  f1-score   support

          一跳       0.89      0.95      0.92      1038
          二跳       0.90      0.79      0.84       601

   micro avg       0.89      0.89      0.89      1639
   macro avg       0.89      0.87      0.88      1639
weighted avg       0.89      0.89      0.89      1639
'''



column_names = ['query', 'Class']

# 读取数据  (如果不指定标签名，会默认把第一行数据当成标签名)
data_train = pd.read_csv(
    "../classification_structure/data/pathData/train_textcnn.csv",
    names=column_names)
data_test = pd.read_csv(
    "../classification_structure/data/pathData/test_textcnn.csv",
    names=column_names)

# print(type(data_test))
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform(data_train["query"])
# print(X_train[0])
X_test = vectorizer.transform(data_test["query"])

# 有时必须要将标签转为数值
from sklearn.preprocessing import LabelEncoder
class_le = LabelEncoder()
y_train_n = class_le.fit_transform(data_train["Class"])
y_test_n = class_le.fit_transform(data_test["Class"])


from sklearn.model_selection import train_test_split,cross_val_score

# 逻辑回归预测
# lg = LogisticRegression(C=1.0)  # 默认使用L2正则化避免过拟合，C=1.0表示正则力度(超参数，可以调参调优)
# lg.fit(X_train, data_train["Class"])
#
# lg = sklearn.svm.SVC(C=1.0, kernel='linear', degree=3,
# 					coef0=0.0, shrinking=True, probability=False, tol=0.001,
# 					cache_size=200, class_weight=None, verbose=False, max_iter=-1,
# 					decision_function_shape="ovr", random_state=None)
#
# lg.fit(X_train, data_train["Class"])
# 回归系数
# print(lg.coef_)  # [[1.12796779  0.28741414  0.66944043 ...]]

# 进行预测
# y_predict = lg.predict(X_test)
#
#


# print("召回率：", classification_report(data_test["Class"].astype(str), y_predict.astype(str), labels=[0,1,2,3], target_names=["一跳","一跳带约束", "二跳","二跳带约束"]))
# print(y_predict)
# print(type(data_test["Class"]))
# print(f1_score(y_predict, data_test["Class"][1]))
# print(accuracy_score(y_predict, data_test["Class"][1]))



model = MLPRegressor(hidden_layer_sizes=(100, 100), activation='relu', solver='adam', max_iter=500)

# 拟合模型
model.fit(X_train, data_train["Class"])

# 预测测试集上的结果
predictions = model.predict(X_test)

print(predictions)
