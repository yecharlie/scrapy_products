import re

from scrapy.item import DictItem, Field
import scrapy.loader.processors as processors


def regextract(regex=None, group=0):
    def _regextrat(string, regex=regex, group=group):
        return re.search(regex, string).group(group) if string else None

    return _regextrat


def extdigits(pick_fn=None):
    """ Extratct Digits

    Return a function whivh first extract digits then apply it to pick_fn (if set).
    """
    def _extdigits(string):
        #(?:...) is a non-capturing group 
        regex = re.compile(r"\d+(?:[,|\.]?\d+)*")
        # pattem: "1-6 of 16 reviews" -> 16
        digits = re.findall(regex, string) if string else None
        return pick_fn(digits) if digits and pick_fn else digits
    return _extdigits


def join_strip():
    return processors.Compose(processors.Join(), str.strip)


def join_strip_regextract(re, gp=0):
    return processors.Compose(processors.Join(), str.strip, regextract(re,gp))


def join_strip_extdigits(pick_fn=None):
    return processors.Compose(processors.Join(), str.strip, extdigits(pick_fn))


def create_item_class(class_name, field_list):
# refer: https://github.com/scrapy/scrapy/issues/398
    field_dict = {}
    for field_name in field_list:
        field_dict[field_name] = Field()
    return type(str(class_name), (DictItem,), {'fields': field_dict})


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


    @property        
    def keys(self):
        return key_map.keys()
