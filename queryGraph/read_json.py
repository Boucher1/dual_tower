import json

value = []
# with open("query_graph/m.01_2n.json","r",encoding="utf-8") as f:
#     for line in f.readlines():
#         if  json.loads(line)["p"]["value"] not in value:
#             value.append( json.loads(line)["p"]["value"])
# # print(value)
# for i in value:
#     print(i.replace("http://rdf.freebase.com/ns/",""))
# print(len(value))

# path = []
# with open("new_queryGraph/m.031v20.json","r",encoding="utf-8") as f:
#     for line in f.readlines():
#         # if json.loads(line)["p"]["value"].replace("http://rdf.freebase.com/ns/","") == "type.object.type":
#         #     print(json.loads(line)["o"]["value"].replace("http://rdf.freebase.com/ns/",""))
#         p = json.loads(line)["p"]["value"].replace("http://rdf.freebase.com/ns/", "")
#         x = json.loads(line)["x"]["value"].replace("http://rdf.freebase.com/ns/", "")
#         if p not in path:
#             path.append(p)
#         if p+"#"+x not in path:
#             path.append(p+"#"+x)
#     print(path)
#     print(len(path))

# print(value)
# for i in value:
#     print(i)
# print(len(value))

# import re
#
#
# def find_year(text):
#     pattern = r'\b\d{4}\b'  # 匹配四位数的数字
#     year_list = []
#     for match in re.finditer(pattern, text):
#         year = int(match.group())  # 遍历匹配结果，转换成整数后添加到列表中
#         if year >= 1000 and year <= 9999:  # 判断是否为年份
#             year_list.append(year)
#     return year_list
#
#
# # text = "where does kate middleton live 2012"
# # year_list = find_year(text)
# # print(year_list)  # 输出 [1995]
# def clean_sparql(topic_entity, sparql):
#     queryGraph = ""
#     oneSparql = sparql.strip().replace(f"ns:{topic_entity}", "").split("\n")
#     for i in range(0, len(oneSparql)):
#         if i >= 4:  # 去除前面部分的sparql  直接获取查询图
#             # 删除主题实体
#
#             queryGraph = queryGraph + oneSparql[i].split("#")[0]
#     return queryGraph
#
# # w = open("../../../FB5M/NER/data/WQ_entity.txt","w",encoding="utf-8")
#
# other_DESC = [ "biggest", "largest", "predominant", "most"]


# q = []
# num = 0
# w = open("in_WQSP_q.txt", "w")
# with open("no_mention_q.txt", "r") as cq:
#     for i in cq.readlines():
#         q.append(i.strip())
with open("../Datasets/WQSP/WebQSP.test.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for i in data["Questions"]:
        queryID = i["QuestionId"]
        query = i["RawQuestion"]
        Constraints = i["Parses"][0]["Constraints"]
        InferentialChain = i["Parses"][0]["InferentialChain"]
        Time =  i["Parses"][0]["Time"]
        Order =  i["Parses"][0]["Order"]
        if len(InferentialChain) == 2  and Constraints and Order:
            print(query)
        # if query in q:
        #     w.write(query + "\n")
        #     num += 1
# with open("../Datasets/WQSP/WebQSP.train.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     for i in data["Questions"]:
#         queryID = i["QuestionId"]
#         query = i["RawQuestion"]
#         if query in q:
#             w.write(query + "\n")
#             num += 1
# with open("../Datasets/WQSP/WebQSP.train.partial.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     for i in data["Questions"]:
#         queryID = i["QuestionId"]
#         query = i["RawQuestion"]
#         if query in q:
#             w.write(query + "\n")
#             num += 1
# with open("../Datasets/WQSP/WebQSP.test.partial.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     for i in data["Questions"]:
#         queryID = i["QuestionId"]
#         query = i["RawQuestion"]
#         if query in q:
#             w.write(query + "\n")

        # mention = i["Parses"][0]["PotentialTopicEntityMention"]
        # Id = i["Parses"][0]["TopicEntityMid"]
        # TopicEntityName = i["Parses"][0]["TopicEntityName"]
        # if mention is None:
        #     mention = " "
        # if Id is None:
        #     Id = ' '
        # if TopicEntityName is None:
        #     TopicEntityName = " "
        # if i["Parses"][0]["PotentialTopicEntityMention"] and i["Parses"][0]["TopicEntityMid"] and i["Parses"][0][
        #     "TopicEntityName"] and i["Parses"][0]["Sparql"]:
        #     print(queryID)
        # print(query)
        # print(mention)
        # print(Id)
        # print(TopicEntityName)
        # w.w
        # w.writelines(query+"\t"+mention+"\t"+Id+"\t"+TopicEntityName+"\n")
        # query_e = query.replace(mention, "<e>")
        # Constraints = i["Parses"][0]["Constraints"]
        # InferentialChain = i["Parses"][0]["InferentialChain"]
        # Sparql = i["Parses"][0]["Sparql"]
        # Time = i["Parses"][0]["Time"]
        # Order = i["Parses"][0]["Order"]

f.close()
# print(num)
