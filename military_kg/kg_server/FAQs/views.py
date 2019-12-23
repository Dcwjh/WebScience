from django.shortcuts import render, redirect
from django.http import HttpResponse
import re
from tools.utils import pku, ltp, neo4j, entities, relations
from tools.chn_to_sum import chn_to_sum
import json

# 问题模板
pattern = [
    ['(.*)大于(.*)的(.*)有哪些', '(.*)[小于|<](.*)的(.*)有哪些', '(.*)[大于等于|>=|不低于|不少于](.*)的(.*)有哪些',
     '(.*)[小于等于|<=|不超过|不多于](.*)的(.*)有哪些'],
    ['(.*)有多少艘(.*)', '(.*)有多少(.*)']
    # [r"最近", "\d+\.?\d*年到\d+\.?\d*", r"\d+\.?\d*年-\d+\.?\d*", r"\d+\.?\d*年- \d+\.?\d*", r"\d+\.?\d*-\d+\.?\d*",
    #  r"\d+\.?\d*- \d+\.?\d*", r"\d+\.?\d*到\d+\.?\d*", r"\d+\.?\d*[到现在|到今天|至今]", r"\d+\.?\d*年[到现在|到今天|至今]"]
]


def index(request):
    return render(request, "index.html")


def kg(request):
    return render(request, 'kg.html')


def kg_search(request):
    keyword = request.GET['keyword']
    return redirect('../kg/?keyword=%s' % keyword)


def show(request):
    keyword = request.GET['keyword']
    answer = neo4j.find_ere_by_e1(keyword)
    print(answer)
    if answer:
        return HttpResponse(json.dumps({'ans': answer}, ensure_ascii=False),
                            content_type="application/json,charset=utf-8")
    return HttpResponse("没有找到关键词的相关信息")


def search(request):
    question = request.GET['question']
    answer = question_answering(question)
    return HttpResponse(json.dumps(answer, ensure_ascii=False), content_type="application/json,charset=utf-8")


def question_answering(question):
    print("用户问题：" + question)
    flag = False  # 判断问题是否已经回答了
    words = pku.cut(question)
    print("分词结果：" + str(words))

    entity_list = []
    relation_list = []
    for word in words:
        if word in entities:
            entity_list.append(word)
            continue
        if word in relations:
            relation_list.append(word)
    n_words = entity_list + relation_list
    print("识别出的实体名称：" + str(entity_list))
    print("识别出的关系名称：" + str(relation_list))

    postags = ltp.postag(words)
    print("词性分析结果：" + str(list(postags)))

    parsers = ltp.parse(words, postags)
    print("词性依赖分析结果：" + str(parsers))

    print("尝试进行模板匹配...")
    for i in range(len(pattern)):
        result = []
        for x in pattern[i]:
            res = re.search(x, question)
            if i == 0 and res:
                print("该问题匹配到第%d类问题" % i)
                n1 = res.group(1)
                n2 = res.group(2)
                n3 = res.group(3)
                print(data_process(n2))
                tmp = chn_to_sum(data_process(n2))
                print("提取的信息为：" + str((n1, n2, n3)))
                ans = neo4j.find_pattern_0(n3, n1)
                for each in ans:
                    tmp1 = float(data_process(each['e2']))
                    if tmp1 > tmp:
                        str1 = str(each['e1'])
                        if str1 not in result:
                            result.append(str1)
                if result:
                    flag = True
                    return {'ans': result}
            if i == 1 and res:
                print("该问题匹配到第%d类问题" % i)
                n1 = res.group(1)
                n2 = res.group(2)
                print("提取的信息为：" + str((n1, n2)))
                res = neo4j.find_r_between_e1_e2(n1, n2, 2)
                if res:
                    result = len(res['ans'])
                    flag = True
                    return {'ans': list().append(result)}

    if len(n_words) == 1:  # 只有一个名词
        if len(entity_list) == 1:
            res = neo4j.find_ere_by_e1(n_words[0])
            print(res)
        else:
            res = neo4j.find_ere_by_r(n_words[0])
            print(res)
    elif len(n_words) > 1:  # 多个名词
        parsers = ltp.parse(words, postags)
        for i in range(len(parsers)):
            if parsers[i][0] == 'HED':
                main_entity = None
                if postags[i] is 'v':
                    for parser in parsers:
                        if parser[0] == 'SBV' and parser[2] == words[i]:
                            main_entity = parser[1]
                            if words[i] in relation_list:
                                all = neo4j.find_ere_by_e1(main_entity)
                                for ere in all:
                                    if similarity(ere['r'], words[i]) > 0.3:
                                        flag = True
                                        return ere
                            else:
                                for sub_entity in n_words:
                                    if sub_entity is not main_entity:
                                        if sub_entity in entity_list:
                                            res = neo4j.find_r_between_e1_e2(main_entity, sub_entity, 2)
                                            return res
                                        else:
                                            res = neo4j.find_e2_by_e1r(main_entity, sub_entity)
                                            return res
                            break
                else:
                    main_entity = parsers[i][1]
                    if main_entity in entity_list:
                        for sub_entity in n_words:
                            if sub_entity is not main_entity:
                                if sub_entity in entity_list:
                                    res = neo4j.find_r_between_e1_e2(main_entity, sub_entity, 2)
                                    return res
                                else:
                                    res = neo4j.find_e2_by_e1r(main_entity, sub_entity)
                                    return res
                    else:
                        for sub_entity in n_words:
                            if sub_entity is not main_entity:
                                res = neo4j.find_e2_by_e1r(sub_entity, main_entity)
                                ans = list()
                                for item in res:
                                    ans.append(item['e2'])
                                return {'ans': ans}
    if flag is False:
        return "抱歉，您的问题尚未找到最佳答案"


# 编辑距离求得字符串相似度
def similarity(str1, str2):
    # 构建编辑矩阵,并初始化
    edit = [[i + j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]

    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                d = 0
            else:
                d = 1
            edit[i][j] = min(edit[i - 1][j] + 1, edit[i][j - 1] + 1, edit[i - 1][j - 1] + d)
    return 1 - edit[len(str1)][len(str2)] / max(len(str1), len(str2))


def data_process(str1):
    parts = re.split(r'，|吨', str1)
    if len(parts) == 2:
        return parts[0]
    else:
        return int(parts[0]) * 1000 + int(parts[1])
