# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CarAndGirlItem(scrapy.Item):
    """
    定义图组名字和图片地址
    """
    group_name = scrapy.Field()
    image_urls = scrapy.Field()
