def pad(*dicts):
    """ Pad dicts according to the head dict of input
    """
    if not dicts:
        return dicts

    dict_base = dicts[0]
    for d in dicts[1:]:
        for k in dict_base.keys():
            if k not in d:
                d[k] = dict_base[k]

    return dicts

# print(pad({'a':1},{'b':2},{}))
