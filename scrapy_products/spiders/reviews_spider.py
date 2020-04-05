# *-* coding: utf-8 *-*
"""
MIT License

Copyright (c) 2018 Ajinkya Indulkar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on: 5-Jul-2018

@author: Ai
"""
import scrapy
from scrapy_products.bin.parse_csv import read_csv
from scrapy_products.utils import extdigits


class AmazonReviewsSpider(scrapy.Spider):
    name = 'amz_reviews'
    custom_settings = {
            "DEFAULT_REQUEST_HEADERS": {
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'            }
    }


    def __init__(
        self,
        asins_path,
        *args, **kwargs
    ):
        super(AmazonReviewsSpider, self).__init__(*args, **kwargs)
        self.asins_path = asins_path
        self.parse_nreviews = extdigits(max)
        self.parse_stars = extdigits(min)
        self.parse_helpful_count = extdigits()


    def start_requests(self):
        asinsl, domainl = read_csv(self.asins_path, "asin", "domain")
        for asin, domain in zip(asinsl, domainl):
            yield scrapy.Request(url='https://www.{0}/product-reviews/{1}/ref=dpx_acr_txt?showViewpoints=1&sortBy=recent'.format(domain, asin), callback=self.parse, meta={"asin":asin, "domain":domain}) 


    def parse(self, response):
        domain = response.meta["domain"]
        asin = response.meta["asin"]

        raw_nreviews = response.css(".a-section [data-hook*='review-count']::text").extract_first()
        nreviews = self.parse_nreviews(raw_nreviews)

        for item in response.css('.a-section.review'):
            if item.css('div::attr(data-hook)').extract_first() == 'review':
                # overview: nreviews + most recent reciew
                review = {"NReviews":nreviews}

                raw_variances = item.css("a[data-hook='format-strip']::text").extract()

                review.update({
                        'domain': domain,
                        'asin': asin,
                        'review_ID': item.css('div.a-section.celwidget::attr(id)').extract_first().split('-')[1],
                        'date': item.css('[data-hook="review-date"]::text').extract_first(),
                        "variance1": raw_variances[0] if raw_variances else None,
                        "variance2": "\n".join(raw_variances[1:]) if raw_variances[1:] else None,
                        'stars': self.parse_stars(item.css('a::attr(title)').extract_first()),
                        'review_title': item.css('[data-hook="review-title"] span::text').extract_first(),
                        'review': ' '.join(item.css("[data-hook*='review-body'] span::text").extract()),
                        'author': item.css('.a-profile-name::text').extract_first(),
                        'helpful_count': self.parse_helpful_count(item.css('[data-hook*="helpful-vote-statement"]::text').extract_first())
                        })
                yield review
                return

#        next_page = response.css('.a-last > a::attr(href)').extract_first()
#        if next_page:
#            next_page = response.urljoin(next_page)
#            yield scrapy.Request(url=next_page, callback=self.parse, meta={"asin":asin, "domain":domain})
