import re
from scrapy.loader import ItemLoader
from .items import (
ListingsItem,
OrganicItem
)
from abc import abstractmethod

import scrapy.loader.processors as processors

def regextract(regex=None, group=0):
    def _regextrat(string, regex=regex, group=group):
        return re.search(regex, string).group(group) if string else None

    return _regextrat


def join_strip():
    return processors.Compose(processors.Join(), str.strip)


def join_strip_regextract(re, gp=0):
    return processors.Compose(processors.Join(), str.strip, regextract(re,gp))




class BasicLoader(ItemLoader):
    @abstractmethod
    def lead(self):
        pass


class ListingsLoader(BasicLoader):
    def __init__(self, response, **kwargs):
        super(ListingsLoader, self).__init__(ListingsItem(), response = response, **kwargs)


class OrganicLoader(BasicLoader):
    def __init__(self, response, **kwargs):
        super(BasicLoader, self).__init__(OrganicItem(), response = response, **kwargs)

    def lead(self):
        XPATH_NEXT = "//li[@class='a-last']/a/@href"
#        XPATH_PRODUCTS = "//div[contains(@class, 's-result-list s-search-results')]/div[@data-asin]"

#        # relative xpaths
#        XPATH_ASIN = '@data-asin'
#        XPATH_INDEX = '@data-index'
        XPATH_ASIN = "//div[contains(@class, 's-result-list s-search-results')]/div[@data-asin]/@data-asin"
        XPATH_INDEX = "//div[contains(@class, 's-result-list s-search-results')]/div[@data-asin]/@data-index"


#        products_loader = self.nested_xpath(XPATH_PRODUCTS)
#        products_loader.add_xpath("asin", XPATH_ASIN)
#        products_loader.add_xpath("index", XPATH_INDEX)

        self.add_xpath("asin",XPATH_ASIN)
        self.add_xpath("index",XPATH_INDEX)
        self.add_xpath("next_page", XPATH_NEXT, join_strip())
