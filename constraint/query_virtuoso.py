#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/27
# @Author  : hehl
# @Software: PyCharm
# @File    : query_virtuoso.py
import nltk
import warnings

warnings.filterwarnings('ignore',
                        message="torch.distributed.reduce_op is deprecated, please use torch.distributed.ReduceOp instead")

from SPARQLWrapper import SPARQLWrapper, JSON
from sentence_transformers import SentenceTransformer,util
import eventlet  # 导入eventlet这个模块

import re

"""链接virtuoso 设置返回数据为json格式"""
# sparqlQuery = SPARQLWrapper("http://43.142.132.166:8890/sparql")
# model_path = 'D:/workspace/pythonProject/complexQA/dyq_complexQA/queryGraph/SBERT/data/preTrain'

sparqlQuery = SPARQLWrapper("http://localhost:8890/sparql")
# model_path = "../SBERT/data/preTrainall"
model_path = "../SBERT/data/CQpreTrainall"

sparqlQuery.setReturnFormat(JSON)

eventlet.monkey_patch()  # 必须加这条代码

import time

"""微调bert  计算相似度"""


model = SentenceTransformer(model_path)
print(model)

def sbert_score(s1, s2):
    embedding1 = model.encode(s1, convert_to_tensor=True)
    embedding2 = model.encode(s2, convert_to_tensor=True)

    similarity = util.cos_sim(embedding1, embedding2)

    vecdict = dict(zip(s2, similarity.cpu().numpy().tolist()[0]))
    # vecdict = dict(zip(s2, similarity.numpy().tolist()[0]))

    return sorted(vecdict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)





def replace_rdf(p):
    return p.replace("http://rdf.freebase.com/ns/", "")


