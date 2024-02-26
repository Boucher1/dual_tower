#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/28
# @Author  : hehl
# @Software: PyCharm
# @File    : create_classfier_data.py
import json


w = open("../../bertorch_main/data/structrue_classfier/test_all_800.tsv", "w")
with open("compQ.test.json", "r", encoding="utf-8") as f:
    for i in json.load(f):
        question = i["question"].replace(".","").replace("?","").lower()
        w.write(question+"\t"+str(0)+"\n")
