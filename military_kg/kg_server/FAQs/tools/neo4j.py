from py2neo import Graph, Node


class Neo4j:

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.graph = Graph(self.url, username=self.username, password=self.password)
        print('neo4j数据库连接成功...')

    # 根据主实体e1找出其相连的所有关系三元组ere
    def find_ere_by_e1(self, e1):
        data = self.graph.run(
            "MATCH (e1 :entity{name:\"" + str(
                e1) + "\"})- [r] -> (e2) RETURN e1,r,e2").data()
        return self.data2json(data)

    def find_ere_by_r(self, r):
        cypher = "match (e1)-[r:%s]->(e2) return e1,r,e2" % r
        data = self.graph.run(cypher).data()
        return self.data2json(data)

    # 根据子实体e2找出其相连的所有关系三元组ere
    def find_relation_by_e2(self, e2):
        data = self.graph.run("MATCH (e1)- [r] -> (e2 {name:\"" + str(e2) + "\"}) RETURN e1,r,e2").data()
        return self.data2json(data)

    # 根据主实体e1和关系r查找子实体e2
    def find_e2_by_e1r(self, e1, r):
        data = self.graph.run(
            "MATCH (e1:entity{name:\"" + str(e1) + "\"})- [r:" + str(r) + "] - (e2) RETURN e1,r,e2").data()
        return self.data2json(data)

    # 根据子实体e2和关系r查找主实体e1
    def find_e1_by_re2(self, r, e2):
        data = self.graph.run(
            "MATCH (e1)- [r:" + str(r) + "] -> (e2 {name:\"" + str(e2) + "\"}) RETURN e1").data()
        return self.data2json(data)

    # 多实体条件查询实体
    def query_by_multi_condition(self, *args):
        cypher = ''
        for index in range(len(args) - 1):
            cypher = cypher + 'match (e1) -- (:entity{name:"%s"}) with e1 '
        cypher = (cypher + 'match (e1)-- (:entity{name:"%s"}) return distinct(e1.name)') % args
        data = self.graph.run(cypher).data()
        print(list(data))

    # 在指定层数关系中寻找e1和e2的公共交点
    def find_r_between_e1_e2(self, e1, e2, layers):
        res = set()
        for layer in range(layers):
            layer += 1
            cypher = 'match (e1:entity{name:"%s"}), (e2:entity{name:"%s"}) return (e1)-[*%d]-(e2)' % (e1, e2, layer)
            data = self.graph.run(cypher).evaluate()
            for d in data:
                # relationships = list()
                # for relationship in d.relationships:
                #     relationships.append(self.relationship2json(relationship))
                # res.append(res)
                for relationship in d.relationships:
                    res.add(self.relationship2json(relationship)['e1'])
        return {'ans': list(res)}

    # 模板问题0
    def find_pattern_0(self, entity, relation):
        answer = self.graph.run(
            "MATCH (e1)-[]->(b) where b.name = \"" + str(entity) + "\" with e1 match (e1)-[r:" + str(
                relation) + "]->(e2) return e1,r,e2").data()
        return self.data2json(answer)

    # 模糊搜索一
    def findOtherEntitiesBasedonAssumption(self, entity, relation):

        answer = self.graph.run("MATCH (n1)- [rel:" + str(relation) + "] -> (n2) where n1.name =~ '.*" + str(
            entity) + ".*'RETURN n1,rel,n2").data()

        return answer

    # 模糊搜索二
    def findOtherEntities2BasedonAssumption(self, entity, relation):
        print("MATCH (n1)- [rel:" + str(relation) + "] -> (n2) where n2.name =~ '.*" + str(
            entity) + ".*'RETURN n1,n2")
        answer = self.graph.run("MATCH (n1)- [rel:" + str(relation) + "] -> (n2) where n2.name =~ '.*" + str(
            entity) + ".*'RETURN n1,rel,n2").data()

        return answer

    # 根据两个实体查询它们之间的最短路径
    def findRelationByEntities(self, entity1, entity2):
        answer = self.graph.run("MATCH (a:entity{name:\"" + str(entity1) + "\"}),(b:entity{name:\"" + str(
            entity2) + "\"}) return (a)-[*2]-(b) as p").evaluate()
        # answer = self.graph.run("MATCH (p1:HudongItem {title:\"" + entity1 + "\"})-[rel:RELATION]-(p2:HudongItem{title:\""+entity2+"\"}) RETURN p1,p2").data()

        if (answer is None):
            answer = self.graph.run(
                "MATCH (a:entity{name:\"" + str(entity1) + "\"}),(b:entity{name:\"" + str(
                    entity2) + "\"}) return (a)-[*3]-(b) as p").evaluate()
        if (answer is None):
            answer = self.graph.run(
                "MATCH (a:entity{name:\"" + str(entity1) + "\"}),(b:entity{name:\"" + str(
                    entity2) + "\"}) return (a)-[*1]-(b) as p").evaluate()
        relationDict = []
        if (answer is not None):
            for x in answer:
                tmp = {}
                start_node = x.start_node
                end_node = x.end_node
                tmp['n1'] = start_node
                tmp['n2'] = end_node
                tmp['rel'] = x
                relationDict.append(tmp)
        return relationDict

    # 时间条件查询
    def findTheTime(self, entity, relation):
        print("MATCH (a)-[]->(b) where b.name = \"" + str(entity) + "\" with a match (a)-[rel:" + str(
            relation) + "]->(c) return a,rel,c")
        answer = self.graph.run(
            "MATCH (a)-[]->(b) where b.name = \"" + str(entity) + "\" with a match (a)-[rel:" + str(
                relation) + "]->(c) return a,rel,c").data()

        return answer

    # 将neo4j查询的data格式转化为json格式
    def data2json(self, data):
        if len(data) == 0:
            return None
        res = list()
        for item in data:
            e1 = item['e1']['name']
            r = type(item['r']).__name__
            e2 = item['e2']['name']
            res.append({
                'e1': e1,
                'r': r,
                'e2': e2
            })
        return res

    def relationship2json(self, relationship):
        e1 = relationship.start_node
        e2 = relationship.end_node
        r = type(relationship).__name__
        return {
            'e1': e1['name'],
            'r': r,
            'e2': e2['name']
        }


if __name__ == '__main__':
    neo4j = Neo4j("http://localhost:7474", "neo4j", "123456")
    neo4j.query_by_multi_condition('美国', '战斗机')
