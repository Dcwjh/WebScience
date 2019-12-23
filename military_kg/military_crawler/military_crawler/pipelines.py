# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql
from redis import *
from military_crawler.items import WikiTripleId, WikiTripleItem, ZhWikiKeyword, WikiTableTriple,Triple
import zhconv


class MilitaryCrawlerPipeline(object):

    def open_spider(self, spider):
        if spider.debug:
            self.file = open(spider.save_path, 'a', encoding='utf-8')

    def close_spider(self, spider):
        if spider.debug:
            self.file.close()

    def process_item(self, item, spider):
        if spider.debug:
            if isinstance(item, ZhWikiKeyword):
                line = zhconv.convert(item['title'], 'zh-hans') + ',' + item['url'] + '\n'
                self.file.write(line)
            elif isinstance(item, WikiTableTriple):
                line = item['entity1'] + ',' + item['relation'] + ',' + item['entity2'] + '\n'
                line = zhconv.convert(line, 'zh-hans')
                self.file.write(line)
            elif isinstance(item, Triple):
                line = item['e1'] + ',' + item['r'] + ',' + item['e2'] + '\n'
                line = zhconv.convert(line, 'zh-hans')
                self.file.write(line)
            else:
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"  # 注意编码问题
                self.file.write(line)
        return item


class RedisPipeline(object):
    def open_spider(self, spider):
        db_host = spider.settings.get('REDIS_HOST')
        db_port = spider.settings.get('REDIS_PORT')
        db_index = spider.settings.get('REDIS_DB_INDEX')
        self.db_conn = StrictRedis(host=db_host, port=db_port, db=db_index)

    def close_spider(self, spider):
        self.db_conn.connection_pool.disconnect()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        if isinstance(item, WikiTripleId):
            entity1_id = item['entity1_id']
            entity2_id = item['entity2_id']
            self.db_conn.sadd('wiki_entity_main_id', entity1_id)
            self.db_conn.sadd('wiki_entity_id', entity1_id, entity2_id)


class MySQLPipeline(object):
    def open_spider(self, spider):
        host = spider.settings.get('MYSQL_HOST')
        port = spider.settings.get('MYSQL_PORT')
        user = spider.settings.get('MYSQL_USER')
        passwd = spider.settings.get('MYSQL_PASSWORD')
        db = spider.settings.get('MYSQL_DB_NAME')
        self.db_conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        if isinstance(item, WikiTripleItem):
            values = (
                item['entity1_id'], item['entity1_name'], item['relation_id'], item['relation_name'],
                item['entity2_id'], item['entity2_name'])
            sql = 'insert into wiki_data_entity_relation(entity1_id,entity1_name,relation_id,relation_name,entity2_id,entity2_name) values(%s,%s,%s,%s,%s,%s)'
        else:
            values = (item['entity_id'], item['entity_name_en'], item['entity_name_zh'], item['entity_desc_en'],
                      item['entity_desc_zh'])
            sql = 'insert into wiki_data_entity(wiki_entity_id,wiki_entity_name_en,wiki_entity_name_zh,wiki_entity_desc_en,wiki_entity_desc_zh) values(%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)
        self.db_conn.commit()
