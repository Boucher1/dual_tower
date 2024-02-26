#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/27
# @Author  : hehl
# @Software: PyCharm
# @File    : query_virtuoso.py


from SPARQLWrapper import SPARQLWrapper, JSON

"""链接virtuoso 设置返回数据为json格式"""
sparqlQuery = SPARQLWrapper("http://43.142.132.166:8890/sparql")
sparqlQuery.setReturnFormat(JSON)

import time
import eventlet  #导入eventlet这个模块
eventlet.monkey_patch()   #必须加这条代码

def replace_rdf(p):
    return p.replace("http://rdf.freebase.com/ns/", "")


def create_ngram_list(input):
    input_list = input.lower().split(" ")
    ngram_list = []

    for num in range(len(input_list) + 1, -1, -1):
        for tmp in zip(*[input_list[i:] for i in range(num)]):
            tmp = " ".join(tmp)
            ngram_list.append(tmp)
    return ngram_list


def get_1hop_p(entityID):
    if "m." in entityID or  "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p  where{ ns:%s  ?p ?o}" % (entityID)
        with eventlet.Timeout(60, False):
            sparqlQuery.setQuery(query_txt)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    if results[i]["p"]["value"] not in data:
                        data.append(replace_rdf(results[i]["p"]["value"]))
                # 返回不重复的Path
                return data
            else:
                return None
    return None


def get_1hop_p_o_name(entityID):
    if "m." in entityID or  "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p ?o ?n where{ ns:%s  ?p ?o.?o ns:type.object.name ?n}" % (
            entityID)
        with eventlet.Timeout(60, False):
            sparqlQuery.setQuery(query_txt)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    print()
                    po = [replace_rdf(results[i]["p"]["value"]), replace_rdf(results[i]["o"]["value"]),
                          replace_rdf(results[i]["n"]["value"])]
                    if po not in data:
                        data.append(po)
                # 返回不重复的Path
                return data
            else:
                return None
    return None


def get_1hop_o(entityID, p):
    if "m." in entityID or  "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?o  where{ ns:%s  ns:%s ?o}" % (entityID, p)
        with eventlet.Timeout(60, False):
            sparqlQuery.setQuery(query_txt)
            results = sparqlQuery.query().convert()["results"]["bindings"]
            data = []
            if len(results):
                for i in range(len(results)):
                    if results[i]["o"]["value"] not in data:
                        data.append(replace_rdf(results[i]["o"]["value"]))
                # 返回不重复的Path
                return data
            else:
                return None
    return None


def get_2hop_po(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?p ?y ?q ?x where{ ns:%s ?p ?y.?y ?q ?x}" % (
        entityID)
        with eventlet.Timeout(60, False):
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
    return None


def query_virtuoso_entityName(entityID):
    if "m." in entityID or "g." in entityID:
        query_txt = "PREFIX ns: <http://rdf.freebase.com/ns/> select  ?x  where{ ns:%s  ns:type.object.name ?x}" % (
            entityID)
        with eventlet.Timeout(60, False):
            sparqlQuery.setQuery(query_txt)
            results = sparqlQuery.query().convert()["results"]["bindings"]

            if len(results):
                return results[0]["x"]["value"].replace("@en", "")
            else:
                return None
    return None

#
#
# data = {}
# p = ["p","q"]
# o = "o"
# data[p[1]] = 0
# print(data.keys())
# print(data.values())
