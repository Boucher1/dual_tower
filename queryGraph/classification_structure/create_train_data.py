#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/21
# @Author  : hehl
# @Software: PyCharm
# @File    : create_train_data.py

# hop1 = ['ns?x']
# hop1_const = ['ns?x?x?sk0', 'ns?x?xns', 'ns?x?xns?x?sk0', 'ns?x?xns?xns', 'ns?x?x?sk0?x?sk1']
# hop2 = ['ns?y?y?x']
# hop2_const = ['ns?y?y?x?yns?x?sk0', 'ns?y?y?x?yns?yns?yns', 'ns?y?y?x?xns', 'ns?y?y?x?yns', 'ns?y?y?x?xns?yns',
#               'ns?y?y?x?xns?y?sk0', 'ns?y?y?x?y?sk0', 'ns?y?y?x?yns?y?sk0', 'ns?y?y?x?yns?yns', 'ns?y?y?x?yns?xns',
#               'ns?y?y?x?x?sk0', 'ns?y?y?x?yns?y?sk8', 'ns?y?y?x?yns?y?sk4']

stu_var = {0: ['ns?x'],
           1: ['ns?x?x?sk0', 'ns?x?xns', 'ns?x?xns?x?sk0', 'ns?x?xns?xns', 'ns?x?x?sk0?x?sk1'],
           2:['ns?y?y?x'],
           3:['ns?y?y?x?yns?x?sk0','ns?y?y?x?xns','ns?y?y?x?xns?yns','ns?y?y?x?xns?y?sk0','ns?y?y?x?yns?xns', 'ns?y?y?x?x?sk0'],#x
           4: ['ns?y?y?x?yns?x?sk0','ns?y?y?x?yns?yns?yns','ns?y?y?x?yns','ns?y?y?x?xns?yns','ns?y?y?x?xns?y?sk0',
               'ns?y?y?x?y?sk0', 'ns?y?y?x?yns?y?sk0','ns?y?y?x?yns?yns','ns?y?y?x?yns?xns', 'ns?y?y?x?yns?y?sk8', 'ns?y?y?x?yns?y?sk4'] #y
           }
import json
import csv
import random
stru = []

data = open("data/structure_5_classfier/WQ_test_all_2032.csv","w",encoding="utf-8",newline="")
data_w = csv.writer(data)

with open("../../Datasets/WQSP/WebQSP.test.partial.json", "rb") as f:
    data = json.load(f)
    num = 0
    for i in data["Questions"]:
            query = i["ProcessedQuestion"]
            e = i["Parses"][0]["PotentialTopicEntityMention"]
            sparql = i["Parses"][0]["Sparql"]
            if e is None:
                e = ""
            query_e = query.replace(e,"<e>")

            # if "#MANUAL" in sparql:
            #     data_w.writerow([query, "0"])
            #     num+= 1
            #     continue
            # structure = ""
            #
            # for line in sparql.split("\n"):
            #     if " ." in line and "EXIST" not in line:
            #         spo = line.split(" ",4)
            #
            #         structure=structure +spo[0].split(":")[0] + spo[2].split(":")[0]
            #
            # for i in range(len(stu_var)):
            #     if structure in stu_var.get(i):
            #         print(query,i)
            #         data_w.writerow([query,i])
            data_w.writerow([query, str(random.randint(0,4))])
print(num)




