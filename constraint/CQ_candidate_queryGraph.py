#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/3/7
# @Author  : hehl
# @Software: PyCharm
# @File    : candidate_queryGraph.py

import json
from loguru import logger
from query_virtuoso import *

import warnings

# 过滤警告
warnings.filterwarnings('ignore',
                        message="torch.distributed.reduce_op is deprecated, please use torch.distributed.ReduceOp instead")

"""需要注意的是sparql的查询语言是否正确！！！"""


# is_true字段已经弃用
#
# def over_leap(list1, list2):
#     if set(list1) == set(list2):
#         return 1
#     elif any(item in list1 for item in list2):
#         return 0.7
#     else:
#         return 0


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

        tp = 0.0  # numerical trick
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


def clean_sparql(topic_entity, sparql):
    queryGraph = ""
    oneSparql = sparql.strip().replace(f"ns:{topic_entity}", "").split("\n")
    for i in range(0, len(oneSparql)):
        if i >= 4:  # 去除前面部分的sparql  直接获取查询图
            # 删除主题实体
            if i == len(oneSparql) - 1 and oneSparql[i] == "}":  # 若最后一个是}则 不加入！
                pass
            else:
                queryGraph = queryGraph + oneSparql[i].split("#")[0]
    return queryGraph


"""针对查询图 选择能查询出答案的为正样本 若完全正确的则为1 否则为0.7"""


def create_negQG(name, linux):
    test_predEntity = {}
    with open("pred_topicEntity/CQ_entity.txt", "r", encoding="utf-8") as e:
        for entityinfo in e.readlines():
            info = entityinfo.strip().split("\t")
            test_predEntity[info[0]] = info[1]
    return test_predEntity


