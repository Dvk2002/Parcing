# -*- coding: utf-8 -*-
import scrapy
from datetime import date


class HubrWeeklySpider(scrapy.Spider):
    name = 'habr.com'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly']

    def parse(self, response):
        pagination_urls = response.css('ul.toggle-menu_pagination a::attr("href")').extract()
        for itm in pagination_urls:

            yield response.follow(itm, callback=self.parse)
        for post_url in response.xpath("//a[contains(@class,'post__title_link')]/@href").extract():
            yield response.follow(post_url, callback= self.post_parse)

    def post_parse(self, response):

        data = {
            'title': response.xpath("//h1//span[@class='post__title-text']/text()").get(),
            'url': response.url,
            'author': response.css("span.user-info__nickname::text").get(),
            'author_url': response.xpath("//a[re:test(@class,'post__user-info ')]/@href").get(),
            'post_date': response.xpath("//span/@data-time_published").get(),
            'pars_date': f'{date.today()}',
            'comments_acc' : response.css("span.post-stats__comments-count::text").get(),
            'tags': response.xpath("//dl[dt/text() = 'Теги:']//a/text()").getall(),
            'hubs': response.xpath("//dl[dt/text() = 'Хабы:']//a/text()").re('\w.+')
        }

        yield (data)


#nav-pagess