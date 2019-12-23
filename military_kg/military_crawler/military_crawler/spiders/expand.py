import scrapy
import re
from military_crawler.items import Triple


# 通过互动百科进行实体属性扩展
class Expand(scrapy.Spider):
    name = 'expand'
    debug = 1
    allowed_domains = ['www.baike.com']
    only_text_pattern = re.compile('>(.*?)<')
    save_path = '武器库.csv'
    threshold = 0.3

    def start_requests(self):
        with open('E:\python_workspace\military_kg\military_crawler\data.csv', 'r', encoding='utf8') as f:
            for line in f.readlines():
                triple = line.strip().split(',')
                e1 = triple[0]
                # e2 = triple[2]
                # e2_list = e2.split('、')
                yield scrapy.Request('http://www.baike.com/wiki/%s' % e1, callback=self.parse, meta={'title': e1})
                # for e in e2_list:
                #     yield scrapy.Request('http://www.baike.com/wiki/%s' % e, callback=self.parse,
                #                          meta={'title': e})
                # yield scrapy.Request('http://www.baike.com/wiki/毛泽东', callback=self.parse, meta={'title': '毛泽东'})

    def parse(self, response):
        title = response.meta['title']
        name = response.xpath('//*[@class="content-h1"]/h1/text()').extract_first()  # 提取名称
        # 相似度比较
        if name:
            label_list = response.xpath('//*[@id="openCatp"]/a/@title').extract()  # 提取互动百科所分配的类别
            for label in label_list:
                triple = Triple()
                triple['e1'] = title
                triple['r'] = '属于'
                triple['e2'] = label
                yield triple

            td_list = response.xpath('//*[@id="datamodule"]//td')
            for td in td_list:
                if td.xpath('./strong') and td.xpath('./span'):
                    key = td.xpath('./strong').xpath('string(.)').extract_first()[0:-1].strip().replace(' ', '')
                    value = ''
                    for span in td.xpath('./span'):
                        value += span.xpath('string(.)').extract_first().strip().replace(' ', '')
                    triple = Triple()
                    triple['e1'] = title
                    triple['r'] = key
                    triple['e2'] = value
                    yield triple
        else:
            pass
