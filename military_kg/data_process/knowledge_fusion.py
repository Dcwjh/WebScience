"""
本模块为知识融合部分，即将多个数据源数据合并，进行实体对齐和关系对齐
目前采用的对齐方式为简单的字符串相似度匹配
"""
import pandas as pd
import csv
import os

DEFAULT_SOURCE_CSV_COLS = ['e1', 'r', 'e2']  # 默认原始数据的三元组格式
SIMILARITY_THRESHOLD = 0.95


def get_er_txt():
    df = pd.read_csv('./final_data/final_triples.csv', usecols=DEFAULT_SOURCE_CSV_COLS, quoting=csv.QUOTE_NONE)
    e1_set = set(df['e1'].tolist())
    e2_set = set(df['e2'].tolist())
    entity_set = e1_set.union(e2_set)
    r_set = set(df['r'].tolist())
    with open('e.txt', 'w', encoding='utf8') as f:
        for e in entity_set:
            f.write(str(e) + '\n')
    with open('r.txt', 'w', encoding='utf8') as f:
        for r in r_set:
            f.write(str(r) + '\n')


# 清洗数据
def clean_data(csv_file_list, cols=None):
    if cols is None:
        cols = DEFAULT_SOURCE_CSV_COLS
    count = len(csv_file_list)
    if count == 0:
        return
    print('开始清理数据...')
    for csv_file in csv_file_list:
        del_rows = list()  # 即将要删除的行
        df = pd.read_csv(csv_file, usecols=cols, quoting=csv.QUOTE_NONE)
        for index, row in df.iterrows():
            main_entity = row['e1']
            relation = row['r']
            sub_entity = row['e2']
            if main_entity and relation and sub_entity:
                pass
            else:
                del_rows.append(index)
        df.drop(index=del_rows, inplace=True)  # 按索引删除行
        df.reset_index(drop=True, inplace=True)  # 重新生成index
        df.to_csv(csv_file, index=False)
        print('清理掉%d条数据' % len(del_rows))


# 合并去重多个csv文件
def merge(csv_file_list, cols=None):
    if cols is None:
        cols = DEFAULT_SOURCE_CSV_COLS
    count = len(csv_file_list)
    if count == 0:
        return
    print('开始合并源数据文件...')
    # 合并csv文件
    df = None
    index = 1
    for csv_file in csv_file_list:
        df_tmp = pd.read_csv(csv_file, usecols=cols, quoting=csv.QUOTE_NONE)
        df = pd.concat([df, df_tmp], axis=0, ignore_index=True)
        print('已合并%d/%d' % (index, count))
        index += 1
    # 去重
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)  # 重新生成index
    df.to_csv('./final_data/triples.csv', index=False)
    print('合并完成')


# 利用字符串相似度做简单的实体关系融合
def fusion(csv_file, cols=None):
    if cols is None:
        cols = DEFAULT_SOURCE_CSV_COLS
    df = pd.read_csv(csv_file, usecols=cols, quoting=csv.QUOTE_NONE)
    print('开始生成实体关系映射表...')
    ere_dict = dict()  # 主实体及其关系映射表
    for index, row in df.iterrows():
        main_entity = row['e1']
        relation = row['r']
        sub_entity = row['e2']
        if main_entity not in ere_dict:
            ere_dict[main_entity] = dict()
            ere_dict[main_entity]['relationships'] = list()
            ere_dict[main_entity]['sub_entities'] = list()
            ere_dict[main_entity]['index'] = list()
        ere_dict[main_entity]['relationships'].append(relation)
        ere_dict[main_entity]['sub_entities'].append(sub_entity)
        ere_dict[main_entity]['index'].append(index)
    print('实体关系映射表已生成完毕,开始进行知识融合..')
    del_rows = list()  # 即将要删除的行
    # 遍历实体关系映射表，进行实体-关系相似度计算
    for key, value in ere_dict.items():
        index = value['index']
        relationships = value['relationships']
        sub_entities = value['sub_entities']
        for i in range(len(index)):
            if index[i] in del_rows:
                continue
            for j in range(i + 1, len(index)):
                rel_sim = similarity(str(relationships[j]), str(relationships[i]))
                ent_sim = similarity(str(sub_entities[j]), str(sub_entities[i]))
                if rel_sim >= SIMILARITY_THRESHOLD and ent_sim >= SIMILARITY_THRESHOLD:
                    e1 = (index[j], key, relationships[j], sub_entities[j])
                    e2 = (index[i], key, relationships[i], sub_entities[i])
                    del_rows.append(index[j])
                    print('发现可融合知识：' + str(e1) + '###' + str(e2))
    df.drop(index=del_rows, inplace=True)  # 按索引删除行
    df.reset_index(drop=True, inplace=True)  # 重新生成index
    df.to_csv('./final_data/final_triples.csv', index=False)
    print('知识融合完成，去除%d个三元组关系' % len(del_rows))


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


if __name__ == '__main__':
    # 获取data目录下所有的csv文件
    path = './data'
    csv_filename_list = os.listdir(path)
    csv_file_path = [path + '/' + filename for filename in csv_filename_list]
    # 先清晰数据
    # clean_data(csv_file_path)
    # merge(csv_file_path)
    # 对最后的csv文件进行知识融合
    fusion('./final_data/triples.csv')
