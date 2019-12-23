import scrapy
import re
from military_crawler.items import WikiEntity


class ZhWiki(scrapy.Spider):
    name = 'zh_wiki'
    start_urls = ['https://wikipedia.hk.wjbk.site/baike-Category:各地军事']
    save_path = 'zh_wiki_org.json'
    depth_limit = 10

    def parse(self, response):
        # 若父类页面没有分配id，则默认设为0，表示最高父类
        if 'category_id' in response.meta:
            category_id = response.meta['category_id']
        else:
            category_id = '0'
        if 'depth' in response.meta:
            depth = response.meta['depth']
        else:
            depth = 0
        depth += 1
        category_name = response.xpath('//*[@id="firstHeading"]/text()').extract_first()
        category_name = category_name.split(':')[1]  # 获取类别名
        # 爬取子类
        sub_category_list = response.xpath(
            '//*[@id="mw-subcategories"]//div[@class="CategoryTreeItem"]//a/@href').extract()
        for index in range(len(sub_category_list)):
            if depth <= self.depth_limit:
                sub_category_id = category_id + "-" + str(index)  # 父类为子类分配id
                yield scrapy.Request(sub_category_list[index], callback=self.parse,
                                     meta={'category_id': sub_category_id, 'depth': depth})
        #  叶子节点，最终实体
        category_entity_list = response.xpath('//*[@id="mw-pages"]//li/a')
        for category_entity in category_entity_list:
            wiki_entity = WikiEntity()
            url = category_entity.attrib['href']
            name = category_entity.attrib['title']
            wiki_entity['categoryId'] = category_id
            wiki_entity['categoryName'] = category_name
            wiki_entity['url'] = url
            wiki_entity['name'] = name
            yield wiki_entity

    def parse_entity(self, response):
        title = response.xpath('//*[@id="firstHeading"]/text()').extract_first()
        pass
