import scrapy
from military_crawler.items import WikiRelationItem
import json

class WikiRelation(scrapy.Spider):
    name = 'wiki_relation'
    start_urls = ['https://www.wikidata.org/wiki/Wikidata:List_of_properties/Summary_table']
    save_path = 'wiki_relation.json'

    def parse(self, response):
        # 主要类别：Generic,Person,Organization,Events,Works,Terms,Geographical feature,Others
        main_category_list = response.xpath('//h3/span[@class="mw-headline"]/text()').extract()
        # 由于子类别规则不固定，这里手动统计每个大类下子类个数
        sub_category_limit_list = [5, 7, 9, 2, 14, 20, 13, 5]
        sub_category_list = response.xpath('//table[@class="wikitable"]')  # 所有子类
        main_category_count = 0  # 对主类计数
        sub_category_count = 0  # 对子类计数
        for sub_category_item in sub_category_list:
            sub_category_limit = sub_category_limit_list[main_category_count]  # 获取对应主类的子类上限
            main_category = main_category_list[main_category_count]  # 对应主类名称
            sub_category = sub_category_item.xpath('.//th/text()').extract_first()
            sub_category = sub_category.replace("\n", "")  # 子类名称

            sub_category_count += 1
            if sub_category_count >= sub_category_limit:
                # 若子类数目达到上限，重新计数，主类切换至下一个
                sub_category_count = 0
                main_category_count += 1

            # 去除无用的子类
            if (main_category == 'Organization' and sub_category == 'Generic') or (
                    main_category == 'Works' or sub_category == 'Film'):
                continue

            wiki_relation_list = sub_category_item.xpath('.//td//li/a')  # 获取子类下所有关系列表
            for wiki_relation_item in wiki_relation_list:
                relation = WikiRelationItem()
                relation_id = wiki_relation_item.xpath('./@title').extract_first()
                relation_id = relation_id.split(':')[1]
                relation_name_en = wiki_relation_item.xpath('.//text()').extract_first().strip()
                relation['relation_id'] = relation_id
                relation['mainCategory'] = main_category
                relation['subCategory'] = sub_category
                relation['relation_name_en'] = relation_name_en
                # 访问新的url,将关系名称有中文转为英文
                relation_json_url = 'https://www.wikidata.org/wiki/Special:EntityData/' + relation_id + '.json'
                yield scrapy.Request(relation_json_url, callback=self.parse_relation_page, meta={'relation': relation})

    # 获取relation对应的中文名字
    def parse_relation_page(self, response):
        relation = response.meta['relation']
        relation_id = relation['relation_id']
        res = json.loads(response.text)
        entity = res['entities'][relation_id]
        labels = entity['labels']
        descriptions = entity['descriptions']
        if 'zh-cn' in labels:
            relation['relation_name_zh'] = labels['zh-cn']['value']
        else:
            relation['relation_name_zh'] = ''
        if 'zh-cn' in descriptions:
            relation['relation_desc'] = descriptions['zh-cn']['value']
        else:
            relation['relation_desc'] = ''
        yield relation
