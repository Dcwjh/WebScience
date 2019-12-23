import scrapy


class zhwiki2(scrapy.Spider):
    name = 'zhwiki2'
    start_urls = ['https://wikipedia.hk.wjbk.site/baike-Category:军事']
    depth_limit = 10

    def parse(self, response):
        labels = response.xpath('//*[@id="mw-subcategories"]//div[@class="CategoryTreeItem"]//a')
        for index in range(len(labels)):
            label = labels[index].xpath('./text()').extract_first()
            entity_url = labels[index].xpath('./@href').extract_first()
            entity_id = '0-c' + str(index)
            print("实体：" + ','.join((entity_id, label, '军事')))
            print("关系：" + ','.join((entity_id, 0, 'subclass')))
            yield scrapy.Request(entity_url, callback=self.parse_entity,
                                 meta={'label': label, 'entity_id': entity_id, 'depth': 0})

    def parse_entity(self, response):
        father_id = response.meta['entity_id']
        label = response.meta['label']
        depth = response.meta['depth']
        depth += 1

        if depth <= self.depth_limit:
            # 爬取子类
            sub_category_list = response.xpath(
                '//*[@id="mw-subcategories"]//div[@class="CategoryTreeItem"]//a')
            for index in range(len(sub_category_list)):
                sub_category_id = father_id + "-c" + str(index)  # 父类为子类分配id

                sub_category_name = sub_category_list[index].xpath('./text()').extract_first()  # 子类名称
                sub_category_url = sub_category_list[index].xpath('./@href').extract_first()  # 子类链接
                print("实体：" + ','.join((sub_category_id, sub_category_name, label)))
                print("关系：" + ','.join((sub_category_id, father_id, 'subclass')))
                yield scrapy.Request(sub_category_url, callback=self.parse_entity,
                                     meta={'label': label, 'entity_id': sub_category_id, 'depth': depth})
            #  叶子节点，最终实体
            category_entity_list = response.xpath('//*[@id="mw-pages"]//li/a')
            for index in range(len(category_entity_list)):
                category_entity_id = father_id + "-e" + str(index)
                category_entity_name = category_entity_list[index].xpath('./@title').extract_first()
                print("实体：" + ','.join((category_entity_id, category_entity_name, label)))
                print("关系：" + ','.join((category_entity_id, father_id, 'subclass')))