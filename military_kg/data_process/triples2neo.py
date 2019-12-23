import pandas as pd
import csv

DEFAULT_SOURCE_CSV_COLS = ['e1', 'r', 'e2']  # 默认原始数据的三元组格式
DEFAULT_ENTITY_CSV_COLS = ['entityId:ID', 'name', ':LABEL']
DEFAULT_RELATION_CSV_COLS = [':START_ID', ':END_ID', ':TYPE']


# 将三元组存储到neo4j中
def csv2neo4j(csv_filename, cols=None):
    if cols is None:
        cols = DEFAULT_SOURCE_CSV_COLS
    print('三元组文件预处理开始...')
    csv_data = pd.read_csv(csv_filename, usecols=cols, quoting=csv.QUOTE_NONE)
    e1_set = set(csv_data['e1'].tolist())
    e2_set = set(csv_data['e2'].tolist())
    entity_set = e1_set.union(e2_set)

    # 为每个实体编号，生成entity.csv，且将id存到字典中
    file_entity = open('./final_data/entity.csv', 'w', newline='', encoding='utf8')
    csv_entity = csv.writer(file_entity)
    csv_entity.writerow(DEFAULT_ENTITY_CSV_COLS)
    index = 0
    entity_dict = dict()
    for entity in entity_set:
        csv_entity.writerow((index, str(entity), 'entity'))
        entity_dict[entity] = index
        index += 1
    file_entity.close()
    print('已生成实体文件')

    # 生成relation.csv
    csv_data[':START_ID'] = csv_data['e1'].map(entity_dict)
    csv_data[':END_ID'] = csv_data['e2'].map(entity_dict)
    csv_data[':TYPE'] = csv_data.pop('r')
    csv_data.to_csv('./final_data/relation.csv', columns=DEFAULT_RELATION_CSV_COLS, index=False)
    print('已生成关系文件')
    print('三元组文件预处理完成')
    print('Tips：下一步只需要用neo4j-admin指令导入新生成的两个csv文件即可（neo4j务必先关闭），其命令行格式为：')
    print('neo4j-admin import --nodes="entity.csv文件路径" --relationships="relation.csv文件路径" ')


def get_all_entity_name(entity_csv_file):
    csv_data = pd.read_csv(entity_csv_file, usecols=DEFAULT_ENTITY_CSV_COLS, quoting=csv.QUOTE_NONE)
    with open('entity.txt', 'w', encoding='utf8') as f:
        for e in csv_data['name']:
            f.write(str(e) + '\n')
    f.close()


if __name__ == '__main__':
    # csv2neo4j('./final_data/final_triples.csv')
    get_all_entity_name('./final_data/entity.csv')
