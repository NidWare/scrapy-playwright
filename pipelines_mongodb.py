import pymongo

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        mongo_user = crawler.settings.get("MONGO_USER")
        mongo_password = crawler.settings.get("MONGO_PASSWORD")
        mongo_port = crawler.settings.get("MONGO_PORT", 27017)
        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@localhost:{mongo_port}/"
        mongo_db = crawler.settings.get("MONGO_DATABASE", "items")
        mongo_collection = crawler.settings.get("MONGO_COLLECTION", "scraped_articles")
        return cls(mongo_uri, mongo_db, mongo_collection)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.mongo_collection].insert_one(dict(item))
        return item
    