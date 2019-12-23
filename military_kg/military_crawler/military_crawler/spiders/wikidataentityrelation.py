import scrapy
import redis
import re
from military_crawler.items import WikiTripleItem


class WikiDataEntityRelation(scrapy.Spider):
    name = 'wiki_data_entity_relation'

    # start_urls = ['https://www.wikidata.org/wiki/Q5816']

    def start_requests(self):
        db_conn = redis.StrictRedis(host='localhost', port=6379, db=0)
        id_set = db_conn.smembers('wiki_entity_main_id')
        for id in id_set:
            entity_id = id.decode('utf8')
            url = 'https://www.wikidata.org/wiki/' + entity_id
            yield scrapy.Request(url, callback=self.parse)
        db_conn.connection_pool.disconnect()

    def parse(self, response):
        entity1_name = response.xpath('//*[@class="wikibase-title-label"]/text()').extract_first()
        if (entity1_name is None) or (entity1_name == 'No label defined'):
            return
        entity1_id = response.xpath('//*[@class="wikibase-title-id"]/text()').extract_first()
        entity1_id = re.sub(r'[\\(\\)]', '', entity1_id)
        statement_group = response.xpath(
            '//*[@class="wikibase-statementgrouplistview"]/div[@class="wikibase-listview"]')
        if statement_group:
            statements = statement_group[0].xpath('./div')
            for statement in statements:
                relation_name = statement.xpath(
                    './/div[@class="wikibase-statementgroupview-property"]//a/text()').extract_first()
                relation_id = statement.xpath(
                    './/div[@class="wikibase-statementgroupview-property"]//a/@href').extract_first()
                relation_id = relation_id.split(':')[1]
                entity2_list = statement.xpath('.//div[@class="wikibase-statementview-mainsnak"]')
                for entity2 in entity2_list:
                    entity2_title = entity2.xpath('.//div[@class="wikibase-snakview-body"]//a/@title')
                    if entity2_title:
                        entity2_id = entity2.xpath('.//a/@title').extract_first()
                        entity2_name = entity2.xpath('.//a/text()').extract_first()
                        wiki_triple = WikiTripleItem()
                        wiki_triple['entity1_id'] = entity1_id
                        wiki_triple['entity1_name'] = entity1_name
                        wiki_triple['relation_id'] = relation_id
                        wiki_triple['relation_name'] = relation_name
                        wiki_triple['entity2_id'] = entity2_id
                        wiki_triple['entity2_name'] = entity2_name
                        yield wiki_triple
