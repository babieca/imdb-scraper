# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()

    film_rating = scrapy.Field()
    duration = scrapy.Field()
    genre = scrapy.Field()
    release_date = scrapy.Field()
    country = scrapy.Field()

    imdb_rating = scrapy.Field()
    rating_count = scrapy.Field()

    description = scrapy.Field()
    storyline = scrapy.Field()

    directors = scrapy.Field()
    writer = scrapy.Field()
    stars = scrapy.Field()
    cast = scrapy.Field()

    taglines = scrapy.Field()

    url = scrapy.Field()
    req_headers = scrapy.Field()
    res_headers = scrapy.Field()
    body = scrapy.Field()

    def __repr__(self):
        pass
