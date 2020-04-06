import os
from dotenv import load_dotenv
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.insta import InstaSpider
# from blogparse.spiders.hubr_weekly import HubrWeeklySpider
# from blogparse.spiders.gb_blog import GbBlogSpider
# from blogparse.spiders.avito import AvitoSpider



env_path = Path(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)


if __name__ == '__main__':

    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crowler_proc = CrawlerProcess(settings= craw_settings)
    # crowler_proc.crawl(AvitoSpider)
    # crowler_proc.crawl(HubrWeeklySpider)
    crowler_proc.crawl(InstaSpider, logpass=(os.getenv('INSTA_LOGIN'), os.getenv('INSTA_PWD')))
    crowler_proc.start()
