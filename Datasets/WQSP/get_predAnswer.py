#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/6
# @Author  : hehl
# @Software: PyCharm
# @File    : get_predAnswer.py
import json

q = []
with open("q_true.txt","r",encoding="utf-8") as d:
    for i in d.readlines():
        q.append(i.strip())
print(len(q))
list_answer_dict = []
with open("WebQSP.test.json", "rb") as f:
    data = json.load(f)
    for i in data["Questions"]:
        query = i["ProcessedQuestion"]
        mention = i["Parses"][0]["PotentialTopicEntityMention"]
        if mention is None:
            mention = ""
        query_e = query.replace(mention, "<e>")
        id = i["QuestionId"]
        Answers_list = i["Parses"][0]["Answers"]
        ansall = []
        for i in Answers_list:
            ans = i["AnswerArgument"]
            ansall.append(ans)
        if query_e in q:
            # print(id)
            data = {"QuestionId":id,"Answers":ansall}
            # dict = json.dumps(data)
            # print(dict)
            list_answer_dict.append(data)
            # print(list_answer_dict)
with open("predAnser.json","w",encoding="utf-8") as w:
    json.dump(list_answer_dict,w,indent=4)