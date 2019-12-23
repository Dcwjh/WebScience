from pku import PKU
from ltp import LTP
from neo4j import Neo4j

# 配置参数（根据自己情况设置，这里路径是以manage.py为准）
CUSTOMIZED_DICT_PATH = './FAQs/data/dict.txt'  # 自定义字典（添加图谱中所有的实体名称）
LTP_DIR_PATH = './FAQs/ltp_data_v3.4.0'  # ltp加载路径
NEO4J_URL = 'http://localhost:7474'  # neo4j的url
NEO4J_USERNAME = 'neo4j'  # neo4j的username
NEO4J_PASSWORD = '123456'  # neo4j的password
ENTITY_DICT_PATH = './FAQs/data/entity.txt'
RELATION_DICT_PATH = './FAQs/data/relation.txt'
# 实体化所有工具类
# 分词
pku = PKU(CUSTOMIZED_DICT_PATH)
# 词性解析
ltp = LTP(LTP_DIR_PATH)
# neo4j数据查询
neo4j = Neo4j(NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD)
entities = list()
relations = list()
with open(ENTITY_DICT_PATH, 'r', encoding='utf8') as fr:
    for line in fr:
        entities.append(line.strip())

with open(RELATION_DICT_PATH, 'r', encoding='utf8') as fr2:
    for line in fr2:
        relations.append(line.strip())