def is_query_anser(entityID, queryGraph):
    if queryGraph.count("{") == queryGraph.count("}"):
        queryGraph = queryGraph + "}"
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> SELECT DISTINCT  ?x WHERE { FILTER (?x != ns:" + entityID + ") ns:" + entityID + " " + queryGraph
    #print(sparql)
    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            if len(results):
                return True
            return False
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue
    return False


def get_1hop_p(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select DISTINCT ?p  where{ ns:%s  ?p ?o}" % (entityID)
        #print(query_txt)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                if len(results):
                    for i in range(len(results)):
                        temp = replace_rdf(results[i]["p"]["value"])
                        if temp not in data:
                            data.append(temp)
                    # 返回不重复的Path
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


# 查找问题中的年份约束
def find_year(text):
    pattern = r'\b\d{4}\b'  # 匹配四位数的数字
    year_list = []
    for match in re.finditer(pattern, text):
        year = int(match.group())  # 遍历匹配结果，转换成整数后添加到列表中
        if year >= 1000 and year <= 9999:  # 判断是否为年份
            year_list.append(year)
    return year_list


# 查询一跳 from to的约束
def query_1hop_p_from_to(entityID, one_hop_path, yearData):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/>  SELECT DISTINCT ?p ?o  WHERE { ns:%s ns:%s ?y . ?y ?p ?o. FILTER( CONTAINS(STR(?p), \".from\") || CONTAINS(STR(?p), \".to\") )}" % (
        entityID, one_hop_path)  # 仅仅查找出包含 from 或者t o的路径
    #print(sparql)

    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]

            from_path = ""
            to_path = ""
            if len(results):
                for i in range(len(results)):
                    # 是否考虑多个from to的路径？
                    p = replace_rdf(results[i]["p"]["value"])
                    o = replace_rdf(results[i]["o"]["value"])
                    if str(yearData) in o and "from" in p:
                        from_path = p
                    if str(yearData) in o and "to" in p:
                        to_path = p
                if from_path and to_path:
                    if to_path.split(".")[1] == from_path.split(".")[1] and to_path.split(".")[0] == \
                            from_path.split(".")[0]:
                        return from_path, to_path
                return None, None
            else:
                return None, None
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue


def query_order_asc_1hop(entityID, one_hop_path):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  ?n where{ ns:%s  ns:%s ?x. ?x  ?p ?n.FILTER( CONTAINS(STR(?p), \".from\") || CONTAINS(STR(?p), \"_date\") )}" % (
        entityID, one_hop_path)
    #print(sparql)

    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    p = replace_rdf(results[i]["p"]["value"])
                    if p not in data and find_year(results[i]["n"]["value"]):  # 且n有数字 年份
                        data.append(p)
                return data
            else:
                return None
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue


def query_order_desc_1hop(entityID, one_hop_path):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  ?n where{ ns:%s  ns:%s ?x. ?x  ?p ?n.FILTER( CONTAINS(STR(?p), \".to\") || CONTAINS(STR(?p), \"_date\") )}" % (
        entityID, one_hop_path)
    print("------------------", sparql)

    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    p = replace_rdf(results[i]["p"]["value"])
                    if p not in data and find_year(results[i]["n"]["value"]):  # 且n有数字 年份
                        if "to" in p.split(".")[2] or "_date" in p.split(".")[2]:
                            data.append(p)
                print(data)
                return data
            else:
                return None
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue


def query_order_asc_2hop(entityID, one_hop_path, two_hop_path):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  ?n where{ ns:%s  ns:%s ?y. ?y ns:%s ?x.?y ?p ?n.FILTER( CONTAINS(STR(?p), \".from\") || CONTAINS(STR(?p), \"date\") )}" % (
        entityID, one_hop_path, two_hop_path)
    #print(sparql)

    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    p = replace_rdf(results[i]["p"]["value"])
                    if p not in data and find_year(results[i]["n"]["value"]):  # 且n有数字 年份
                        data.append(p)
                return data
            else:
                return None
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue


def query_order_desc_2hop(entityID, one_hop_path, two_hop_path):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  ?n where{ ns:%s  ns:%s ?y. ?y ns:%s ?x.?y ?p ?n.FILTER( CONTAINS(STR(?p), \".to\") || CONTAINS(STR(?p), \"_date\") )}" % (
        entityID, one_hop_path, two_hop_path)
    #print(sparql)

    while True:
        try:
            sparqlQuery.setQuery(sparql)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    p = replace_rdf(results[i]["p"]["value"])
                    if p not in data and find_year(results[i]["n"]["value"]):  # 且n有数字 年份
                        data.append(p)
                return data
            else:
                return None
        except Exception as e:
            print("发生错误:", e)
            time.sleep(5)
            continue


def query_2hop_p_from_to(entityID, one_hop_path, two_hop_path, yearData):
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/>  SELECT DISTINCT ?p ?o  WHERE { ns:%s ns:%s ?y . ?y ns:%s ?x. ?y ?p ?o. FILTER( CONTAINS(STR(?p), \".from\") || CONTAINS(STR(?p), \".to\") )}" % (
        entityID, one_hop_path, two_hop_path)  # 仅仅查找出包含 from 或者t o的路径
    #print(sparql)
    with eventlet.Timeout(60, False):
        while True:
            try:
                sparqlQuery.setQuery(sparql)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                # print(results)
                from_path = ""
                to_path = ""
                if len(results):
                    for i in range(len(results)):
                        # 是否考虑多个from to的路径？
                        p = replace_rdf(results[i]["p"]["value"])
                        o = replace_rdf(results[i]["o"]["value"])
                        if str(yearData) in o and "from" in p:
                            from_path = p
                        if str(yearData) in o and "to" in p:
                            to_path = p
                    if from_path and to_path:
                        if to_path.split(".")[1] == from_path.split(".")[1] and to_path.split(".")[0] == \
                                from_path.split(".")[0]:
                            return from_path, to_path
                    return None, None
                else:
                    return None, None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue
    return None,None

# 将查出的from 和 to 配对 对于两跳均是加在y上的
def get_1hop_p_o_name(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p ?o ?n where{ ns:%s  ?p ?o.?o ns:type.object.name ?n}" % (
            entityID)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                if len(results):
                    for i in range(len(results)):
                        po = [replace_rdf(results[i]["p"]["value"]), replace_rdf(results[i]["o"]["value"]),
                              replace_rdf(results[i]["n"]["value"])]
                        if po not in data:
                            data.append(po)
                    # 返回不重复的Path
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


def get_1hop_o(entityID, p):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select DISTINCT ?o  where{ ns:%s  ns:%s ?o}" % (entityID, p)
        with eventlet.Timeout(60, False):
            while True:
                try:
                    sparqlQuery.setQuery(query_txt)
                    results = sparqlQuery.query().convert()["results"]["bindings"]
                    data = []
                    if len(results):
                        for i in range(len(results)):
                            temp = replace_rdf(results[i]["o"]["value"])
                            if temp not in data:
                                data.append(temp)
                        # 返回不重复的Path
                        return data
                    else:
                        return None
                except Exception as e:
                    print("发生错误:", e)
                    time.sleep(5)
                    continue
    return None


# 根据id和path 获取第二跳的路径
def from_id_path_get_2hop_po(entityID, one_hop_path):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select DISTINCT ?q where{ ns:%s ns:%s ?y.?y ?q ?x}" % (
            entityID, one_hop_path)
        #print(query_txt)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                # 选择分数较高和top-k个关系
                if len(results):
                    for i in range(len(results)):
                        temp = replace_rdf(results[i]["q"]["value"])
                        if temp not in data:
                            data.append(temp)
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


# 生成n-gram list
def create_ngram_list(input):
    input_list = input.lower().split(" ")
    ngram_list = []
    for num in range(len(input_list) + 1, -1, -1):
        for tmp in zip(*[input_list[i:] for i in range(num)]):
            tmp = " ".join(tmp)
            ngram_list.append(tmp)
    return ngram_list


def is_substring(n, q):
    n_list = n.lower().split("/")  # College/University
    for ns in n_list:
        if ns in q.lower():
            return True
    return False
    # q_list = q.split()
    # n_list = create_ngram_list(n)
    # for w_n in n_list:
    #         if w_n in q_list:
    #             return True
    # return False


def from_id_path_get_2hop_po_oName(question, entityID, one_hop_path):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?q  ?x ?n  where{ ns:%s ns:%s ?y. ?y ?q ?x.  ?x ns:type.object.name ?n}" % (
            entityID, one_hop_path)
        #print(query_txt)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                sentences = []
                if len(results):
                    for i in range(len(results)):
                        name = results[i]["n"]["value"].replace("@en", "")
                        sentences.append(name)
                        is_sub = is_substring(name, question)
                        if is_sub is True:
                            cons_path = replace_rdf(results[i]["q"]["value"])
                            id = replace_rdf(results[i]["x"]["value"])
                            if [cons_path, id, name] not in data:
                                data.append([cons_path, id, name])
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


def from_id_path_get_3hop_po_oName_x(question, entityID, one_hop_path, two_hop_path):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?q  ?x ?n  where{ ns:%s ns:%s ?a. ?a ns:%s ?y. ?y ?q ?x.  ?x ns:type.object.name ?n}" % (
            entityID, one_hop_path, two_hop_path)
        #print(query_txt)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                sentences = []
                if len(results):
                    for i in range(len(results)):
                        name = results[i]["n"]["value"].replace("@en", "").replace("\"", "")
                        sentences.append(name)
                        is_sub = is_substring(name, question)
                        if is_sub is True:
                            cons_path = replace_rdf(results[i]["q"]["value"])
                            id = replace_rdf(results[i]["x"]["value"])
                            if [cons_path, id, name] not in data:
                                data.append([cons_path, id, name])
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


def from_id_path_get_3hop_po_oName_y(question, entityID, one_hop_path, two_hop_path):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?q  ?x ?n  where{ ns:%s ns:%s ?a. ?a ns:%s ?y. ?a ?q ?x.  ?x ns:type.object.name ?n}" % (
            entityID, one_hop_path, two_hop_path)
        #print(query_txt)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                sentences = []

                if len(results):
                    for i in range(len(results)):
                        name = results[i]["n"]["value"].replace("@en", "").replace("\"", "")
                        sentences.append(name)
                        is_sub = is_substring(name, question)
                        if is_sub is True:
                            cons_path = replace_rdf(results[i]["q"]["value"])
                            id = replace_rdf(results[i]["x"]["value"])
                            if [cons_path, id, name] not in data:
                                data.append([cons_path, id, name])
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


def from_id_to_topK_path(query_e, entityId, k, threshold):
    result = get_1hop_p(entityId)  # 已知id获取路径
    candidate_path = []
    if result:
        candidate_path = sbert_score(query_e, result)
        # print(candidate_path) #[('location.country.languages_spoken', 0.8907366991043091), ('location.country.official_language', 0.7186728715896606)]
    path_score = []
    # print(min(k, len(candidate_path)))
    if candidate_path:
        for i in range(min(k, len(candidate_path))):
            # if i == 0:
            path_score.append(candidate_path[i])
            # elif candidate_path[i][1] > threshold:  # 阈值！！！
            #     path_score.append(candidate_path[i])
    return path_score


# 获取两条的top-k个路径
def from_id_to_topK_2path(query_e, entityId, one_hop_rel, k, threshold):
    result = from_id_path_get_2hop_po(entityId, one_hop_rel)  # 已知id获取路径
    candidate_path = []
    if result:
        candidate_path = sbert_score(query_e, result)
        # print(candidate_path) #[('location.country.languages_spoken', 0.8907366991043091), ('location.country.official_language', 0.7186728715896606)]
    path_score = []
    if candidate_path:
        for i in range(min(k, len(candidate_path))):
            # if i == 0:
            path_score.append(candidate_path[i])
            # elif candidate_path[i][1] > threshold:  # 阈值！！！
                # path_score.append(candidate_path[i])
    return path_score


def getConsPosPath(InferentialChain, sparql):
    x_cons = []
    y_cons = []
    for line in sparql.split("\n"):
        spo = line.split(" ", 4)
        if spo[0].split(":")[0] == "?x" and spo[2].split(":")[0] == "ns":
            x_cons.append(spo[1].split(":")[1])
        if spo[0].split(":")[0] == "?y" and spo[2].split(":")[0] == "ns":
            y_cons.append(spo[1].split(":")[1])
        if "FILTER(NOT" in line:
            y_cons.append(line.split(" ")[3].split(":")[1])
    if x_cons == []:
        x_cons = ""
    if y_cons == []:
        y_cons = ""

    return InferentialChain[0] + str(y_cons) + " [unused1] " + InferentialChain[1] + str(x_cons)





def get_2hop_po(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p ?y ?q ?x where{ ns:%s ?p ?y.?y ?q ?x}" % (
            entityID)
        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                data = []
                if len(results):
                    for i in range(len(results)):
                        temp = [replace_rdf(results[i]["p"]["value"]), replace_rdf(results[i]["q"]["value"])]
                        if temp not in data:
                            data.append(temp)
                    return data
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


def query_virtuoso_entityName(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select DISTINCT ?x  where{ ns:%s  ns:type.object.name ?x}" % (
            entityID)

        while True:
            try:
                sparqlQuery.setQuery(query_txt)
                results = sparqlQuery.query().convert()["results"]["bindings"]
                if len(results):
                    return results[0]["x"]["value"].replace("@en", "").replace("\"", "")
                else:
                    return None
            except Exception as e:
                print("发生错误:", e)
                time.sleep(5)
                continue


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


# 获取答案
def get_answer(entityID, queryGraph):
    if queryGraph.count("{") == queryGraph.count("}"):
        queryGraph = queryGraph + "}"
    sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> SELECT DISTINCT ?x WHERE { FILTER (?x != ns:%s) ns:%s %s" % (
        entityID, entityID, queryGraph)
    # print(sparql)
    sparqlQuery.setQuery(sparql)
    results = sparqlQuery.query().convert()["results"]["bindings"]
    # print(results)
    answer = []
    if len(results):
        for i in range(len(results)):
            data = replace_rdf(results[i]["x"]["value"])
            if data not in answer:
                answer.append(data)
        print(answer)
        return answer
    else:
        return None


def get_answer_to_name(entityID, queryGraph):
    try:
        if queryGraph.count("{") == queryGraph.count("}"):
            queryGraph = queryGraph + "}"
        sparql = "PREFIX ns: <http://rdf.freebase.com/ns/> SELECT DISTINCT ?x WHERE { FILTER (?x != ns:%s) . ns:%s %s" % (
            entityID, entityID, queryGraph)
        # print(sparql)
        sparqlQuery.setQuery(sparql)
        results = sparqlQuery.query().convert()["results"]["bindings"]
        # print(results)
        answer = []
        answer_name = []
        if len(results):
            for i in range(len(results)):
                data = results[i]["x"]["value"]
                if data not in answer:
                    if "http://rdf.freebase.com/ns/" in data:
                        sparql_name = "PREFIX ns: <http://rdf.freebase.com/ns/> select ?n where{ ns:%s  ns:type.object.name  ?n}" % (replace_rdf(data))
                        sparqlQuery.setQuery(sparql_name)
                        results_name = sparqlQuery.query().convert()["results"]["bindings"]
                        if len(results_name):
                            name = results_name[0]["n"]["value"].replace("@en", "").replace("\"", "").lower()
                            if name not in answer_name:
                                answer_name.append(name)
            # print(answer_name)
            return answer_name
        else:
            return None
    except Exception:
        print("发生异常")
        return None


if __name__ == '__main__':
    # from_id_path_get_2hop_po_oName("what year did the <e> win superbowl","m.01ct6","sports.sports_team.championships")
    # print(is_substring("M", "what is the name of <e> daughter"))
    # # print(match_ngram("", "what year did the <e> win super bowl college"))
    # print("m" in 'what is the name of <e> daughter')
    # print(is_query_anser("m.016rwt"," ns:people.person.children ?y .?y ns:people.person.sibling_s ?x.?x ns:people.person.gender ns:m.02zsn ."))

    # query_1hop_p_from_to( "m.05kkh","government.governmental_jurisdiction.governing_officials","2011")

    # from_id_path_get_3hop_po_oName_y("who did james franco play in <e>","m.03hkch7","film.film.starring","film.performance.character")
    # name = ''.replace("@en", "")
    #
    # is_sub = is_substring(name, "who did james franco play in <e>")
    # print(is_sub)

    # print(get_1hop_p("m.03ryn"))
    print(get_answer_to_name("m.0f2y0"," ns:education.athletics_brand.institution ?x"))
