import os
import re
import sys
import time
import random
import logging
import string

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from imdb.items import ImdbItem
from scrapy.utils.project import get_project_settings

#logging.basicConfig()
#logger = logging.getLogger('imdb')
#logger.setLevel(logging.INFO)

class imdbSpider(CrawlSpider):

    settings = get_project_settings()

    name = "imdbSpider"
    allowed_domains = ['imdb.com']

    start_urls = [
        'https://www.imdb.com/search/title?release_date=1980-01-01,'
        ]
    deny_urls = ['']

    with open(settings.get('DENIED_DOMAINS')) as f:
        content = f.readlines()

    no_domains = [x.strip() for x in content]

    no_ext = ['']
    tags = ['a', 'area', 'audio', 'embed', 'iframe', 'img', 'input', 'script', 'source', 'track', 'video', 'form']
    #attrs = ['href', 'src', 'action']
    attrs = ['href']
   
    people_links = {}
    detail_fields = ["Taglines:", "Country:", "Language:", "Budget:", "Cumulative Worldwide Gross:", "Production Co:"]
    director_fields = ["Director:", "Writers:"]

    movie_link = r'/title/\w+/\?ref_=adv_li_tt'
    nextpage_link = r'/search/title\?release_date=1980-01-01,&start=\d+&ref_=adv_nxt'

    rules = (
        Rule(LxmlLinkExtractor(allow=movie_link), callback='parse_movie', follow=False),
        Rule(LxmlLinkExtractor(allow=nextpage_link), follow=True),
        )

    def parse_movie(self, response):

        #logger.info(">>>>> Movie: {}".format(response.request.url))
        print(">>>>> Movie: {}".format(response.request.url))

        # inputs

        _id = response.request.url.split('/')[4]
        title = ''.join(list(filter( lambda x: x in string.printable, response.xpath('//div[@class="title_wrapper"]/h1/text()').extract_first())))
        subtext = ''.join(list(map(str.strip, response.xpath('//div[@class="subtext"]//text()').extract()))).split('|')
        imdb_rating = ''.join(map(str, response.xpath('//div[@class="ratingValue"]/strong/span/text()').extract()))
        #rating_count = ''.join(map(str, response.xpath(response.xpath('//span[@itemprop="ratingCount"]/text()').extract())))
        description = response.xpath('//div[@class="summary_text"]/text()').extract_first().strip() 
        storyline = response.xpath('//div[@id="titleStoryLine"]/div/p/span/text()').extract_first().strip()
        directors = response.xpath('//div[@class="plot_summary "]/div[2][@class="credit_summary_item"]/a/text()').extract()
        writer = response.xpath('//div[@class="plot_summary "]/div[3][@class="credit_summary_item"]/a/text()').extract()
        stars = response.xpath('//div[@class="plot_summary "]/div[4][@class="credit_summary_item"]/a/text()').extract()
        cast = response.xpath('//div[@class="plot_summary "]/div[4][@class="credit_summary_item"]/a/text()').extract()
        taglines = ''.join(response.xpath('//div[@id="titleStoryLine"]/div[@class="txt-block"]/text()').extract()).strip()
        url = response.request.url
        req_headers = response.request.headers
        res_headers = response.headers
        body = response.body


        # Cleaning inputs

        if not _id: return
        if not title: return

        if isinstance(subtext, (list,)):
            film_rating = subtext[0] if len(subtext)>0 else ''
            duration = subtext[1] if len(subtext)>1 else ''
            genre = subtext[2].split(',') if len(subtext)>2 else ''
            release_date = re.sub("[\(\[].*?[\)\]]", "", subtext[3]).strip() if len(subtext)>3 else ''
            country = subtext[3][subtext[3].find("(")+1:subtext[3].find(")")] if len(subtext)>3 else ''                

        imdb_rating = float(imdb_rating) if imdb_rating and imdb_rating.isdigit() else -1
        #rating_count = float(rating_count) if rating_count and rating_count.isdigit() else -1

        description = description if type(description) is str else ''
        storyline = storyline if type(storyline) is str else ''

        if 'See full cast & crew' in cast: cast.remove('See full cast & crew')
        cast = cast

        if body and not isinstance(body, str): body = body.decode('utf-8')

        # Output

        item = ImdbItem()

        item['id'] = _id
        item['title'] = title
        item['film_rating'] = film_rating
        item['duration'] = duration
        item['genre'] = genre
        item['release_date'] = release_date
        item['country'] = country
        item['imdb_rating'] = imdb_rating
        #item['rating_count'] = rating_count
        item['description'] = description
        item['storyline'] = storyline
        item['directors'] = directors
        item['writer'] = writer
        item['stars'] = stars
        item['cast'] = cast
        item['taglines'] = taglines
        item['url'] = url
        item['req_headers'] = req_headers
        item['res_headers'] = res_headers
        item['body'] = body

        yield item
