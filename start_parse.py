from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.hubr_weekly import HubrWeeklySpider


if __name__ == '__main__':

    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crowler_proc = CrawlerProcess(settings= craw_settings)
    crowler_proc.crawl(HubrWeeklySpider)
    crowler_proc.start()
