import scrapy
import re
from military_crawler.items import ZhWikiKeyword


# 基于中文维基的军事分类,爬取与军事相关的关键词,再利用互动百科和wikidata进行属性扩展
class zhwiki(scrapy.Spider):
    name = 'zhwiki3'
    limit_depth = 15  # 爬取的最大深度
    category_name = '各地军事人物'
    start_urls = ['https://wikipedia.hk.wjbk.site/baike-Category:%s' % category_name]
    save_path = '%s.txt' % category_name

    def parse(self, response):
        if 'depth' in response.meta:
            depth = response.meta['depth']
        else:
            depth = 0
        depth += 1
        if depth <= self.limit_depth:
            # 爬取子类
            sub_category_list = response.xpath(
                '//*[@id="mw-subcategories"]//div[@class="CategoryTreeItem"]//a')
            for index in range(len(sub_category_list)):
                sub_category_url = sub_category_list[index].xpath('./@href').extract_first()  # 子类链接
                yield scrapy.Request(sub_category_url, callback=self.parse,
                                     meta={'depth': depth})
            #  叶子节点，最终实体
            entity_list = response.xpath('//*[@id="mw-pages"]//li/a')
            for index in range(len(entity_list)):
                entity_name = entity_list[index].xpath('./@title').extract_first()
                entity_url = entity_list[index].xpath('./@href').extract_first()
                keyword = ZhWikiKeyword()
                entity_name = re.sub('\\(.*\\)', '', entity_name).strip()
                keyword['title'] = entity_name
                keyword['url'] = entity_url
                if 'Template' in entity_url or 'Portal' in entity_url:
                    pass
                else:
                    yield keyword
