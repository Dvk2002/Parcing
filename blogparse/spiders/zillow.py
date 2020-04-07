
# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import ZillowItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time



class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/homes/Tampa,-FL_rb/']

    browser = webdriver.Chrome()

    def parse(self, response):
        for pag_url in response.xpath('//nav[@aria-label="Pagination"]//a/@href'):
            yield response.follow(pag_url, callback=self.parse)

        for ads_url in response.xpath('//a[@class="list-card-link"]/@href'):
            data = {}
            data['price']= response.xpath('//div[@class="list-card-price"]/text()').get()
            data['address'] = response.xpath('//address[@class="list-card-addr"]/text()').get()
            data['sqrt'] = response.xpath('//ul[class="list-card-details"]//li[2]/text()').get()

            yield response.follow(ads_url, callback=self.ads_parse, cb_kwargs= {'data': data})


    def ads_parse(self, response, data):

        item = ItemLoader(ZillowItem(), response)
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_class_name('ds-media-col')
        photo_pic_len = len(
                    self.browser.find_elements_by_xpath('//ul[@class="media-stream"]//source[@type="image/jpeg"]')
                )

        while True:
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
            tmp = len(self.browser.find_elements_by_xpath('//ul[@class="media-stream"]//source[@type="image/jpeg"]'))
            if tmp == photo_pic_len:
                break

            photo_pic_len = tmp
        images = [
            itm.get_attribute('srcset').split(' ')[-2] for itm in
            self.browser.find_elements_by_xpath('//ul[@class="media-stream"]//source[@type="image/jpeg"]')
        ]
        item.add_value('photos', images)
        item.add_value('url', response.url)
        item.add_value('price', data['price'])
        item.add_value('address', data['address'])
        item.add_value('sqrt', data['sqrt'] )

        yield item.load_item()

