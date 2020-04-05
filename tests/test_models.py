import scrapy
import os.path as pth
from scrapy.loader import ItemLoader 
from scrapy.selector import Selector
from scrapy_products.models import ( ChainedLoader , CSVPagesIter)

import pytest


_BOOK_STORE = """
<?xml version="1.0" encoding="UTF-8"?>

<bookstore>

<site>
Star Avenue
</site>

<book>
  <title lang="en">Learning XML</title>
  <price>39.95</price>
</book>


<book>
  <title lang="en">Harry Potter</title>
  <price>29.99</price>
  <ratings>211</ratings>
</book>

</bookstore> 
"""

class Product(scrapy.Item):
    name=scrapy.Field()
    ratings=scrapy.Field()


class TestCSVPagesIter:
    def test_basic(self):
        _ASINS = pth.join(pth.dirname(__file__), "asins_demo.csv")
        it = CSVPagesIter(_ASINS, lambda r:r["asin"])
        for wp in it:
            print("WebPage:url={}, auxs={}".format(wp.url, wp.auxiliaries))


class TestChainedLoader:
    def create_loader(self, xpath="//book"):
        # Note: set text of <body>..</body>
        loader = ItemLoader(item=Product(), selector=Selector(text=_BOOK_STORE))
        return ChainedLoader.chain_nested(loader, xpath)


    def test_chained_one_node(self):
        chained = self.create_loader("//site")
        assert chained.dim == 1
        

    def test_add_xpath(self):
        chained = self.create_loader()
        chained.add_xpath("ratings", "ratings/text()")
        ratings = chained.load_item()["ratings"]
        assert ratings == ["", "211"]


    def test_add_value(self):
        chained = self.create_loader()
        chained.add_value("name", "Charlie")
        names = chained.load_item()["name"]
        assert names == ["Charlie", "Charlie"]


    def test_load_item(self):
        loader = ItemLoader(item=Product(), selector=Selector(text=_BOOK_STORE))
        loader.add_value("name", "Three Body")
        loader2 = ItemLoader(item=Product(), selector=Selector(text=_BOOK_STORE))
        loader.add_value("ratings", 166)
        ch = ChainedLoader.chain(loader, loader2)
        ch.set_united_item(["name", "ratings"])
        it = ch.load_item()
        assert "name" in it and it["name"][0] == "Three Body"
        assert "ratings" in it and it["ratings"][0] == 166
