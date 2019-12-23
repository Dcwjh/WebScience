import scrapy
import re
from military_crawler.items import Triple


class wikitable(scrapy.Spider):
    name = 'wikitable2'
    start_urls = [
        # 'https://wikipedia.hk.wjbk.site/baike-%E6%88%98%E4%BA%89%E5%88%97%E8%A1%A8_(1800%E5%B9%B4-1899%E5%B9%B4)'
        # 'https://wikipedia.hk.wjbk.site/baike-%E6%88%98%E4%BA%89%E5%88%97%E8%A1%A8_(1945%E5%B9%B4-1989%E5%B9%B4)'
    ]

    save_path = 'triples.csv'
    debug = 1

    def parse(self, response):
        table_list = response.xpath('//table[contains(@align,"center")]')
        for table in table_list:
            tr_list = table.xpath('.//tr')
            for tr in tr_list:
                if tr.xpath('./th'):
                    pass
                else:
                    td_list = tr.xpath('./td')
                    start_time = td_list[0].xpath('./text()').extract_first().strip()+'年'
                    finish_time = td_list[1].xpath('./text()').extract_first().strip()+'年'
                    war_name = td_list[2].xpath('./a/text()').extract_first().strip()
                    if td_list[3].xpath('.//a'):
                        p1 = '##'.join(td_list[3].xpath('./a/text()').extract()).strip()
                    else:
                        p1 = td_list[3].xpath('string(.)').extract_first().strip()
                    if td_list[4].xpath('.//a'):
                        p2 = '##'.join(td_list[4].xpath('./a/text()').extract()).strip()
                    else:
                        p2 = td_list[4].xpath('string(.)').extract_first().strip()
                    t1 = Triple()
                    t1['e1'] = war_name
                    t1['r'] = '开始时间'
                    t1['e2'] = start_time
                    yield t1

                    t2 = Triple()
                    t2['e1'] = war_name
                    t2['r'] = '结束时间'
                    t2['e2'] = finish_time
                    yield t2

                    t3 = Triple()
                    t3['e1'] = war_name
                    t3['r'] = '主要参战方1'
                    t3['e2'] = p1
                    if p1:
                        yield t3

                    t4 = Triple()
                    t4['e1'] = war_name
                    t4['r'] = '主要参展方2'
                    t4['e2'] = p2
                    if p2:
                        yield t4


