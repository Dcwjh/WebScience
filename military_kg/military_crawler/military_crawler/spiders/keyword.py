import scrapy
import re

from military_crawler.items import Keyword


# 先基于一些小网站爬取有限的有关的军事关键词
class keyword(scrapy.Spider):
    name = 'keyword'
    start_urls = ['https://junshi.supfree.net/ouzhou.asp?zimu=%s&page=1' % chr(i) for i in range(65, 91)]
    name_pattern = re.compile('<a.*>(.*)</a>')
    num_pattern = re.compile('page=(\d+)')

    def parse(self, response):
        page_num_element = response.xpath('//*[@class="ulink"]/a[2]/@href').extract_first()
        page_num = int(self.num_pattern.search(page_num_element).group(1))
        for index in range(2, page_num + 1):
            next_page_url = self.num_pattern.sub('page=' + str(index), response.url)
            yield scrapy.Request(next_page_url, callback=self.parse_next)
        name_elements = response.xpath('//*[@id="content"]/div/div[2]/div[4]/h4').extract()
        for item in name_elements:
            name = self.name_pattern.search(item).group(1)
            keyword = Keyword()
            keyword['name'] = name
            yield keyword

    def parse_next(self, response):
        name_elements = response.xpath('//*[@id="content"]/div/div[2]/div[4]/h4').extract()
        for item in name_elements:
            name = self.name_pattern.search(item).group(1)
            keyword = Keyword()
            keyword['name'] = name
            yield keyword
