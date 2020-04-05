import re

from scrapy_products.models import CSVPagesIter

        
_AMZ_DOMAIN_TAB = [
        ["domain",       "search_fmt"],
        ['amazon.co.jp', "hhtps://{dm}/s?k={kw}&__mk_ja_JP=カタカナ&ref=nb_sb_noss"],
        ["amazon.ae",    "https://{dm}/s?k={kw}&ref=nb_sb_noss_1"]
]


class TableHelper:
    def __init__(self, table, set_key):
        self.table = table

        # suppose the first row of _DOMAIN_TAB descripts the fieldnames
        self.fields_map = {f:i for i,f in enumerate(table[0])}

        self.key_map = {r[self.fields_map[set_key]]:i for i,r in enumerate(table) if i > 0}
        if len(self.key_map) < len(table) - 1:
            raise ValueError("Incalid key:", set_key)


    def lookup(self, key, field):
        try:
            return self.table[self.key_map[key]][self.fields_map[field]]
        except KeyError:
            raise ValueError("lookup: invalid query (key={}, field={})".format(key, field))


class AmzSearchIter(CSVPagesIter):
    def __init__(self, kwcsv):
        super(AmzSearchIter, self).__init__(kwcsv)
        self.kwcsv = kwcsv
        self.dmhelper = AmzDomainHelper(_AMZ_DOMAIN_TAB, "domain")    


    def do_get_url(self, row):
        assert "domain" in row, "for csv {} a 'domain' field is required, eg: 'amazon.com'.".format(self.kwcsv)
        assert "keywords" in row, "for csv {} a 'keywords' field is required, eg: 'iphone 11' ".format(self.kwcsv)

        fmt = self.dmhelper.lookup(row["domain"], "search_fmt")
        return fmt.format(dm=row["domain"], kw=__normalizer(row["keywords"], "+"))


    def __normalizer(kw, sub=''):
        return re.sub("\\s+", sub, kw.strip()).casefold()
