# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ListingsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    ratings = scrapy.Field()
    nratings = scrapy.Field()
    bsrb = scrapy.Field()
    bsrn = scrapy.Field()
    keywords = scrapy.Field() # auto-generated field
    asin = scrapy.Field() # auto-generated field


class OrganicItem(scrapy.Item):
    keywords = scrapy.Field()
    asin = scrapy.Field()
    index = scrapy.Field()
    next_page = scrapy.Field()
