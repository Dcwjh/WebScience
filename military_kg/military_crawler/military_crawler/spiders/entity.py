import scrapy
import re

from military_crawler.items import Keyword, Entity


# 根据之前爬到的一些关键词，基于互动百科爬取实体信息
class properties(scrapy.Spider):
    name = 'entity'
    allowed_domains = ['http://www.baike.com/']
    # start_urls = ['http://www.baike.com/wiki/毛泽东']
    property_name_pattern = re.compile('<strong>(.*?)：</strong>')
    property_value_pattern = re.compile('<span>.*?</span>')
    only_text_pattern = re.compile('>(.*?)<')
    remove_pattern = re.compile('[\n\t\r ]')
    save_path = 'hudong_pedia2.json'  # item保存路径
    keyword_file = 'E:\python_workspace\military_kg\military_crawler\military_crawler\keywords3.text'

    def start_requests(self):
        with open(self.keyword_file, 'r', encoding='utf8') as f:
            keyword = [line.rstrip('\n') for line in f]
        urls = ['http://www.baike.com/wiki/%s' % item for item in keyword]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        entity = Entity()
        name = response.xpath('//*[@class="content-h1"]/h1/text()').extract_first()  # 提取名称
        if name:  # 所搜索的条目存在
            entity['url'] = response.url
            entity['name'] = name
            summary = response.xpath('//*[@class="summary"]').xpath('string(.)').extract_first()  # 提取摘要/简介
            summary = re.sub(self.remove_pattern, '', summary)[0:-4]  # 去除“摘要编辑”四个字
            entity['summary'] = summary
            labels = response.xpath('//*[@id="openCatp"]/a/@title').extract()  # 提取类别
            entity['labelList'] = labels
            image = response.xpath('//*[@class="doc-img"]/a/img/@src').extract_first()  # 提取图片
            entity['image'] = image
            tds_list = response.xpath('//*[@id="datamodule"]//tr').extract()
            base_info_key_list = list()
            base_info_value_list = list()
            for td in tds_list:
                base_info_key = self.property_name_pattern.search(td).group(1)
                base_info_value = self.property_value_pattern.search(td).group(0)  # 先匹配到全局
                # 再去除标签，提取里面所有的文字
                a_text = self.only_text_pattern.findall(base_info_value)
                base_info_value = ''.join(a_text)
                base_info_key_list.append(base_info_key)
                base_info_value_list.append(base_info_value)
            entity['baseInfoKeyList'] = base_info_key_list
            entity['baseInfoValueList'] = base_info_value_list
            yield entity
        else:  # 若搜索条目不存在，则爬取返回的结果列表中的链接
            result_list = response.xpath('//*[@class="result-list"]/h3/a/@href').extract()
            for result in result_list:
                scrapy.Request(result, callback=self.parse)
        # nouns = self.ltputils.extract_noun(property_value)
        # if nouns is not None:
        #     for noun in nouns:
        #         keyword = Keyword()
        #         keyword['name'] = noun
        #         yield keyword
