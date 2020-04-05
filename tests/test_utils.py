from scrapy_products.utils import TableHelper
from scrapy_products.spiders.amz import _AMZ_DOMAIN_TAB


class TestTableHelper:
    def test_lookup(self):
        helper = TableHelper(_AMZ_DOMAIN_TAB, "domain")
        assert "https://{dm}/s?k={kw}&ref=nb_sb_noss_1" ==  helper.lookup("amazon.ae", "search_fmt")
