# scrapy_products

使用 Scrapy &amp; Schedule &amp; Threading 自动爬取特定商品在 Amazon 上获取排名（BSR, 搜索排名等）信息。该项目最初的目的是为了给Amazon运营人员提供一个获取前台信息的免费工具。

# 环境

- Python 3.6+
- Scrapy 1.8.0
- schedule 0.6.0
- plac 1.1.3

# 特性

- 已支持的站点：美、日、德、意、中东。
- 获取特定商品的信息，包括：标题、评级（Rating）、评级数、BSR、搜索排名（Organic Rank）。
- 待搜索的商品列表存放在csv文件中，第一行为行头，包括字段名：domain,asin,[sku],keywords，其中sku可选，余下每一行表示一个商品，支持同时输入多个csv文件。见auto.py。某个商品表示为：
    ```
    amazon.it,B071DBXXXX,myproductA,product A search kw
    ```
- 在搜索结果里查找时，同一种商品的不同变种（比如红色和绿色）可以自动识别出来，只要其标题的前面部分是一致的，
- 提供一组工具类：BasicProductsSpider、ChainedLoader、CSVPagesIter等，封装了基于Scrapy的翻页查找类应用的通用业务逻辑，用户可根据API开发定制化业务，上述亚马逊业务可视为其应用示例。


# 使用前注意（重要）

- 如果可以的话，尽量考虑优先使用 Amazon Advertising API。
- Amazon 上同一站点不同类目商品页面布局不同，使用前可能需要添加新的布局（Xpath），具体请参考源码，搜索排名不受影响。
- 为了能够正常使用程序，可能需要代理，请考虑自行购买SSR服务。在搜索某个站点的商品时之前，可能需要设置位于对应国家（地区）的代理服务器，受covid-19疫情影响，某个站点的部分商品可能不会出现在其他国家（地区）的用户的搜索结果里面。

# API

暂缺，可以查看basic_product.py, models.py相关组件源码以及我们的示例。
