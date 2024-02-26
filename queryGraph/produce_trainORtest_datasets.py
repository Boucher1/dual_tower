import json
from collections import defaultdict
json_file = open('test_data.json', 'w')

def repData(data):
    return data.replace("http://rdf.freebase.com/ns/","")

with open("../origin_dataset/WebQSP.train.json","r",encoding="utf-8") as f:
    train_data = json.load(f)
    train_question_e = defaultdict(list)
    train_question_e["introduction"].append(" introduction")

    for i in train_data["Questions"]:
        ques_info = {}
        question = i["ProcessedQuestion"]
        PotentialTopicEntityMention = i["Parses"][0]["PotentialTopicEntityMention"]
        if PotentialTopicEntityMention is None:
            continue
        TopicEntityMid = i["Parses"][0]["TopicEntityMid"]
        question_e = question.replace(PotentialTopicEntityMention,",<e>")
        ques_info["question_e"] = question_e

        with open(f"query_graph/{TopicEntityMid}.json","r",encoding="utf-8") as entity:
            # entity_info = json.re(entity)
            typelist= []
            for line in entity.readlines():
                # print(json.loads(line)["p"]["value"].replace("http://rdf.freebase.com/ns/","").split(".")[2])
                istype = repData(json.loads(line)["p"]["value"])
                if istype not in typelist:
                    typelist.append(istype)

            if len(typelist) == 0:
                print(TopicEntityMid)
        train_question_e["question"].append(json.dumps(ques_info))

    # json_str = json.dumps(train_question_e, indent=4)
    # with open('test_data.json', 'w') as json_file:
    #     json_file.write(json_str)

# with open('test_data.json', 'r') as json_file:
#     f = json.load(json_file)
#     for i in f["question"]:
#         print(i)
