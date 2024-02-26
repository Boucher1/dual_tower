#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/17
# @Author  : hehl
# @Software: PyCharm
# @File    : produce_train_data.py
import csv
import json
data = open("classification_test.csv","w",encoding="utf-8",newline="")
data_w  = csv.writer(data)
with open("../../origin_dataset/WebQSP.test.json", "rb") as f:
    data = json.load(f)
    for i in data["Questions"]:
            query = i["ProcessedQuestion"]
            PotentialTopicEntityMention = i["Parses"][0]["PotentialTopicEntityMention"]
            InferentialChain = i["Parses"][0]["InferentialChain"]
            if InferentialChain is None:
                InferentialChain = []
            if len(InferentialChain):
                data_w.writerow([query.replace(PotentialTopicEntityMention,"<e>"),len(InferentialChain)])
