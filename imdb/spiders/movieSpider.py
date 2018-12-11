import os
import re
import sys
import time
import json
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

    moviesPerPage = '250'
    start_urls = [
        'https://www.imdb.com/search/title?release_date=1980-01-01,&count='+moviesPerPage
        ]
    deny_urls = ['']

    req_num = req_num_page = 0

    with open(settings.get('DENIED_DOMAINS')) as f:
        content = f.readlines()

    no_domains = [x.strip() for x in content]

    no_ext = ['']
    tags = ['a', 'area', 'audio', 'embed', 'iframe', 'img', 'input', 'script', 'source', 'track', 'video', 'form']
    #attrs = ['href', 'src', 'action']
    attrs = ['href']

    link_movie = r'/title/\w*/\?ref_=adv_li_tt'
    link_nextpage = r'/search/title\?release_date=1980-01-01,&count='+moviesPerPage+'&start=\d*&ref_=adv_nxt'

    rules = (
        Rule(LxmlLinkExtractor(allow=link_movie), callback='parse_movie', follow=False),
        Rule(LxmlLinkExtractor(allow=link_nextpage), callback='parse_nextpage', follow=True),
        )

    def parse_nextpage(self, response):
        print("[  PAGE ({})  ]  {}".format(self.req_num_page, response.request.url))
        self.req_num_page += 1

    def parse_reviews(self, response):
        divs = response.xpath('//div[contains(@class, "lister-item mode-detail") and contains(@class, "imdb-user-review") and contains(@class, "collapsable")]//div[@class="content"]/div[@class="text show-more__control"]/text()')
        reviews = [div.extract() for div in divs]
        
        item = response.meta['item']
        item['reviews'] = reviews
        req_num = item['req_num']

        print("[  REVIEWS ({})  ]  {}".format(req_num, response.request.url))

        yield item

    def parse_movie(self, response):

        #logger.info(">>>>> Movie: {}".format(response.request.url))
        print("[  MOVIE ({})  ]  {}".format(self.req_num, response.request.url))

        # inputs

        movie_id = response.request.url.split('/')[4]
        title = ''.join(list(filter( lambda x: x in string.printable, response.xpath('//div[@class="title_wrapper"]/h1/text()').extract_first().strip())))
        film_rating = response.xpath('//div[@class="subtext"]/text()').extract_first()
        duration = response.xpath('//div[@class="subtext"]/time/text()').extract_first()
        genre = response.xpath('//div[@class="subtext"]/a[not(@title="See more release dates")]/text()').extract()
        release_date = response.xpath('//div[@class="subtext"]/a[@title="See more release dates"]/text()').extract_first()

        imdb_ratingValue = response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first()
        imdb_bestRating = response.xpath('//span[@itemprop="bestRating"]/text()').extract_first()
        imdb_ratingCount = response.xpath('//span[@itemprop="ratingCount"]/text()').extract_first()

        summary = response.xpath('//div[@class="summary_text"]/text()').extract_first()
        storyline = response.xpath('//div[@id="titleStoryLine"]/div/p/span/text()').extract_first()

        lables = response.xpath('//div[contains(@class, "plot_summary") and not(@class="plot_summary_wrapper")]/div[@class="credit_summary_item" and not(@class="summary_text")]/h4/text()').extract()
        credits = dict.fromkeys(['director', 'creator' ,'writer' ,'stars'])
        k = 2
        for x in lables:
            persons = response.xpath('//div[contains(@class, "plot_summary") and not(@class="plot_summary_wrapper")]/div['+str(k)+'][@class="credit_summary_item"]/a/text()').extract()

            if 'See full cast & crew' in persons: persons.remove('See full cast & crew')

            # remove comments between brakets or parenthesis
            persons = [re.sub("[\(\[].*?[\)\]]", "", p).strip() for p in persons]

            # director(s), creator(s), writer(s), stars
            if 'director' in x.lower(): credits['director'] = persons
            if 'creator' in x.lower(): credits['creator'] = persons
            if 'writer' in x.lower(): credits['writer'] = persons
            if 'star' in x.lower(): credits['stars'] = persons

            k += 1

        taglines = response.xpath('//div[@id="titleStoryLine"]/div[@class="txt-block"]/text()').extract()
        tagwords = response.xpath('//div[@class="see-more inline canwrap"]/a/span[@class="itemprop"]/text()').extract()

        req_url = response.request.url

        req_headers = self.headers_format(response.request.headers)
        res_headers = self.headers_format(response.headers)

        p = re.compile('/title/\w+/reviews\?ref_=tt_urv')
        links = response.xpath('//div[@id="titleUserReviewsTeaser"]/div[@class="user-comments"]/a/@href').extract()
        request = None
        for link in links:
            if p.match(link):
                url = response.urljoin(link)
                request = scrapy.Request(url, callback=self.parse_reviews, dont_filter=True)
                break

        # Cleaning inputs

        if not movie_id or not title: return

        film_rating = film_rating.strip() if film_rating and type(film_rating) is str  else ''
        release_date = release_date.strip() if release_date and type(release_date) is str  else ''
        duration = duration.strip() if duration and type(duration) is str  else ''

        genre = [g.strip() for g in genre if type(g) is str and len(g)>0 ]
        if len(genre) == 0: genre = ''


        imdb_ratingValue = self.input2num(imdb_ratingValue)
        imdb_ratingCount = self.input2num(imdb_ratingCount)
        imdb_bestRating = self.input2num(imdb_bestRating)

        taglines_clean = []
        for tag in taglines:
            tag = tag.replace('\n', '')
            tag = tag.strip()
            if tag: taglines_clean.append(tag)
        tagwords = [tag.strip() for tag in tagwords]

        summary = summary.strip() if summary and type(summary) is str else ''
        storyline = storyline.strip() if storyline and type(storyline) is str else ''


        # Output

        item = ImdbItem()

        item['movie_id'] = movie_id
        item['title'] = title
        item['film_rating'] = film_rating
        item['duration'] = duration
        item['genre'] = genre
        item['release_date'] = release_date
        item['imdb_ratingValue'] = imdb_ratingValue
        item['imdb_bestRating'] = imdb_bestRating
        item['imdb_ratingCount'] = imdb_ratingCount
        item['summary'] = summary
        item['storyline'] = storyline
        item['director'] = credits.get('director', '')
        item['writer'] = credits.get('writer', '')
        item['creator'] = credits.get('creator', '')
        item['stars'] = credits.get('stars', '')
        item['taglines'] = taglines_clean
        item['tagwords'] = tagwords
        item['reviews'] = None
        item['url'] = req_url
        item['req_headers'] = req_headers
        item['res_headers'] = res_headers

        item['req_num'] = self.req_num
        self.req_num +=1

        if request:
            request.meta['item'] = item
            yield request

        else:
            yield item

    def input2num(self, iput):

        regnum = re.compile("^(?=.*?\d)\d*[.,]?\d*$")
        if iput:
            if iput.isdigit():
                return float(iput)

            oput = iput.replace(",", "")
            if regnum.match(oput):
                return float(oput)
        return -1

    def headers_format(self, header):
        hdr = {}
        for key, value in header.items():
            if isinstance(key, (bytes, bytearray)):
                hdr[key.decode('utf-8')] = b''.join(value).decode('utf-8')
            else:
                hdr[key] = ''.join(value)

        return json.dumps(hdr, ensure_ascii=False)

