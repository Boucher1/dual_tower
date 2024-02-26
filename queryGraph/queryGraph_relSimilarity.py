from transformers import BertTokenizer
import torch
import torch.nn.functional as F
"两个文本比较相似度"
tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
# question_text = 'who plays ken barlow in <e>'
# bert_input_q = tokenizer(question_text, padding='max_length',
#                        max_length = 100,
#                        truncation = True,
#                        return_tensors = "pt")
#
# query_graph = "award.award_nominated_work.award_nominations"
# bert_input_g = tokenizer(query_graph, padding='max_length',
#                        max_length = 100,
#                        truncation = True,
#                        return_tensors = "pt")
#
# # ------- bert_input ------
# print(bert_input_q['input_ids'])
# print(bert_input_g['input_ids'])
#
# q = bert_input_q['input_ids']
# g = bert_input_g['input_ids']
#
# print(F.cosine_similarity(q.float(),g,dim=1))


"问句与核心推导链直接的相似度"
import json
with open("../origin_dataset/WebQSP.test.json","r",encoding="utf-8") as f:
    data =json.load(f)
    maxScore = 0
    minScore = 1
    num = 0
    for i in data["Questions"]:
        query = i["ProcessedQuestion"]
        mention = i["Parses"][0]["PotentialTopicEntityMention"]
        query_e = query.replace(mention, "")
        bert_input_q = tokenizer(query_e, padding='max_length', max_length=100, truncation=True, return_tensors="pt")
        q = bert_input_q['input_ids'].float()
        TopicEntityMid = i["Parses"][0]["TopicEntityMid"]
        InferentialChain = i["Parses"][0]["InferentialChain"]

        # p_info = []
        # with open(f"query_graph/{TopicEntityMid}.json", "r", encoding="utf-8") as f:
        #     for line in f.readlines():
        #         p = json.loads(line)["p"]["value"].replace("http://rdf.freebase.com/ns/", "")
        #         if p not in p_info:
        #             p_info.append(p)
        # for p in p_info:
        #     bert_input_g = tokenizer(p, padding='max_length', max_length=100, truncation=True, return_tensors="pt")
        #     sim = F.cosine_similarity(q, bert_input_g['input_ids'], dim=1)
        if InferentialChain is not None:
            # print(InferentialChain[0])
            inferential = InferentialChain[0].split(".")[2]
            bert_input_g = tokenizer(inferential, padding='max_length', max_length=100, truncation=True, return_tensors="pt")
            sim = F.cosine_similarity(q, bert_input_g['input_ids'], dim=1)
            score = sim[0].item()
            if score < 0.1:
                num += 1
            if score > maxScore:
                maxScore = score
            if score < minScore:
                minScore = score
            if score < 0.05:
                print(i["QuestionId"])
            # print(sim[0].item())
        # print("-"*50)
    print(maxScore,minScore)
    print(num)

#
# "利用sbert训练相似度模型"
# from sentence_transformers import models, evaluation
# word_embedding_model = models.Transformer()
