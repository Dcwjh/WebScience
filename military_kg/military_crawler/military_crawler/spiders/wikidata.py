import scrapy
import json
from military_crawler.items import WikiEntityItem, WikiTripleId


class WikiData(scrapy.Spider):
    name = "wiki_data"
    save_path = 'triples.json'

    def start_requests(self):
        # with open('hudong_pedia.json', encoding='utf8') as f:
        #     for line in f.readlines():
        #         obj = json.loads(line.strip('\n'))
        #         url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=" + \
        #               obj['name']
        #         yield scrapy.Request(url, callback=self.parse)
        # with open('E:\\python_workspace\\military_kg\\military_crawler\\keyword.txt', encoding='utf8') as f:
        #     for line in f.readlines():
        #         keyword = line.strip('\n')
        #         url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=" + keyword
        #         yield scrapy.Request(url, callback=self.parse)
        with open('military.json', encoding='utf8') as f:
            for line in f.readlines():
                obj = json.loads(line.strip('\n'))
                url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=" + \
                      obj['名称']
                yield scrapy.Request(url, callback=self.parse)
        # with open('zh_wiki_org.json', encoding='utf8') as f:
        #     for line in f.readlines():
        #         obj = json.loads(line.strip('\n'))
        #         url = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=" + \
        #               obj['name']
        #         yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        res = json.loads(response.text)
        search_list = res['search']
        if search_list is not None:
            for item in search_list:
                entity = WikiEntityItem()
                entity['entity_id'] = item['id']
                # entity['entity_aliases'] = item['aliases']
                # entity['entity_description'] = item['description']
                entity['entity_label'] = item['label']
                entity['entity_concept_url'] = item['concepturi']
                url = 'https://www.wikidata.org/wiki/' + entity['entity_id']
                yield scrapy.Request(url, callback=self.parse_entity_page, meta={'entity_id': entity['entity_id']})

    def parse_entity_page(self, response):
        entity_name = response.xpath('//*[@class="wikibase-title-label"]/text()').extract_first()
        if (entity_name is None) or (entity_name == 'No label defined'):
            return
        entity_id = response.meta['entity_id']
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
                    # 若该实体有链接
                    # entity2_img = entity2.xpath('.//a[contains(@class,"img")]')
                    # entity2_external = entity2.xpath('.//a[contains(@class,"external")]')
                    entity2_a = entity2.xpath('.//div[@class="wikibase-snakview-body"]//a/@title')
                    # if entity2_img:
                    #     entity2_id = 'img'
                    #     entity2_name = entity2.xpath('.//a/@href').extract_first()
                    # if entity2_external:
                    #     entity2_id = 'category'
                    #     entity2_name = entity2.xpath('.//a/text()').extract_first()
                    #     print((entity2_id, entity2_name))
                    # else:
                    if entity2_a:
                        entity2_id = entity2.xpath('.//a/@title').extract_first()
                        entity2_name = entity2.xpath('.//a/text()').extract_first()
                        wiki_triple_id = WikiTripleId()
                        wiki_triple_id['entity1_id'] = entity_id
                        wiki_triple_id['relation_id'] = relation_id
                        wiki_triple_id['entity2_id'] = entity2_id
                        yield wiki_triple_id
                        # print((entity_id, entity_name, relation_id, relation_name, entity2_id, entity2_name))
                    # else:
                    #     entity2_id = 'num'
                    #     entity2_name = entity2.xpath('./text()').extract_first()
                    #     print(entity_name)
                    #     print(response.url)
                    # wiki_triple_id = WikiTripleId()
                    # wiki_triple_id['entity1_id'] = entity_id
                    # wiki_triple_id['relation_id'] = relation_id
                    # wiki_triple_id['entity2_id'] = entity2_id
                    # print((entity_id, entity_name, relation_id, relation_name, entity2_id, entity2_name))

    def parse_entity_zh(self, response):
        pass
