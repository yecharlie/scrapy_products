import abc
import re
import os.path as pth

from scrapy_products.bin.parse_csv import read_csv
        

class WebPage:
    def __init__(self, url, auxs=None):
        self.__url=url
        self.auxiliaries=auxs


    @property
    def url(self):
        return self.__url


    @property
    def auxiliaries(self):
        return self.__auxs


    @auxiliaries.setter
    def auxiliaries(self, auxs):
        self.__auxs = auxs


class CSVPagesIter:
    def __init__(self, kwcsv, get_url=None):
        self.get_url = get_url
        self.kwcsv = kwcsv


    def __iter__(self):                    
        rows, fieldnames = read_csv(pth.abspath(self.kwcsv))

        # merge rows who belongs to same url
        urls = [self.do_get_url(r) for r in rows]
        merged_urls = {url:[] for url in set(urls)}
        for url,row in zip(urls,rows): 
            merged_urls[url].append(row)

        for url,auxs in merged_urls.items():
            yield WebPage(url, auxs)


    def do_get_url(self, row):
        if self.get_url:
            return self.get_url(row)
        else:
            raise NotImplementedError()


class ChainedLoader:
    def __init__(self, itloader, chloader=None):
        self._local = itloader
        self._next = chloader
        self.item_keys = []


    @staticmethod
    def chain(*itloaders):
        for i,ld in enumerate(reversed(itloaders)):
            if i == 0:
                ph = ChainedLoader(ld) # pior to create head
                h = ph
            else:
                h = ChainedLoader(ld, ph) # new head
                ph = h

        h._dim = len(itloaders)
        return h


    @staticmethod
    def chain_nested(itloader, xpath, filter_ = lambda x:x):
        seles = itloader.get_xpath(xpath)
        if not seles:
            return ChainedLoader.chain(itloader.nested_xpath(xpath))

        nested = [itloader.nested_xpath("{}[{}]".format(xpath, i+1)) for i,sl in enumerate(seles) if filter_(sl)]
#        for n in nested:
#            print(n.selector.get())
        return ChainedLoader.chain(*nested)


    @property
    def dim(self):
        return self._dim


    def add_xpath(self, field_name, xpath, *processors, default_val = '', **kwargs):
#        print(self._local.selector.get())
        if self._local.get_xpath(xpath, *processors, **kwargs):
            self._local.add_xpath(field_name, xpath, *processors, **kwargs )
        else:
            self._local.add_value(field_name, default_val)

        if self._next:
            self._next.add_xpath(field_name, xpath, *processors, default_val=default_val, **kwargs)

    
    def add_value(self, field_name, value, *processors, **kwargs):
        self._local.add_value(field_name, value)
        if self._next:
            self._next.add_value(field_name, value, *processors, **kwargs)


    def set_united_item(self, keys):
        """ Set Minimum Requriment for a Completed Load Action
        """
        self.item_keys = keys


    def load_item(self):
        return self._recursive_load({})


    def _recursive_load(self, cur_item):
        item = self._local.load_item()

        # 1. preference on items from the previous loaders 
        # 2. the actual number of fields might be more than we set with self.item_keys
        recur = False
        for k in self.item_keys + list(item.keys()):
            if k in cur_item:
                continue
            elif k in item:
                cur_item[k] = item[k]
            else:
                recur = True

        if recur and self._next:
            return self._next._recursive_load(cur_item)
        else:
            return cur_item
