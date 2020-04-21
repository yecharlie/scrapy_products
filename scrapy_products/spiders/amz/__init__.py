_AMZ_DOMAIN_TAB = [
        ["domain",      "typecode", "search_fmt"],
        ['amazon.co.jp',"ケース",   "https://www.{dm}/s?k={kw}&__mk_ja_JP=カタカナ&ref=nb_sb_noss"],
        ["amazon.ae",   "case",     "https://www.{dm}/s?k={kw}&ref=nb_sb_noss_1"],
        ["amazon.com",  "case",     "https://www.{dm}/s?k={kw}&ref=nb_sb_noss_2"],
        ["amazon.de",   "Hülle",    "https://www.{dm}/s?k={kw}&__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss"],
        ["amazon.it",  "",     "https://www.{dm}/s?k={kw}&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss"] # don't support SIMPLE extract of keyowrds
]
