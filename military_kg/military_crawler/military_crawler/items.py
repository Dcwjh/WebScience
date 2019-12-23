# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Triple(scrapy.Item):
    e1 = scrapy.Field()
    r = scrapy.Field()
    e2 = scrapy.Field()

class Keyword(scrapy.Item):
    name = scrapy.Field()


class Entity(scrapy.Item):
    url = scrapy.Field()  # 互动百科链接
    name = scrapy.Field()  # 实体名称
    summary = scrapy.Field()  # 实体简介
    image = scrapy.Field()  # 实体图片
    labelList = scrapy.Field()  # 实体类别
    baseInfoKeyList = scrapy.Field()  # 实体属性名
    baseInfoValueList = scrapy.Field()  # 实体属性值


class ZhWikiKeyword(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()





class ZhWikiEntity(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    label = scrapy.Field()
    category = scrapy.Field()
    type = scrapy.Field()


# wiki实体类
class WikiEntity(scrapy.Item):
    categoryId = scrapy.Field()  # 类别id
    categoryName = scrapy.Field()  # 类别名称
    url = scrapy.Field()  # 实体链接
    name = scrapy.Field()  # 实体名称


class WikiRelationItem(scrapy.Item):
    relation_id = scrapy.Field()
    mainCategory = scrapy.Field()
    subCategory = scrapy.Field()
    relation_name_en = scrapy.Field()
    relation_name_zh = scrapy.Field()
    relation_desc = scrapy.Field()


class WikiEntityItem(scrapy.Item):
    entity_id = scrapy.Field()
    entity_aliases = scrapy.Field()
    entity_description = scrapy.Field()
    entity_label = scrapy.Field()
    entity_concept_url = scrapy.Field()


class WikiTripleItem(scrapy.Item):
    entity1_id = scrapy.Field()
    entity1_name = scrapy.Field()
    relation_id = scrapy.Field()
    relation_name = scrapy.Field()
    entity2_id = scrapy.Field()
    entity2_name = scrapy.Field()


class WikiTripleId(scrapy.Item):
    entity1_id = scrapy.Field()
    relation_id = scrapy.Field()
    entity2_id = scrapy.Field()


class WikiDataEntityItem(scrapy.Item):
    entity_id = scrapy.Field()
    entity_name_en = scrapy.Field()
    entity_name_zh = scrapy.Field()
    entity_desc_en = scrapy.Field()
    entity_desc_zh = scrapy.Field()


class WikiTableTriple(scrapy.Item):
    entity1 = scrapy.Field()
    relation = scrapy.Field()
    entity2 = scrapy.Field()