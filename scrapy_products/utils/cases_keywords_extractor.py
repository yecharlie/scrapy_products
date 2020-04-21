import re
import logging

_logger = logging.getLogger(__name__)

_BRANDS=[
"iPhone",
"Apple",
"Huawei",
"Galaxy",
"Samsung",
"Xperia",
"Sony",
"Mi",
"Redmi",
"Xiaomi",
"OnePlus",
"1+",
"OPPO",
"Pixel",
"Google"
]

def simple_extract(
    title,
    typecode,
    brandsl=None
):
    """ Extract with Certain Pattem

    Pattem: BRAND + SERIES + TYPECODE (eg: iphone 7 case)
    """
    tt = title.casefold()
    brandsl = brandsl if brandsl else _BRANDS

    # try to recognize model with certain pattem 
    for bd in brandsl:
        # "?" makes ".+" match in a non-greedy fashion
        pat = "{bd}.+?{tc}".format(bd=bd, tc=typecode).casefold()

        # replace findall with search
        match = re.search(pat, tt)
        if match:
            kw = match.group()
            _logger.debug("auto-generate keywords {} for\n\t{}".format(kw, tt))
            return kw

    _logger.debug("fail to generate keywords for\n\t{}".format(tt))
