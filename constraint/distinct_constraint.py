#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/23
# @Author  : hehl
# @Software: PyCharm
# @File    : distinct_constraint.py

import json

"""识别时间约束 和 排序约束等"""

"""
    时间约束：
   train [None, '2010', '2011', '2012', '2013', 'now', 'new', '1819', '1945', '2009', 'current, today', 'present', '2003', 
   'currently', '2007', 'current', '1980', '1996', '1998', 'just', '1958', '2005', '1948', '1971', '2008', '1800s']
   
   test ['2011', None, 'now', 'right now', '2012', '2010', 'the 90s', '2003', '2013', '1988', '2009', '2008', '1999', 
   '1993', 'current', 'last year', '1971', 'today', '1859']
   
   
   排序约束：
   date
   first + from
   marr_  + to  /from
   last   time.event.end_date
         time.event.start_date
    城市约束： Country /state common.topic.notable_types 
    性别约束： Male: dad,father,son,brothers,brother/Female:mom,daughter,wife,mother,mum [people.person.gender]
    婚姻约束 Marriage：marr_ , husband, married, marry, wife  [people.marriage.type_of_union]
    College/University    
    president government.government_position_held.office_position_or_title    
              government.government_position_held.office_position_or_title 
    highschool: base.schemastaging.non_profit_extra.classification    
    College/University: common.topic.notable_types                            

        
"""

"""
const_minimax_dic = 'first|last|predominant|biggest|major|warmest|tallest|current|largest|most|newly|son|daughter' #
self.const_time = re.findall('\d+', raw_question) if re.search('\d+', raw_question) and len(re.findall('\d+', raw_question)[0])==4 else None
self.const_minimax = re.findall('(?<= )(%s)' %const_minimax_dic, raw_question) if re.search('(?<= )(%s)' %const_minimax_dic, raw_question) else None
"""
import re


# const_minimax_dic = 'first|last|predominant|biggest|major|warmest|tallest|current|largest|most|newly|son|daughter' #
#
#
#
# PotentialTimeMention = []
# with open("../Datasets/WQSP/WebQSP.test.json", "rb") as f:
#     data = json.load(f)
#     for i in data["Questions"]:
#         query = i["ProcessedQuestion"]
#         mention = i["Parses"][0]["PotentialTopicEntityMention"]
#         if mention is None:
#             mention = ""
#         query_e = query.replace(mention, "<e>")
#         Time = i["Parses"][0]["Time"]
#         sparql = i["Parses"][0]["Sparql"]
#         # if Time is not None:
#         #     print(query_e)
#         #     if Time["PotentialTimeMention"] not in PotentialTimeMention:
#         #         PotentialTimeMention.append(Time["PotentialTimeMention"])
#         # pass
#
#         Order = i["Parses"][0]["Order"]
#         if Order is not None:
#             print(query)
#             print(sparql)
#             print(Order["NodePredicate"],Order["ValueType"])
#
#         # const_time = re.findall('\d+', query_e) if re.search('\d+', query_e) and len(
#         #     re.findall('\d+', query_e)[0]) == 4 else None
#         #
#         # const_minimax = re.findall('(?<= )(%s)' % const_minimax_dic, query_e) if re.search(
#         #     '(?<= )(%s)' % const_minimax_dic, query_e) else None
#         # if const_minimax is not None or const_time is not None:
#         #     print(query,"------------------>",const_minimax, const_time)
# # print(PotentialTimeMention)


def list_overlap_f1(list1, list2):
    exists_count = 0
    if set(list1) == set(list2):
        return 1
    elif any(item in list1 for item in list2):
        for i in list1:
            if i in list2:
                exists_count += 1
        return exists_count / len(list1)
    else:
        return 0


def FindInList(entry, elist):
    for item in elist:
        if entry == item:
            return True
    return False


def CalculatePRF1(glist, predAnswerList):
    if len(predAnswerList) == 0 or len(glist) == 0:
        return 0.0
    else:

        plist = predAnswerList

        tp = 0.0 # numerical trick
        fp = 0.0
        fn = 0.0

        for gentry in glist:
            if FindInList(gentry, plist):
                tp += 1
            else:
                fn += 1
        for pentry in plist:
            if not FindInList(pentry, glist):
                fp += 1
        if tp == 0:
            return 0.0
        else:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)

            f1 = (2 * precision * recall) / (precision + recall)
        return f1


if __name__ == '__main__':
    # test_predEntity = []
    # with open("pred_topicEntity/topic_entity_for_question_new.txt", "r", encoding="utf-8") as e:
    #     for entityinfo in e.readlines():
    #         data = {}
    #         line = entityinfo.split(",")
    #         data["question"]=line[0]
    #         data["ID"] = line[1]
    #         test_predEntity.append(json.dumps(data))
    # preEntity_num = 0
    # print( json.loads(test_predEntity[0])["ID"])
    # num = 0
    # with open("../Datasets/WQSP/WebQSP.test.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    #     for i in data["Questions"]:
    #         queryID = i["QuestionId"]
    #         query = i["ProcessedQuestion"]
    #         if json.loads(test_predEntity[preEntity_num])["question"] == i["ProcessedQuestion"]:
    #             preEntity_num += 1
    #             print(queryID)
    #             num += 1
    #             if i["Parses"][0]["PotentialTopicEntityMention"] and i["Parses"][0]["TopicEntityMid"] and i["Parses"][0][
    #                     "TopicEntityName"] and i["Parses"][0]["Sparql"]:
    #                 print("生成负样本中")
    # print(num)
    print(CalculatePRF1([], []))
