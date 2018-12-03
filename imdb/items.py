# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    movie_id = scrapy.Field()
    title = scrapy.Field()

    film_rating = scrapy.Field()
    duration = scrapy.Field()
    genre = scrapy.Field()
    release_date = scrapy.Field()

    imdb_ratingValue = scrapy.Field()
    imdb_bestRating = scrapy.Field()
    imdb_ratingCount = scrapy.Field()

    summary = scrapy.Field()
    storyline = scrapy.Field()

    director = scrapy.Field()
    creator = scrapy.Field()
    writer = scrapy.Field()
    stars = scrapy.Field()

    taglines = scrapy.Field()
    tagwords = scrapy.Field()
    reviews = scrapy.Field()

    url = scrapy.Field()
    req_headers = scrapy.Field()
    res_headers = scrapy.Field()

    def __repr__(self):
        pass
