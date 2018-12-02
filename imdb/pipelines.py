# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from elasticsearch_dsl.document import Document
from elasticsearch_dsl.field import Text, Date, Keyword, Integer, Completion, Float, Object
from elasticsearch_dsl.analysis import token_filter, analyzer
from elasticsearch_dsl import Index
from elasticsearch import Elasticsearch


#es=Elasticsearch(['localhost'],http_auth=('elastic', 'changeme'),port=9200)
es=Elasticsearch(['localhost'],port=9200)

ngram_filter = token_filter('ngram_filter',
                            type='nGram',
                            min_gram=1,
                            max_gram=20)

ngram_analyzer = analyzer('ngram_analyzer',
                          type='custom',
                          tokenizer='whitespace',
                          filter=[
                              'lowercase',
                              'asciifolding',
                              ngram_filter
                          ])


class ImdbPipeline(object):

    def __init__(self):
        movies = Index('imdb', using=es)
        movies.doc_type(Movie)
        movies.delete(ignore=404)
        movies.create()

    # insert data into ElasticSearch
    def process_item(self, item, spider):
        movie = Movie()
        movie.meta['id'] = item['movie_id']
        movie.title = item['title']
        movie.film_rating = item['film_rating']
        movie.duration = item['duration']
        movie.genre = item['genre']
        movie.release_date = item['release_date']
        movie.imdb_ratingValue = item['imdb_ratingValue']
        movie.imdb_bestRating = item['imdb_bestRating']
        movie.imdb_ratioCount = item['imdb_ratingCount']
        movie.summary = item['summary']
        movie.storyline = item['storyline']
        movie.director = item['director']
        movie.creator = item['creator']
        movie.writer = item['writer']
        movie.stars = item['stars']
        movie.taglines = item['taglines']
        movie.tagwords = item['tagwords']
        movie.url = item['url']
        movie.req_headers = json.loads(item['req_headers'])
        movie.res_headers = json.loads(item['res_headers'])
        #movie.suggest = item['title'] + item['stars'] + item['creator']
        movie.save(using=es)

        print('[  Elasticsearch  ]  {}'.format(movie))
        return item


# define data mapping and analyzer
class Movie(Document):
    title = Text(fields={'raw':{'type': 'keyword'}})
    film_rating = Text()
    duration = Text()
    genre = Keyword(multi=True)
    release_date = Text()
    imdb_ratingValue = Float()
    imdb_bestRating = Float()
    imdb_ratingCount = Float()
    summary = Text()
    storyline = Text()
    director = Keyword(multi=True)
    creator = Keyword(multi=True)
    writer = Keyword(multi=True)
    stars = Keyword(multi=True)
    taglines = Keyword(multi=True)
    tagwords = Keyword(multi=True)
    url = Keyword(index=False)
    req_headers = Object(enabled=False)
    res_headers = Object(enabled=False)

    suggest = Completion(analyzer=ngram_analyzer,
                         search_analyzer=analyzer('standard'))

    #datePublished = Date()
    #time = Integer()

    class Index:
        name = 'imdb'
