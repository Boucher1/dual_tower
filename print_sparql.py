# """是否需要预测查询图的结构"""
# dateTimeList =["first","last","most","est","start","new","original","2012"]
# dateTimeList = ["most", "est", "start", "new", "original", "2012"]
# num = 0
# num_no = 0
# import json
#
# stru = []
#
#
# def create_ngram_list(input):
#     input_list = input.lower().split(" ")
#     ngram_list = []
#     for num in range(len(input_list) + 1, -1, -1):
#         for tmp in zip(*[input_list[i:] for i in range(num)]):
#             tmp = " ".join(tmp)
#             ngram_list.append(tmp)
#
#     return ngram_list
#
#
# with open("./Datasets/myWQSP/WebQSP.test.json", "r") as f:
#     for line in f.readlines():
#         path = ""
#         line = json.loads(line)
#         query = line["query"]
#         # print("-" * 50, query)
#         mention = line["PotentialTopicEntityMention"]
#         entityId = line["TopicEntityMid"]
#         if mention is None:
#             mention = ""
#         query_e = query.replace(mention, "<e>")
#         query_addType = query_e + " [unused0] " + line["entityType"]
#         InferentialChain = line["InferentialChain"]
#         if InferentialChain is None:
#             InferentialChain = []
#         Constraints = line["Constraints"]
#         if Constraints is None:
#             Constraints = []
#         Time = line["Time"]
#         Order = line["Order"]
#
#         sparql = line["sparql"]
#         path = ""
#         # if len(InferentialChain) == 2 and len(Constraints) > 0:
#         #     # print(sparql)
#         #     path =
#
# print("PREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT DISTINCT ?x\nWHERE {\nFILTER (?x != ns:m.0vmt)\nns:m.0vmt ns:government.governmental_jurisdiction.governing_officials ?y .\n?y ns:government.government_position_held.office_holder ?x .\n?y ns:government.government_position_held.basic_title ns:m.0fkvn .\nFILTER(NOT EXISTS {?y ns:government.government_position_held.from ?sk0} || \nEXISTS {?y ns:government.government_position_held.from ?sk1 . \nFILTER(xsd:datetime(?sk1) <= \"2009-12-31\"^^xsd:dateTime) })\nFILTER(NOT EXISTS {?y ns:government.government_position_held.to ?sk2} || \nEXISTS {?y ns:government.government_position_held.to ?sk3 . \nFILTER(xsd:datetime(?sk3) >= \"2009-01-01\"^^xsd:dateTime) })\n}\n"
#           )
# print("#MANUAL SPARQL\nPREFIX ns: <http://rdf.freebase.com/ns/>\nSELECT DISTINCT ?x \nWHERE {\n    ns:m.059g4 ns:location.location.contains ?x .  # North America\n    ?x ns:common.topic.notable_types ns:m.01mp . # Country\n    ?x ns:location.location.contains ?y .\n    ?y ns:common.topic.notable_types ?t . \n# All the possible \"province\" type\nFILTER ((?t = ns:m.01nm) ||\n(?t = ns:m.02_1y_9) ||\n(?t = ns:m.02_3ny_) ||\n(?t = ns:m.02_3phk) ||\n(?t = ns:m.02_3r2r) ||\n(?t = ns:m.02_3rt3) ||\n(?t = ns:m.02_3zf4) ||\n(?t = ns:m.02_40h1) ||\n(?t = ns:m.02_96lm) ||\n(?t = ns:m.02yxk5c) ||\n(?t = ns:m.02zd6yn) ||\n(?t = ns:m.03z96kq) ||\n(?t = ns:m.04g7rg9) ||\n(?t = ns:m.04js0h5) ||\n(?t = ns:m.065rjpr) ||\n(?t = ns:m.078_8dm) ||\n(?t = ns:m.0hzcb3l) ||\n(?t = ns:m.0hzcb5p) ||\n(?t = ns:m.0hzcb69) ||\n(?t = ns:m.0hzcb7p) ||\n(?t = ns:m.0hzcd76) ||\n(?t = ns:m.0hzcd7v) ||\n(?t = ns:m.0hzcdb0) ||\n(?t = ns:m.0hzcdd6) ||\n(?t = ns:m.0hzcdlq) ||\n(?t = ns:m.0hzcdmg) ||\n(?t = ns:m.0hzcdrj) ||\n(?t = ns:m.0hzcdzg) ||\n(?t = ns:m.0hzcdzv) ||\n(?t = ns:m.0hzcf4d) ||\n(?t = ns:m.0hzcf50) ||\n(?t = ns:m.0hzcfdx) ||\n(?t = ns:m.0hzcffv) ||\n(?t = ns:m.0hzcfgg) ||\n(?t = ns:m.0hzcfj0) ||\n(?t = ns:m.0hzcfm2) ||\n(?t = ns:m.0hzcfpz) ||\n(?t = ns:m.0hzcfsv) ||\n(?t = ns:m.0hzcfyb) ||\n(?t = ns:m.0hzcg20) ||\n(?t = ns:m.0hzcg90) ||\n(?t = ns:m.0hzcgdz) ||\n(?t = ns:m.0hzcgfl) ||\n(?t = ns:m.0hzcggv) ||\n(?t = ns:m.0hzcgj2) ||\n(?t = ns:m.0hzcgk4) ||\n(?t = ns:m.0hzcgny) ||\n(?t = ns:m.0hzcgqt) ||\n(?t = ns:m.0hzcgsp) ||\n(?t = ns:m.0hzcgvh) ||\n(?t = ns:m.0hzcgvw) ||\n(?t = ns:m.0hzcgxf) ||\n(?t = ns:m.0hzcjv6) ||\n(?t = ns:m.0hzcjvv) ||\n(?t = ns:m.0hzcjxq) ||\n(?t = ns:m.0hzck_1) ||\n(?t = ns:m.0hzck1r) ||\n(?t = ns:m.0hzck47) ||\n(?t = ns:m.0hzck7p) ||\n(?t = ns:m.0hzckbh) ||\n(?t = ns:m.0hzckgc) ||\n(?t = ns:m.0hzcklh) ||\n(?t = ns:m.0hzckv_) ||\n(?t = ns:m.0hzckvp) ||\n(?t = ns:m.0hzckwy) ||\n(?t = ns:m.0hzcl1k) ||\n(?t = ns:m.0hzcl2t) ||\n(?t = ns:m.0hzfxh6) ||\n(?t = ns:m.0hzfxjh) ||\n(?t = ns:m.0hzfxny) ||\n(?t = ns:m.0hzfxv1) ||\n(?t = ns:m.0hzfxx7) ||\n(?t = ns:m.0hzfxzs) ||\n(?t = ns:m.0hzfy0d) ||\n(?t = ns:m.0hz_gjz) ||\n(?t = ns:m.0hzjldq) ||\n(?t = ns:m.0hzjm9b) ||\n(?t = ns:m.0hzjmf9) ||\n(?t = ns:m.0hzjmjf) ||\n(?t = ns:m.0hzjmlj) ||\n(?t = ns:m.0hzjmm6) ||\n(?t = ns:m.0hzjmmx) ||\n(?t = ns:m.0j1zd59) ||\n(?t = ns:m.0j1zd5w) )\n}".splitlines())

# from_path = ""
# to_path = ""
# if from_path and to_path:
#     print("-")
#     if to_path.split(".")[1] == from_path.split(".")[1]:
#             print( from_path, to_path)

