# -*- coding: utf-8 -*-
import scrapy
import abc
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BasicProductsSpider(CrawlSpider, metaclass=abc.ABCMeta):
#    name = 'basic_products'
    follow_link_from = "next_page"
#    list_indices_at = "index"
#    Request = scrapy.Request


    @abc.abstractmethod
    def create_pages_iterator(self):
        """ Return a Webpage iterator

        A webpage is simple structure include ane url field and one optional auxiliaries field
        """
        ...


    @abc.abstractmethod
    def create_loader(self, selector=None, response=None, webpage=None):
        """ Object to load item

        A loader could be an ItemLoader instance or obbject that implements the load_item() interface. 
        """
        ...


    def start_requests(self, pgiter=None):
        for wp in pgiter if pgiter else self.create_pages_iterator():
            yield self.request_hook(wp)


    def request_hook(self, wp):
        return scrapy.Request(url=wp.url, callback=self.parse_products, cb_kwargs=dict(webpage=wp))


    def parse_products(self, response, webpage, ioffset=1, pageno=1):
        loader = self.create_loader(response=response, webpage=webpage)
        item = loader.load_item()

#        self.logger.debug("item.items={}".format(item.items()))
        # Suppose the page contain N (N >= 1) products and at most one link to follow
        nproducts = max(len(v) for k,v in item.items())
        branch_fields = [] # product-specific
        tree_fields = [] # shared by all products 
        [branch_fields.append(k) if len(v) == nproducts else tree_fields.append(k) for k,v in item.items() if k != self.follow_link_from]
        self.logger.debug("NProducts={}, Branchs={}, Trees={}".format(nproducts, branch_fields, tree_fields))

        for i, bfvals in enumerate(zip(*[item[bf] for bf in branch_fields])):
            # 1. construct a product
            product = { tf:item[tf] for tf in tree_fields}
            product.update({ bf:v for bf, v in zip(branch_fields, bfvals)})

#            # 2. add index
#            if self.list_indices_at and self.list_indices_at not in branch_fields + tree_fields: # index of porduct
#                product.update({self.list_indices_at:i+ioffset})

            # 3. filter
            product = self.filter_product_hook(
                    product,
                    webpage,
                    response.meta,
                    index = i + ioffset,
                    ioffset = ioffset,
                    pageno = pageno
                    )

            if product:
                yield product

        next_page = item[self.follow_link_from] if self.follow_link_from else None
        if self.continue_crawling_hook(
            next_page,
            webpage,
            response.meta,
            ioffset = ioffset,
            pageno = pageno
        ):
            yield response.follow(
                    next_page[0],
                    callback=self.parse_products,
                    cb_kwargs=dict(
                        webpage=webpage,
                        ioffset=ioffset+nproducts,
                        pageno = pageno+1)
                )


    def continue_crawling_hook(self, next_page, webpage, meta, **locators):
        return True if next_page else False


    def filter_product_hook(self, product, webpage, meta, **locators):
        return product

#    rules = (
#        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
#    )
#
#    def parse_item(self, response):
#        item = {}
#        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
#        #item['name'] = response.xpath('//div[@id="name"]').get()
#        #item['description'] = response.xpath('//div[@id="description"]').get()
#        return item
