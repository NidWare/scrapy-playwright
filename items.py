import scrapy

class NewsArticleItem(scrapy.Item):
    title = scrapy.Field(required=True)
    description = scrapy.Field(required=True)
    article_text = scrapy.Field(required=True)
    publication_datetime = scrapy.Field(required=True)
    header_photo_url = scrapy.Field(default=None)
    header_photo_base64 = scrapy.Field(default=None)
    keywords = scrapy.Field(default=[])
    authors = scrapy.Field(default=[])
    source_url = scrapy.Field(required=True)
    