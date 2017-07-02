# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ViolinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()

class MasterItem(scrapy.Item):
    sky_40 = scrapy.Field()
    sky = scrapy.Field()
    serial = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()

