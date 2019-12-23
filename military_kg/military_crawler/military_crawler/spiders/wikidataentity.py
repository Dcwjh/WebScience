import scrapy
import json
from military_crawler.items import WikiDataEntityItem
import redis


class WikiDataEntity(scrapy.Spider):
    name = "wiki_data_entity"

    def start_requests(self):
        db_conn = redis.StrictRedis(host='localhost', port=6379, db=0)
        id_set = db_conn.smembers('wiki_entity_id')
        for id in id_set:
            entity_id = id.decode('utf8')
            url = 'https://www.wikidata.org/wiki/Special:EntityData/' + entity_id + '.json'
            yield scrapy.Request(url, callback=self.parse, meta={'entity_id': entity_id})
        db_conn.connection_pool.disconnect()

    def parse(self, response):
        entity_id = response.meta['entity_id']

        res = json.loads(response.text)
        entity = res['entities'][entity_id]
        labels = entity['labels']
        descriptions = entity['descriptions']
        wiki_data_entity = WikiDataEntityItem()
        wiki_data_entity['entity_id'] = entity_id
        wiki_data_entity['entity_name_en'] = labels['en']['value'] if 'en' in labels else ''
        wiki_data_entity['entity_name_zh'] = labels['zh-cn']['value'] if 'zh-cn' in labels else ''
        wiki_data_entity['entity_desc_en'] = descriptions['en']['value'] if 'en' in descriptions else ''
        wiki_data_entity['entity_desc_zh'] = descriptions['zh-cn']['value'] if 'zh-cn' in descriptions else ''
        yield wiki_data_entity