def create(name, linux=False, k=3, threshold=0.5):
    test_predEntity = create_negQG(name, linux)
    print(len(test_predEntity))
    preEntity_num = 0
    """生成候选查询图"""
    logger.info("开始生成候选查询图.....")

    gender_male = ["dad", "father", "son", "brothers", "brother"]
    gender_female = ["mom", "daughter", "wife", "mother", "mum"]
    marry = ["husband", "married", "marry", "wife"]  # people.marriage.type_of_union
    order_ASC = "first"  # from start_date  ?y ns:sports.sports_team_roster.from ?sk0 . ORDER BY xsd:datetime(?sk0) LIMIT 1    #first name/ first wife /first language
    order_DESC = "last"  # last year ! = 2014
    other_DESC = ["the most", "biggest", "largest", "predominant", "tallest", "major"]

    if linux:
        data_path = f"CQ/compQ.{name}.json"
    else:
        data_path = "../Datasets/WQSP/test.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for i in data:
            QuestionId = i["questionId"]
            q_id = QuestionId
            # if int(q_id.replace("WebQTest-", "")) > -1 :
            # if int(q_id.replace("WebQTrn-", "")) > -1:

            logger.info("生成%s的训练数据中......" % (QuestionId))
            w_json = open(f"WQSP_candidate_queryGraph_json/CQ_{name}_top{k}/{QuestionId}.json", "w", encoding="utf-8")
            path_info = {}
            # 存储问题的基本信息 id 问题 提及 实体id
            # 一定数据要都存在再处理
            path_info["QuestionId"] = QuestionId
            question = i["question"].replace("?","").replace(".","").lower()  # 大写转小写
            path_info["question"] = question
            mention = i["mention"].lower()
            path_info["mention"] = mention
            topicEntityID = i["TopicEntityMid"]
            path_info["topicEntityID"] = topicEntityID
            if name == "test":
                print(question)
                preTopicEntityID = test_predEntity.get(question)
                print(preTopicEntityID)
                path_info["preTopicEntityID"] = preTopicEntityID
                topicEntityID = preTopicEntityID
            print(topicEntityID)
            if topicEntityID:
                Answers = i["answer"]
                path_info["Answers"] = i["answer"]
                "存储问题的实体类型 由于前期已经查询过 直接从文件获取 不再查库浪费时间 "

                topicEntityType = query_virtuoso_entityType(topicEntityID)  # 查询实体类型
                path_info["topicEntityType"] = topicEntityType

                "生成正样本 注意：训练集的正样本从数据集中获取，测试集是直接选择打分最高的然后查询答案直接评估整体性能（也需要评估模型 所以也需要一个正样本） 所以对于测试集中多出一个字段来显示能否检索出正确的查询图"
                # "将语义结构分类模型用于判断 控制生成的查询图数量 （在此对每条候选查询图标注类型 之后再考虑是否用语义结构分类）"

                ################################################################################################################################################################################
                "生成负样本"  # 包括格式 分数 路径
                NegQueryGraph = []
                "变量最后一定要清零！！！！"

                "需要判断查询出的路径是否是正确的路径"

                logger.info("生成负样本中.......")
                query_e = question.replace(mention, "<e>")
                # query_e = query_e.replace("last year","2014")
                yearCons = find_year(query_e)  # 查找问题中有没有明确的时间约束 2012,2009....

                # 先查询第一跳的路径 ,返回top-3且分数大于0.5的路径及分数：
                one_hop_rels = from_id_to_topK_path(query_e, topicEntityID, k, threshold)
                print("one_hop_rels------------->", one_hop_rels)
                # ------至此：一跳无约束查找完毕
                is_true = False  # 用于判断是否能正确检索出正确的查询图

                if one_hop_rels:
                    for one_hop_rel in one_hop_rels:  # 第一跳的路径扩展
                        # 生成一跳无约束的样本，再存入json # ns:location.country.languages_spoken ?x .
                        # 判断是否是正确的查询
                        g_1hop = f" ns:{one_hop_rel[0]} ?x ."
                        preAnswer = get_answer_to_name(topicEntityID, g_1hop)  # 判断是否能够查询出正确的答案
                        if preAnswer:
                            q_g = {"path": g_1hop, "score": f"{one_hop_rel[1]}", "type": 0,
                                   "label": CalculatePRF1(preAnswer, Answers)}

                            NegQueryGraph.append(q_g)
                        # 若存在实体约束 则 添加实体约束  多个怎么办
                        """处理约束 实体约束（该实体信息在问题中存在） 约束加载第一跳的实体上"""  # 实体存在问题中 查询出第二跳的实体名称及路径  #多个约束 who is the voice of eric cartman on south park
                        one_hop_entity_constrains = from_id_path_get_2hop_po_oName(query_e, topicEntityID,
                                                                                   one_hop_rel[0])
                        # 返回多个不同的实体约束 要组合  已经做了 但是同名称的一起拼接会怎样!

                        if one_hop_entity_constrains:
                            for one_hop_entity_constrain in one_hop_entity_constrains:
                                g_1hop_c = g_1hop + f"?x ns:{one_hop_entity_constrain[0]} ns:{one_hop_entity_constrain[1]} ."  # 多个实体约束就都添加上！
                                preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                                # print("preAnswer-------------->", preAnswer)
                                if preAnswer:
                                    q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}",
                                           "entityName": one_hop_entity_constrain[2],
                                           "type": 1, "label": CalculatePRF1(preAnswer, Answers)}
                                    # 如果实体约束名称不一样 要拼接多个约束

                                    NegQueryGraph.append(q_g)

                        """如果问的是性别 婚姻等 直接加入约束--->但需要判断约束是否真实存在于知识库中  一跳问题的约束均加在x上"""
                        if set(gender_male) & set(query_e.split()):
                            g_1hop_c = g_1hop + f"?x ns:people.person.gender ns:m.05zppz ."  # 男性
                            preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                            if preAnswer:
                                # if is_query_anser(topicEntityID, g_1hop):
                                q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}", "entityName": "Male", "type": 1,
                                       "label": CalculatePRF1(preAnswer, Answers)}

                                NegQueryGraph.append(q_g)

                        if set(gender_female) & set(query_e.split()):
                            g_1hop_c = g_1hop + f"?x ns:people.person.gender ns:m.02zsn ."  # 女性
                            # if is_query_anser(topicEntityID, g_1hop):
                            preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                            if preAnswer:
                                q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}", "entityName": "Female",
                                       "type": 1,
                                       "label": CalculatePRF1(preAnswer, Answers)}

                                NegQueryGraph.append(q_g)

                        # """时间约束 主要是年份！"""
                        if yearCons:  # 如果问题中有年份的时间约束

                            yearData = yearCons[0]  # 以防万一有多个时间 但该数据集中只有一个  # 在x加上时间约束

                            # 至于约束的名称则需要在库里面查询 （ from ,to ）
                            from_path, to_path = query_1hop_p_from_to(topicEntityID, one_hop_rel[0],
                                                                      yearData)  # 选出成对的路径
                            if from_path and to_path:
                                g_1hop_c = g_1hop + 'FILTER(NOT EXISTS {?x ns:%s ?sk0} || EXISTS {?x ns:%s  ?sk1 . FILTER(xsd:datetime(?sk1) <= "%s-12-31"^^xsd:dateTime) })' \
                                                    'FILTER(NOT EXISTS {?x ns:%s ?sk2} || EXISTS {?x ns:%s  ?sk3 .  FILTER(xsd:datetime(?sk3) >= "%s-01-01"^^xsd:dateTime) })}' \
                                           % (from_path, from_path, yearData, to_path, to_path, yearData)
                                preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                                if preAnswer:
                                    q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}", "type": 1,
                                           "label": CalculatePRF1(preAnswer, Answers)}

                                    NegQueryGraph.append(q_g)

                            # 然后生成sparql查询是否是正确的！！！ 加入年份

                        if order_ASC in query_e.split():
                            # 查找包含date或from 的路径  sk0是时间 “1979”^^<http://www.w3.org/2001/XMLSchema#gYear>
                            paths = query_order_asc_1hop(topicEntityID, one_hop_rel[0])
                            if paths:
                                # 暂时只要一个
                                g_1hop_c = g_1hop + "?x ns:%s ?sk0 .}ORDER BY xsd:datetime(?sk0)LIMIT 1" % (paths[0])
                                preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                                if preAnswer:
                                    q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}", "type": 1,
                                           "label": CalculatePRF1(preAnswer, Answers)}

                                    NegQueryGraph.append(q_g)
                        elif order_DESC in query_e.split():
                            paths = query_order_desc_1hop(topicEntityID, one_hop_rel[0])
                            # print(paths) #多个path
                            if paths:
                                desc_path = paths[0]
                                for path in paths:
                                    if "end_date" in paths:
                                        desc_path = path
                                        break
                                # 暂时只要一个
                                g_1hop_c = g_1hop + "?x ns:%s ?sk0 .}ORDER BY DESC(xsd:datetime(?sk0))LIMIT 1" % (
                                    desc_path)
                                preAnswer = get_answer_to_name(topicEntityID, g_1hop_c)  # 判断是否能够查询出正确的答案
                                if preAnswer:
                                    q_g = {"path": g_1hop_c, "score": f"{one_hop_rel[1]}", "type": 1,
                                           "label": CalculatePRF1(preAnswer, Answers)}

                                    NegQueryGraph.append(q_g)
                        # 排序类的约束 first /last 处理
                        # 多个约束需要组合
                        # 若存在实体约束 则 不加入 无实体约束的一跳两跳的内容 因为实体约束一定会有！ 缩小查询图

                        """特殊的实体约束（该实体不在问题中存在 marr_ /时间 /性别）"""

                        ################################################################################################################################################################################

                        # 根据已知路径和主题实体获取谓语 并进行第二跳的选择
                        """根据问题判断是否存在约束 候选在做 先做核心路径推理"""
                        # o_Id = get_1hop_o(topicEntityID, one_hop_rel[0])   # 不在乎?y是什么 这里如果这样做会返回多个ID 加大图 所以直接根据id和路径获取第二跳的路径  有约束可能会在乎哪里
                        two_hop_rels = from_id_to_topK_2path(query_e, topicEntityID, one_hop_rel[
                            0], k, threshold)  # [('language.human_language.countries_spoken_in', 0.7789026498794556)]
                        if two_hop_rels:
                            for two_hop_rel in two_hop_rels:
                                g_2hop = f" ns:{one_hop_rel[0]} ?y .?y ns:{two_hop_rel[0]} ?x ."
                                preAnswer = get_answer_to_name(topicEntityID, g_2hop)
                                if preAnswer:
                                    q_g = {"path": g_2hop, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}", "type": 2,
                                           "label": CalculatePRF1(preAnswer, Answers)}
                                    NegQueryGraph.append(q_g)

                                """处理约束 实体约束 约束加载第二跳的实体上"""  # 实体存在问题中 查询出第二跳的实体名称及路径
                                two_hop_entity_constrains_x = from_id_path_get_3hop_po_oName_x(query_e, topicEntityID,
                                                                                               one_hop_rel[0],
                                                                                               two_hop_rel[0])

                                if two_hop_entity_constrains_x:  # 如果存在实体约束 变放弃无约束的路径 约束加在y上的
                                    for two_hop_entity_constrain in two_hop_entity_constrains_x:
                                        g_2hop_c = g_2hop + f"?x ns:{two_hop_entity_constrain[0]} ns:{two_hop_entity_constrain[1]} ."
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)  # 判断是否能够查询出正确的答案
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "entityName": two_hop_entity_constrain[2], "type": 3,
                                                   "label": CalculatePRF1(preAnswer, Answers)}


                                            NegQueryGraph.append(q_g)

                                # 在y上的实体约束
                                two_hop_entity_constrains_y = from_id_path_get_3hop_po_oName_y(query_e, topicEntityID,
                                                                                               one_hop_rel[0],
                                                                                               two_hop_rel[0])
                                if two_hop_entity_constrains_y:  # 如果存在实体约束 变放弃无约束的路径 约束加在y上的
                                    for two_hop_entity_constrain in two_hop_entity_constrains_y:
                                        g_2hop_c = g_2hop + f"?y ns:{two_hop_entity_constrain[0]} ns:{two_hop_entity_constrain[1]} ."
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)  # 判断是否能够查询出正确的答案
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "entityName": two_hop_entity_constrain[2], "type": 4,
                                                   "label": CalculatePRF1(preAnswer, Answers)}

                                            NegQueryGraph.append(q_g)

                                # 约束一定是加在x的吗？ 加在y上呢 要判断是否有这个约束
                                # 直接生成查询语言 能查出结果的就加在哪个上！！！！
                                """如果问的是性别 婚姻等 直接加入约束  但需要判断约束是否真实存在于知识库中 同时要考虑约束加在x还是y上   通过分类模型来判断？！！！！"""
                                # 若存在多种约束 需要加在上面 直接添加

                                if set(gender_male) & set(query_e.split()):
                                    g_2hop_c = g_2hop + f"?x ns:people.person.gender ns:m.05zppz ."  # 男性
                                    # if is_query_anser(topicEntityID, g_2hop):
                                    preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)  # 判断是否能够查询出正确的答案
                                    if preAnswer:
                                        q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                               "entityName": "Male", "type": 3,
                                               "label": CalculatePRF1(preAnswer, Answers)}
                                        NegQueryGraph.append(q_g)


                                    g_2hop_c = g_2hop + f"?y ns:people.person.gender ns:m.05zppz ."  # 男性 约束在y上
                                    # if is_query_anser(topicEntityID, g_2hop):
                                    preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)  # 判断是否能够查询出正确的答案
                                    if preAnswer:
                                        q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                               "entityName": "Male", "type": 4,
                                               "label": CalculatePRF1(preAnswer, Answers)}
                                        NegQueryGraph.append(q_g)

                                if set(gender_female) & set(query_e.split()):
                                    g_2hop_c = g_2hop + f"?x ns:people.person.gender ns:m.02zsn ."  # 女性
                                    # if is_query_anser(topicEntityID, g_2hop):
                                    preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)  # 判断是否能够查询出正确的答案
                                    if preAnswer:
                                        q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                               "entityName": "Female", "type": 3,
                                               "label": CalculatePRF1(preAnswer, Answers)}
                                        NegQueryGraph.append(q_g)


                                    g_2hop_c = g_2hop + f"?y ns:people.person.gender ns:m.02zsn ."  # 女性 约束在y上
                                    # if is_query_anser(topicEntityID, g_2hop):
                                    preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)
                                    if preAnswer:
                                        q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                               "entityName": "Female", "type": 4,
                                               "label": CalculatePRF1(preAnswer, Answers)}
                                        NegQueryGraph.append(q_g)

                                if set(marry) & set(query_e.split()):
                                    g_2hop_c = g_2hop + f"?y ns:people.marriage.type_of_union ns:m.04ztj ."  # 婚姻 约束在y上 是否都有时间限制
                                    if "married" in query_e.split() and yearCons is None:
                                        g_2hop_c = g_2hop_c + 'FILTER(NOT EXISTS {?y ns:people.marriage.from ?sk0} || EXISTS {?y ns:people.marriage.from ?sk1 . ' \
                                                              'FILTER(xsd:datetime(?sk1) <= "2015-08-10"^^xsd:dateTime) })FILTER(NOT EXISTS {?y ns:people.marriage.to ?sk2} || ' \
                                                              'EXISTS {?y ns:people.marriage.to ?sk3 . FILTER(xsd:datetime(?sk3) >= "2015-08-10"^^xsd:dateTime) })}'
                                        # if is_query_anser(topicEntityID, g_2hop):
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "entityName": "Marriage", "type": 4,
                                                   "label": CalculatePRF1(preAnswer, Answers)}
                                            NegQueryGraph.append(q_g)

                                if yearCons:  # 如果问题中有年份的时间约束
                                    yearData = yearCons[0]  # 以防万一有多个时间 但该数据集中只有一个  # 在y加上时间约束
                                    # 至于约束的名称则需要在库里面查询 （ from ,to ）
                                    from_path, to_path = query_2hop_p_from_to(topicEntityID, one_hop_rel[0],
                                                                              two_hop_rel[0], yearData)  # 选出成对的路径
                                    if from_path and to_path:
                                        g_2hop_c = g_2hop + 'FILTER(NOT EXISTS {?y ns:%s ?sk0} || EXISTS {?y ns:%s  ?sk1 . FILTER(xsd:datetime(?sk1) <= "%s-12-31"^^xsd:dateTime) })' \
                                                            'FILTER(NOT EXISTS {?y ns:%s ?sk2} || EXISTS {?y ns:%s  ?sk3 .  FILTER(xsd:datetime(?sk3) >= "%s-01-01"^^xsd:dateTime) })}' \
                                                   % (from_path, from_path, yearData, to_path, to_path, yearData)
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "type": 4,
                                                   "label": CalculatePRF1(preAnswer, Answers)}
                                            NegQueryGraph.append(q_g)

                                    # 然后生成sparql查询是否是正确的！！！ 加入年份
                                if order_ASC in query_e.split():  # 通过观察约束均在y上
                                    # 查找包含date或from 的路径  sk0是时间 “1979”^^<http://www.w3.org/2001/XMLSchema#gYear>
                                    paths = query_order_asc_2hop(topicEntityID, one_hop_rel[0], two_hop_rel[0])
                                    if paths:
                                        # 暂时只要一个paths
                                        g_2hop_c = g_2hop + "?y ns:%s ?sk0 .}ORDER BY xsd:datetime(?sk0)LIMIT 1" % (
                                            paths[0])
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "type": 4, "label": CalculatePRF1(preAnswer, Answers)}
                                            NegQueryGraph.append(q_g)

                                elif order_DESC in query_e.split():
                                    paths = query_order_desc_2hop(topicEntityID, one_hop_rel[0], two_hop_rel[0])
                                    if paths:
                                        # 暂时只要一个paths
                                        desc_path = paths[0]
                                        for path in paths:
                                            if "end_date" in paths:
                                                desc_path = path
                                                break
                                        g_2hop_c = g_2hop + "?y ns:%s ?sk0 .}ORDER BY DESC(xsd:datetime(?sk0))LIMIT 1" % (
                                            desc_path)
                                        preAnswer = get_answer_to_name(topicEntityID, g_2hop_c)
                                        if preAnswer:
                                            q_g = {"path": g_2hop_c, "score": f"{one_hop_rel[1]}#{two_hop_rel[1]}",
                                                   "type": 4, "label": CalculatePRF1(preAnswer, Answers)}
                                            NegQueryGraph.append(q_g)


                            # ------至此：两跳无约束查找完毕
                path_info["NegQueryGraph"] = NegQueryGraph
                path_info["is_true"] = is_true
                # 将全部信息存入json
                json.dump(path_info, w_json, indent=4)
        # 滚动！

        preEntity_num += 1


if __name__ == '__main__':
    for i in [1,2,4,5]:
        create("test", True, i, 0.2)


