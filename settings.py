BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'

FEED_EXPORT_ENCODING = "utf-8"

DOWNLOADER_MIDDLEWARES = {
    "scrapy_playwright.middleware.PlaywrightMiddleware": 543,
}

