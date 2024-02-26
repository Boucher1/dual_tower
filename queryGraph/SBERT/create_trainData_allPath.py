#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/16
# @Author  : hehl
# @Software: PyCharm
# @File    : create_trainData_allPath.py


# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/15
# @Author  : hehl
# @Software: PyCharm
# @File    : create_trianData.py

#
"""生成训练样本
总共有数据：165822条，其中正样本：3044条，负样本：162778条
训练数据：116075条,其中正样本：2162条，负样本：113913条
测试数据：49747条,其中正样本：882条，负样本：48865条

负样本太多！ 删减掉一部分
"""
import nltk
import warnings

warnings.filterwarnings('ignore',
                        message="torch.distributed.reduce_op is deprecated, please use torch.distributed.ReduceOp instead")

from SPARQLWrapper import SPARQLWrapper, JSON

"""链接virtuoso 设置返回数据为json格式"""
sparqlQuery = SPARQLWrapper("http://172.23.253.79:8890/sparql")
sparqlQuery.setReturnFormat(JSON)

import eventlet  # 导入eventlet这个模块

eventlet.monkey_patch()  # 必须加这条代码


def replace_rdf(p):
    return p.replace("http://rdf.freebase.com/ns/", "")


from transformers import BertTokenizer
import torch
import torch.nn.functional as F

"两个文本比较相似度"
tokenizer = BertTokenizer.from_pretrained('bert-base-cased')

import json
import csv
import time

'''标注训练集'''


# def getConsPosPath(sparql):
#     cons = []
#     for line in sparql.split("\n"):
#         spo = line.split(" ", 4)
#         if spo[0].split(":")[0] == "?x" and spo[2].split(":")[0] == "ns":
#             cons.append(spo[1].split(":")[1])
#         if spo[0].split(":")[0] == "?y" and spo[2].split(":")[0] == "ns":
#             cons.append(spo[1].split(":")[1])
#         if "FILTER(NOT" in line:
#             cons.append(line.split(" ")[3].split(":")[1])
#     return cons
def get_1hop_p(entityID):
    if "m." in entityID or "g." in entityID:
        while True:
            try:
                query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  where{ ns:%s  ?p ?o}" % (entityID)
                print(query_txt)
                with eventlet.Timeout(60, False):
                    sparqlQuery.setQuery(query_txt)
                    results = sparqlQuery.query().convert()["results"]["bindings"]
                    data = []
                    if len(results):
                        for i in range(len(results)):
                            p = replace_rdf(results[i]["p"]["value"])
                            if p not in data:
                                data.append(p)
                            # 返回不重复的Path
                        # print(data)
                        return data
                    else:
                        return None
                return None
            except Exception as e:
                print("Exception:", e)
                time.sleep(5)
                continue  # 间隔5秒以便重试


def get_2hop_p(entityID, one_hop_path):
    if "m." in entityID or "g." in entityID:
        while True:
            try:
                query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  where{ ns:%s ns:%s ?x.?x ?p ?o}" % (
                    entityID, one_hop_path)
                print(query_txt)
                with eventlet.Timeout(60, False):
                    sparqlQuery.setQuery(query_txt)
                    results = sparqlQuery.query().convert()["results"]["bindings"]
                    data = []
                    if len(results):
                        for i in range(len(results)):
                            p = replace_rdf(results[i]["p"]["value"])
                            if p not in data:
                                data.append(p)
                        # 返回不重复的Path
                        # print(data)
                        return data
                    else:
                        return None
                return None
            except Exception as e:
                print("Exception:", e)
                time.sleep(5)
                continue  # 间隔5秒以便重试
def query_virtuoso_entityType(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select DISTINCT ?n where{ ns:%s  ns:common.topic.notable_types ?x.?x ns:type.object.name  ?n}" % (
            entityID)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                if len(results):
                    return results[0]["n"]["value"].replace("@en", "").replace("\"", "")
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue

def create_score_function(path):
    train = open(f"my_data/SBERT_{path}_NoCons_nomask_type_allpath.csv", "w", encoding="utf-8", newline="")
    train_w = csv.writer(train, delimiter='\t')
    # train = open(f"data/SBERT_test_topK_NoCons.csv", "w", encoding="utf-8")
    # train_w = csv.writer(train, delimiter='\t')
    """只对主路径进行打分选择"""

    num = 1
    K = 5  # top_k 负样本

    with open(f"../../Datasets/WQSP/WebQSP.{path}.json", "r", encoding="utf-8") as f:
        # with open(f"../../Datasets/WQSP/test.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for i in data["Questions"]:
            """获取基本信息"""
            query = i["ProcessedQuestion"]
            mention = i["Parses"][0]["PotentialTopicEntityMention"]
            if mention is None:
                mention = ""
            # query_e = query.replace(mention, "<e>")
            query_e = query
            TopicEntityMid = i["Parses"][0]["TopicEntityMid"]
            InferentialChain = i["Parses"][0]["InferentialChain"]            # 没有answer就跳过
            try:
                AnswerEntityMid = i["Parses"][0]["Answers"][0]["AnswerArgument"]
            except Exception as e:
                print(e)
                continue

            """生成训练数据"""
            # p_info = []
            if InferentialChain is not None:
                # 主题实体类型
                top_e_typename = query_virtuoso_entityType(TopicEntityMid)
                # 答案实体类型
                answer_typename = query_virtuoso_entityType(AnswerEntityMid)
                # 要是查不到类型就跳过
                if top_e_typename is None or answer_typename is None:
                    continue
                query_e = query_e + ' [unused0] ' + answer_typename
                core_path_pos = InferentialChain[0] + ' [unused0] ' + top_e_typename
                # p_info.append(InferentialChain[0])
                train_w.writerow([num, query_e, core_path_pos, 1])  # 写入主路径的正样本
                print(num, query_e, core_path_pos, 1)
                num += 1

                one_hop_path = get_1hop_p(TopicEntityMid)
                if one_hop_path:
                    for p in one_hop_path:
                        if p not in InferentialChain:  # 剔除正样本
                            core_path_neg = p + ' [unused0] ' + top_e_typename
                            train_w.writerow([num, query_e, core_path_neg, 0])
                            print(num, query_e, core_path_neg, 0)
                            num += 1
                if len(InferentialChain) == 2:
                    core_path_pos = InferentialChain[1] + ' [unused0] ' + top_e_typename
                    train_w.writerow([num, query_e, core_path_pos, 1])  # 写入主路径的正样本
                    print(num, query_e, core_path_pos, 1)
                    num += 1
                    two_hop_path = get_2hop_p(TopicEntityMid, InferentialChain[0])
                    if two_hop_path:
                        for p2 in two_hop_path:
                            if p2 not in InferentialChain:  # 剔除正样本
                                core_path_neg = p2 + ' [unused0] ' + top_e_typename
                                train_w.writerow([num, query_e, core_path_neg, 0])
                                print(num, query_e, core_path_neg, 0)
                                num += 1


if __name__ == '__main__':
    for path in ["test"]:
        print("生成", path, "路径中......")
        create_score_function(path)
    print("ok !")
    # create_score_function("1")

