# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import AvitoRealEstateItem
import requests
import re


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru','www.avito.ru']
    start_urls = ['https://www.avito.ru/syzran/kvartiry/']

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()'):
            try:
                tmp = int(num.get())
                yield response.follow(f'/syzran/kvartiry/?p={tmp}', callback=self.parse)

            except ValueError as e:
                continue
            except TypeError as e:
                continue
        for ads_url in response.css('div.item_table h3.snippet-title a.snippet-link::attr("href")'):
            yield response.follow(ads_url, callback= self.ads_parse)

    def get_phone(self, response):
        _id = re.search(r'\d+$', response.url)[0]
        url = f'https://m.avito.ru/api/1/items/{_id}/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir'
        result = requests.get(url)
        phone_number = '+' + re.findall(r'number=%2B(\d+)',result.text)[0]
        return phone_number

    def ads_parse(self, response):
        item = ItemLoader(AvitoRealEstateItem(), response)
        item.add_value('url', response.url)
        item.add_css('author_name', 'div.seller-info-name  a::text')
        item.add_css('author_url', 'div.seller-info-name  a::attr(href)')
        item.add_xpath('title','//span[@class = "title-info-title-text"]/text()')
        item.add_xpath('data', "//div[@class= 'title-info-metadata-item-redesign']/text()")
        for sel in response.xpath("//li[@class='item-params-list-item']"):
            param_value = sel.xpath("./text()").getall()[1]
            param = sel.xpath(".//span/text()").get()
            item.add_value('item_param', {param:param_value})
        item.add_xpath('photos', "//div[contains(@class, 'gallery-img-frame')]/@data-url")
        item.add_value('phone', self.get_phone(response))

        yield item.load_item()



        print(1)
