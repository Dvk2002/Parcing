# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import date, timedelta


# class BlogparseItem(scrapy.Item):
# #     # define the fields for your item here like:
# #     # name = scrapy.Field()
# #     pass


def clean_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def clean_url(values):
        return f'https://www.avito.ru{values}'


def clean_date(values):
    return values[0].replace('сегодня', f'{date.today()}').\
        replace('вчера', f'{date.today() - timedelta(days=1)}').replace('\n ','')


class AvitoRealEstateItem(scrapy.Item):

    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    data = scrapy.Field(input_processor=clean_date)
    author_name = scrapy.Field(input_processor=lambda values: values[0].replace('\n ',''))
    author_url = scrapy.Field(input_processor= lambda values: f'https://www.avito.ru{values[0]}')
    item_param = scrapy.Field()
    phone = scrapy.Field()
    photos = scrapy.Field(input_processor=MapCompose(clean_photo))

class ZillowItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor = TakeFirst())
    title = scrapy.Field()
    photos = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    sqrt = scrapy.Field()
    sqft = scrapy.Field()
