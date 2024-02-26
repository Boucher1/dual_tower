#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/27
# @Author  : hehl
# @Software: PyCharm
# @File    : CQ_create_trainData_allPath.py


# !/usr/bin/env python
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
sparqlQuery = SPARQLWrapper("http://localhost:8890/sparql")
sparqlQuery.setReturnFormat(JSON)

import eventlet  # 导入eventlet这个模块

eventlet.monkey_patch()  # 必须加这条代码


def replace_rdf(p):
    return p.replace("http://rdf.freebase.com/ns/", "")


from transformers import BertTokenizer
import torch
import torch.nn.functional as F

"两个文本比较相似度"
# tokenizer = BertTokenizer.from_pretrained('bert-base-cased')

import json
import csv
import time

'''标注训练集'''


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


def create_score_function(path):
    train = open(f"data/SBERT_CQ_{path}_NoCons.tsv", "w", encoding="utf-8", newline="")
    train_w = csv.writer(train, delimiter='\t')
    # train = open(f"data/SBERT_test_topK_NoCons.csv", "w", encoding="utf-8")
    # train_w = csv.writer(train, delimiter='\t')
    """只对主路径进行打分选择"""

    num = 1
    with open(f"../dual_encoder/CQ/compQ.{path}.json", "r", encoding="utf-8") as f:
        # with open(f"../../constraint/CQ/compQ.{path}.json", "r", encoding="utf-8") as f:
        for i in json.load(f):
            query = i["question"].replace("?", "").replace(".", "").lower()
            mention = i["mention"]
            if mention is None:
                mention = ""
            # query_e = query.replace(mention, "<e>")
            query_e = query
            TopicEntityMid = i["TopicEntityMid"]
            # if "Core_path" in i:  # 部分正确的查询图
            #     if "InferentialChain" in i:
            #         if i["InferentialChain"]:
            #             InferentialChain = i["InferentialChain"]
            #             """生成训练数据"""
            #             p_info = []
            #             for infer in InferentialChain:
            #                 p_info.append(infer)
            #                 train_w.writerow([num, query_e, infer, 0.7])  # 写入主路径的正样本 !
            #                 print(num, query_e, infer, 0.7)
            #                 num += 1
            #
            #             one_hop_path = get_1hop_p(TopicEntityMid)
            #             if one_hop_path:
            #                 for p in one_hop_path:
            #                     if p not in InferentialChain:  # 剔除正样本
            #                         train_w.writerow([num, query_e, p, 0])
            #                         print(num, query_e, p, 0)
            #                         num += 1
            #                 # 负样本
            #                 two_hop_path = get_2hop_p(TopicEntityMid, InferentialChain[0])
            #                 if two_hop_path:
            #                     for p2 in two_hop_path:
            #                         if p2 not in InferentialChain:  # 剔除正样本
            #                             train_w.writerow([num, query_e, p2, 0])
            #                             print(num, query_e, p2, 0)
            #                             num += 1
            # else: #完全正确的查询图
            if "InferentialChain" in i:
                if i["InferentialChain"]:
                    InferentialChain = i["InferentialChain"]

                    p_info = []
                    for infer in InferentialChain:
                        p_info.append(infer)
                        train_w.writerow([num, query_e, infer, 1])  # 写入主路径的正样本 !
                        print(num, query_e, infer, 1)
                        num += 1

                    one_hop_path = get_1hop_p(TopicEntityMid)
                    if one_hop_path:
                        for p in one_hop_path:
                            if p not in InferentialChain:  # 剔除正样本
                                train_w.writerow([num, query_e, p, 0])
                                print(num, query_e, p, 0)
                                num += 1
                        # 负样本
                        two_hop_path = get_2hop_p(TopicEntityMid, InferentialChain[0])
                        if two_hop_path:
                            for p2 in two_hop_path:
                                if p2 not in InferentialChain:  # 剔除正样本
                                    train_w.writerow([num, query_e, p2, 0])
                                    print(num, query_e, p2, 0)
                                    num += 1


if __name__ == '__main__':
    for path in ["test","train"]:
        print("生成", path, "路径中......")
        create_score_function(path)
    print("ok !")
    # create_score_function("1")
