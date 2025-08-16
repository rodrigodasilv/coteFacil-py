from spiders.products_spider import ProductsSpider
from scrapy.crawler import CrawlerProcess
import json

def run_spider(job):
    print(job)
    usuario = job["usuario"]
    senha = job["senha"]
    callback_url = job["callback_url"]

    process = CrawlerProcess()
    process.crawl(ProductsSpider, usuario=usuario, senha=senha, callback_url=callback_url)
    process.start()
