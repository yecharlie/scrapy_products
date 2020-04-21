# -*- coding: utf-8 -*-
import scrapy

from scrapy.loader import ItemLoader
from scrapy_products.spiders.basic_products import BasicProductsSpider
from scrapy_products.models import (
    CSVPagesIter,
    ChainedLoader
)

from scrapy_products.utils import (
        create_item_class,
        join_strip,
        join_strip_extdigits
)
import scrapy_products.utils.padding_dict as padding_dict 

# WARNING: all the layouts are tested on limited categories

_JP_LISTINGS_XPATHS = {
        "title" : "//h1[@id='title']/span/text()",
        "broad_bsr" : "//tr[@id='SalesRank']/td[@class='value']/text()[1]",
        "narrow_bsr" : "//tr[@id='SalesRank']//span[@class='zg_hrsr_rank']/text()",
        "ratings" : "//div[@id='averageCustomerReviews_feature_div']//span[@class='a-icon-alt']/text()",
        "nratings" : "//div[contains(@class, 'averageStarRatingNumerical')]/span/text()"
}

_AE_LISTINGS_XPATHS = {
        "title" : "//h1[@id='title']/span/text()",
        "broad_bsr" :  "//li[@id='SalesRank']/text()[2]",
        "narrow_bsr" : "//li[@id='SalesRank']//span[@class='zg_hrsr_rank']/text()",
        "ratings" : "//div[@id='averageCustomerReviews_feature_div']//span[@class='a-icon-alt']/text()",
        "nratings" : "//div[@id='averageCustomerReviews_feature_div']//span[@id='acrCustomerReviewText']/text()"
}

_AE_LISTINGS_XPATHS2 = {
        "broad_bsr" : "//tr[@id='SalesRank']/td[@class='value']/text()[1]",
        "narrow_bsr" : "//tr[@id='SalesRank']//span[@class='zg_hrsr_rank']/text()",
}

_US_LISTINGS_XPATHS = {
        "title" : "//h1[@id='title']/span/text()",
        "broad_bsr" : "//tr[contains(th/text(), 'Best Sellers Rank')]/td/span/span[1]/text()",
        "narrow_bsr" : "//tr[contains(th/text(), 'Best Sellers Rank')]/td/span/span[2]/text()",
        "ratings" : "//tr[contains(th/text(), 'Customer Reviews')]/td/text()",
        "nratings" : "//tr[contains(th/text(), 'Customer Reviews')]/td//span[@id='acrCustomerReviewText']/text()"
}

_DE_LISTINGS_XPATH = {
        "title" : "//h1[@id='title']/span/text()",
        "broad_bsr" :  "//li[@id='SalesRank']/text()[1]",
        "narrow_bsr" : "//li[@id='SalesRank']//span[@class='zg_hrsr_rank']/text()",
        "ratings":"//span[@data-hook='rating-out-of-text']/text()",
        "nratings":"//div[@data-hook='total-review-count']/span/text()"
}

_IT_LISTINGS_XPATH = {
        "title" : "//h1[@id='title']/span/text()",
        "broad_bsr":"//tr[@id='SalesRank']//td[2]/text()[1]",
        "narrow_bsr":"//tr[@id='SalesRank']//span[@class='zg_hrsr_rank']/text()",
        "ratings":"//span[@data-hook='rating-out-of-text']/text()",
        "nratings":"//div[@data-hook='total-review-count']/span/text()"
}

class AmzListingsIter(CSVPagesIter):
    url_fmt = "https://www.{domain}/dp/{asin}"
    def __init__(self, asins_csv):
        super(AmzListingsIter, self).__init__(asins_csv)

    def do_get_url(self, row):
        assert "domain" in row, "A 'domain' field is required for AmzListingsIter, eg: 'amazon.com'"
        assert "asin" in row, "A 'asin' field is required for AmzListingsIter"
        return self.url_fmt.format(domain=row["domain"], asin=row["asin"])


class AmzListingsSpider(BasicProductsSpider):
    name = 'amz_listings'
    follow_link_from = None
    custom_settings = {
            "DEFAULT_REQUEST_HEADERS": {
#                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
            },
#            "CONCURRENT_REQUESTS" : 1,
            "DOWNLOAD_DELAY":3
    }


    def __init__(self, asins_csv):
        self.asins_csv = asins_csv
    

    def create_pages_iterator(self):
        return AmzListingsIter(self.asins_csv)


    def create_loader(self, selector=None, response=None, webpage=None):
        fields = ["domain", "asin", "title", "broad_bsr", "narrow_bsr", "nratings", "ratings"]
        Listings = create_item_class("Listings", fields )
        if not webpage:
            # dont know how
            return ItemLoader(item=Listings(), selector=selector, response=response)
        elif webpage.auxiliaries[0]["domain"] == "amazon.co.jp":
            _LISTINGS_XPATH_LIST = [_JP_LISTINGS_XPATHS]
        elif webpage.auxiliaries[0]["domain"] == "amazon.ae":
            _LISTINGS_XPATH_LIST = padding_dict.pad(_AE_LISTINGS_XPATHS, _AE_LISTINGS_XPATHS2) 
        elif webpage.auxiliaries[0]["domain"] == "amazon.com":
            _LISTINGS_XPATH_LIST = [_US_LISTINGS_XPATHS]
        elif webpage.auxiliaries[0]["domain"] == "amazon.de":
            _LISTINGS_XPATH_LIST = [_DE_LISTINGS_XPATH]
        elif webpage.auxiliaries[0]["domain"] == "amazon.it":
            _LISTINGS_XPATH_LIST = [_IT_LISTINGS_XPATH]
        else:
            raise NotImplementedError("{}: currently not supported!".format(webpage.auxiliaries[0]["domain"]))

        domain = webpage.auxiliaries[0]["domain"]
        asin = webpage.auxiliaries[0]["asin"]

        loaders_list = []
        for _LISTINGS_XPATH in _LISTINGS_XPATH_LIST:
            loader = ItemLoader(item=Listings(), selector=selector, response=response)
            loader.add_value("domain", domain)
            loader.add_value("asin", asin)
            loader.add_xpath("title", _LISTINGS_XPATH["title"], join_strip())
            loader.add_xpath("broad_bsr", _LISTINGS_XPATH["broad_bsr"], join_strip_extdigits())
            loader.add_xpath("narrow_bsr", _LISTINGS_XPATH["narrow_bsr"], join_strip_extdigits())
            loader.add_xpath("nratings", _LISTINGS_XPATH["nratings"], join_strip_extdigits())
            loader.add_xpath("ratings", _LISTINGS_XPATH["ratings"], join_strip_extdigits(min)) # eg: 4.7 out of 5 -> 4.7
            loaders_list.append(loader)

        ch_loader = ChainedLoader.chain(*loaders_list)
        ch_loader.set_united_item(fields)
        return ch_loader
