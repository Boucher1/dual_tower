>train:3098-1(错误Sprql 无实体 无约束)
test:1639(部分mention 的空格经过处理 )

本次构建的virtuoso已经过处理 仅包含英文知识 



主题实体类型对确定核心路径起着重要作用
domain->type->topic
域 类型
kg.object_profile.prominent_type
type.object.name # 名字
type.object.type  # 筛掉一部分关系！ （至少他不应该被包含在候选路径中）
common.topic.notable_types 实体类型

查询实体的类型名称:
PREFIX ns: <http://rdf.freebase.com/ns/>
select  ?x 
where{
ns:m.03_r3 ns:common.topic.notable_types ?o.
?o ns:type.object.name ?x}

1-2跳作为核心推理链

约束和推理链之和：
{0: 23, 1: 940, 2: 345, 3: 227, 4: 67, 5: 36, 6: 1, 7: 0, 8: 0, 9: 0}

sparql的长度：[7+8+9] = (一跳/两跳/加一个约束) = 1440 = 87.85%
{0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 912, 8: 309, 9: 219, 10: 27, 11: 22, 12: 9, 13: 2, 14: 61, 15: 33, 16: 3, 17: 0, 18: 0, 19: 0}

42个 MANUAL SPARQL == 2.56%

23个问题无约束

Time：
1. 与时间有关：42个 2012/90s
2. 与现在相关：57个  marry

Order:
1. DateTime 42个 first/last
2. Number 7个 largest/most/predominant 

entity

209个值的约束 例如2015-08-10
113个实体约束在问题中出现  对于这类型的问题他依靠实体链接或者 出现在问句中的实体和中间变量名称相同来确定  marr_
231个与问题不完全相同的实体 (部分约束实体在问句中出现)
107个问题不止一个约束
343个2015-08-10的约束
性别约束：male/female(son Dad)
约束是加在x或y的！ 

语义结构分类来缩小空间 按比例缩小 不完全依靠他

或许可以做一个语义结构分类模型！ 


 