import scrapy
from scrapy_playwright.page import PageCoroutine
from project.items import NewsArticleItem  # Проверьте корректность импорта в зависимости от структуры проекта

class KpSpider(scrapy.Spider):
    name = "kp_spider"
    allowed_domains = ["kp.ru"]
    start_urls = ["https://www.kp.ru/online/"]

    custom_settings = {
        # Настройки для Playwright
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        
        # Приоритезация пайплайнов:
        # Сначала обрабатываем изображения (PhotoDownloaderPipeline), затем сохраняем в MongoDB.
        "ITEM_PIPELINES": {
            "project.pipeline.PhotoDownloaderPipeline": 100,
            "project.pipelines_mongodb.MongoDBPipeline": 200,
        },
        "RESULT_IMAGE_QUALITY": 35,
        
        # Соблюдение robots.txt и задержка между запросами
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
    }

    async def parse(self, response):
        # Пример извлечения ссылок на статьи.
        # XPath нужно скорректировать согласно реальной верстке сайта kp.ru.
        article_links = response.xpath("//div[contains(@class, 'article-item')]//a/@href").getall()
        for link in article_links:
            if not link.startswith("http"):
                link = response.urljoin(link)
            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={
                    "playwright": True,
                    "playwright_page_coroutines": [
                        PageCoroutine("wait_for_selector", "article")
                    ],
                },
            )

    async def parse_article(self, response):
        item = NewsArticleItem()
        item["title"] = response.xpath("//h1/text()").get(default="").strip()
        item["description"] = response.xpath("//meta[@name='description']/@content").get(default="").strip()
        # Извлекаем весь текст статьи, объединяя все текстовые узлы.
        item["article_text"] = " ".join(response.xpath("//div[contains(@class, 'article-content')]//text()").getall()).strip()
        item["publication_datetime"] = response.xpath("//time/@datetime").get(default="").strip()
        item["header_photo_url"] = response.xpath("//div[contains(@class, 'article-header')]//img/@src").get()
        
        # Извлечение ключевых слов (если они заданы в meta-теге)
        keywords = response.xpath("//meta[@name='keywords']/@content").get()
        if keywords:
            item["keywords"] = [kw.strip() for kw in keywords.split(",")]
        else:
            item["keywords"] = []
        
        # Извлечение авторов (пример XPath – требует проверки)
        authors = response.xpath("//span[contains(@class, 'author')]/text()").getall()
        item["authors"] = [author.strip() for author in authors if author.strip()]
        
        item["source_url"] = response.url
        yield item
        