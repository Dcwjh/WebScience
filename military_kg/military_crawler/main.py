from scrapy.cmdline import execute
import sys
import os

# 获取到当前目录，方便后面cmd命令运行不必去找目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 测试目录获取是否正确
# print(os.path.dirname(os.path.abspath(__file__)))
# 调用命令运行爬虫
# execute(["scrapy", "crawl", "keyword"])
# execute(["scrapy", "crawl", "entity"])
# execute(["scrapy", "crawl", "zh_wiki"])
# execute(["scrapy", "crawl", "wiki_relation"])
# execute(["scrapy", "crawl", "wiki_data"])
# execute(["scrapy", "crawl", "wiki_data_entity"])
# execute(["scrapy", "crawl", "wiki_data_entity_relation"])
# execute(["scrapy", "crawl", "zhwiki3"])
# execute(["scrapy", "crawl", "wikitable"])
execute(["scrapy", "crawl", "expand"])

