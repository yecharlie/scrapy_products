# -*- coding: utf-8 -*-
import scrapy
import re
import os.path as pth
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest

from scrapy_products.spiders.basic_products import BasicProductsSpider
from scrapy_products.spiders.amz import _AMZ_DOMAIN_TAB
from scrapy_products.utils import (TableHelper, create_item_class, join_strip)
from scrapy_products.models import (CSVPagesIter,ChainedLoader)


_SEARCH_XPATHS = {
        "next"   : "//li[@class='a-last']/a/@href" ,
        "nested" : "//div[contains(@class, 's-result-list s-search-results')]/div[@data-asin]", # the base xpath of below fields
        "asin"   : "@data-asin",
        "title"  : ".//h2/a/span/text()",
        "sponsored": ".//div[@data-component-type='sp-sponsored-result']"
}

class WaitProductsAjaxCompleted:
    def __init__(self, times):
        self.cur_times = 0
        self.n_times = times
        self.n_invisible = 0

    def _observe_no_diff_n_times(self, driver):
        products = driver.find_elements_by_xpath(_SEARCH_XPATHS["nested"])
        self.n_products = len(products)

        # ASINs of invisible products
#        invisibles = {i: p.find_element_by_xpath(_SEARCH_XPATHS["asin"]).get_attribute("outerHTML") for i,p in enumerate(products) if not p.is_displayed()}
        invisibles = [i for i,p in enumerate(products) if not p.is_displayed()]
        self.invisibles = invisibles
        logging.info("url={}, cur_times={}, n_invis={}".format(driver.current_url, self.cur_times, len(invisibles)))
#        logging.info("there are {} invisible products out of total {} at page, indices are {}. the first invisible product's ASIN is {}".format(len(invisibles), len(products), invisibles.keys(), invisibles[invisibles.keys()[0]] if invisibles.keys() else None))
        if len(invisibles) != self.n_invisible:
            self.n_invisible = len(invisibles)
            self.cur_times = 0
        else:
            self.cur_times += 1

        return self.cur_times >= self.n_times


    def __call__(self, driver):
        return self._observe_no_diff_n_times(driver)


class InvisibleProductsDetector:
    def __call__(self, driver, res_meta):
        # wait for products Ajaxs started
        try:
            WebDriverWait(driver, 10, 1).until_not(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, _SEARCH_XPATHS["nested"])
                )
            )
        except BaseException:
            logging.exception("wait after 10 secs but products ajaxs operations has not been started.")

        # wait for products Ajaxs completed
        waitc = WaitProductsAjaxCompleted(2)
        try:
            WebDriverWait(driver, 5, 0.5).until(waitc)
        except BaseException:
            logging.exception("wait after 5 secs but products ajaxs operations has not been completed.")

        invisibles = waitc.invisibles
        res_meta.update(amz_search_invisibles=invisibles)

        logging.info("there are {} invisible products out of total {} at page, indices are {}".format(len(invisibles), waitc.n_products, invisibles))
#        logging.info("there are {} invisible products out of total {} at page, indices are {}. the first invisible product's ASIN is {}".format(len(invisibles), waitc.n_products, invisibles.keys(), invisibles[invisibles.keys()[0]] if invisibles.keys() else None))



        


class AmzSearchIter(CSVPagesIter):
    def __init__(self, kwcsv):
        super(AmzSearchIter, self).__init__(kwcsv)
        self.url_helper = TableHelper(_AMZ_DOMAIN_TAB, "domain")    


    def do_get_url(self, row):
        assert "domain" in row, "A 'domain' field is required for AmzSearchIter, eg: 'amazon.com'"
        assert "keywords" in row, "A 'keywords' field is required for AmzSearchIter, eg: 'iphone 11' "

        fmt = self.url_helper.lookup(row["domain"], "search_fmt")
        return fmt.format(dm=row["domain"], kw=AmzSearchIter.__normalizer(row["keywords"], "+"))


    def __normalizer(kw, sub=''):
        return re.sub("\\s+", sub, kw.strip()).casefold()


    def __iter__(self):
        for wp in super(AmzSearchIter, self).__iter__():
            # collect the found asked products 
            wp.found = {} 

            # counter of Ads in one search
            wp.sp_conuter = 0
            yield wp
        


