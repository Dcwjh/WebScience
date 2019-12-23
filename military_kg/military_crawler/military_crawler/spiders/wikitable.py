import scrapy
import re
from military_crawler.items import WikiTableTriple


class wikitable(scrapy.Spider):
    name = 'wikitable'
    start_urls = [
        'https://wikipedia.hk.wjbk.site/baike-%E7%AC%AC%E4%BA%8C%E6%AC%A1%E4%B8%96%E7%95%8C%E5%A4%A7%E6%88%B0%E9%A3%9B%E6%A9%9F%E5%88%97%E8%A1%A8']
    save_path = 'triples2.csv'
    debug = 0
    main_column = 0  # 主要条目
    invalid_columns = [3]  # 要废弃的条目
    invalid_vocabulary = ['', '不明', '─']
    my_dict = {}

    def parse(self, response):
        table_list = response.xpath('//table[contains(@class,"wikitable")]')
        for table in table_list:
            tr_list = table.xpath('.//tr')
            column_list = list()
            for tr in tr_list:
                row_list = list()
                if tr.xpath('./th'):
                    th_list = tr.xpath('./th/text()').extract()
                    for th in th_list:
                        th = th.strip()
                        column_list.append(th)
                else:
                    td_list = tr.xpath('./td')
                    for td in td_list:
                        if td.xpath('.//a'):
                            td_content = td.xpath('.//a/text()').extract()
                            td_content = '|'.join(td_content)
                        else:
                            td_content = td.xpath('./text()').extract_first()
                        row_list.append(td_content)
                        print(row_list)
                    main_entity = row_list[self.main_column]
                    for index in range(len(row_list)):
                        if index is not self.main_column and index not in self.invalid_columns:
                            e1 = main_entity
                            r = column_list[index]
                            e2 = row_list[index]
                            if e2 in self.invalid_vocabulary:
                                pass
                            else:
                                triple = WikiTableTriple()
                                triple['entity1'] = e1
                                triple['relation'] = r
                                triple['entity2'] = e2
                                yield triple