class AmzSearchIndsSpider(BasicProductsSpider):
    name = 'amz_search_inds'
#    Request = SeleniumRequest

    custom_settings = {
            "DEFAULT_REQUEST_HEADERS": {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
            },
#            "CONCURRENT_REQUESTS" : 1,
#            "DOWNLOAD_DELAY":6
    }


    def __init__(self, kwcsv=None):
        self.kwcsv = pth.abspath(kwcsv)
#        self.detector = InvisibleProductsDetector()


    def create_pages_iterator(self):
        return AmzSearchIter(self.kwcsv)


    def create_loader(self, selector=None, response=None, webpage=None):
        Product = create_item_class("Product", ["matched_asin", "title", "index", "next_page", "sponsored"]) # "asin" has been tocken for asked asin 
        loader = ItemLoader(item=Product(), selector=selector, response=response)
        loader.add_xpath("next_page", _SEARCH_XPATHS["next"], join_strip())

        # attributes of a product
        chained_loader = ChainedLoader.chain_nested(loader, _SEARCH_XPATHS["nested"])
        chained_loader.add_xpath("matched_asin", _SEARCH_XPATHS["asin"])
        chained_loader.add_xpath("title", _SEARCH_XPATHS["title"], join_strip())

        # Will be filtered If return False directly
        is_sponsored_processor = lambda x:[True] if x else [False]
        chained_loader.add_xpath("sponsored", _SEARCH_XPATHS['sponsored'], is_sponsored_processor)

        return loader


#    def request_hook(self, wp):
#        return SeleniumRequest(
#                url=wp.url,
#                callback=self.parse_products,
#                cb_kwargs=dict(webpage=wp, ioffset=1),
#                meta={"selenium_callback":self.detector}
#                )


    def found_product(self, product, webpage):
        asin, title = product["matched_asin"], product["title"]
        for aux in webpage.auxiliaries:
            if asin == aux["asin"]:
                return aux["asin"]
            elif "title" in aux:
                nprefix = len(title) * 4 // 5

                # compaare prefix of title, title may be appended with different color information, in case
                if title[:nprefix] == aux["title"][:nprefix]:
                    return aux["asin"]
        return


    def filter_product_hook(self, product, webpage, meta, **locators):
#        self.logger.debug("Product: title={}, asin={} sponsored={}".format(product["title"], product["matched_asin"], product["sponsored"]))

        # ignored
        if product["sponsored"]:
            webpage.sp_conuter += 1
            return

        found_asin = self.found_product(product, webpage)
        domain = webpage.auxiliaries[0]["domain"]
        if found_asin:
            if found_asin in webpage.found:
                # sometimes there are several subproducts on the list
                return
            else:
                # tag
                webpage.found[found_asin] = True

            product["domain"] = domain

            # Note that matched_asin may not equal to found_asin
            product["asin"] = found_asin

            product["index"] = locators["index"] - webpage.sp_conuter

            # no need as we have ignored Ads
            del product["sponsored"]

            return product


    def found_all_products(self, webpage):
#        self.logger.debug("Webpage: title={}, asin={}".format(webpage.auxiliaries[0]["title"], webpage.auxiliaries[0]["asin"]))
        return all([aux["asin"] in webpage.found for aux in webpage.auxiliaries])


    def continue_crawling_hook(self, next_page, webpage, meta, **locators):
#        self.logger.debug("Request response url: %s" % webpage.url)
#        self.logger.debug("Request driver url: %s" % meta['driver'].current_url)
#        return False
        return super(AmzSearchIndsSpider, self).continue_crawling_hook(next_page, webpage, meta, **locators) and not self.found_all_products(webpage)
