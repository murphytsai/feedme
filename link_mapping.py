#!/usr/bin/python
# -*- coding: utf-8 -*-
import feedparser
import urllib2
import urlparse
from BeautifulSoup import BeautifulSoup

import time
import datetime
import socket
import csv
import re
import json

import sqlite3
import logging
import util

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )
ignore_urls=["http://www.ptt.cc/"]
google_api=r'https://www.googleapis.com/urlshortener/v1/url?shortUrl={0}&projection=FULL'
scanlog={}
DB='db.sqlite'
conn=sqlite3.connect(DB)
c = conn.cursor()
c.execute('select source, content from posts')
_all_posts=c.fetchall()
conn.commit()
conn.close()
all_urls=[]
count=0
try:
    for _p in _all_posts:
        content=_p[1]
        soup = BeautifulSoup(content)
        total_push_tag=0
        _push_tag = soup.findAll("span", { "class":"hl push-tag" })
        _reply_tag = soup.findAll("span", { "class":"f1 hl push-tag"})
        total_push_tag = len(_push_tag)+len(_reply_tag)

        for link in soup.findAll('a', href=True):
            #_link = link.get('href')
            _link = link['href']
            if _link and (_link.lower().startswith("http") or _link.lower().startswith("https") or
                (_link.startswith("/bbs/BuyTogether/") and not _link.startswith("/bbs/BuyTogether/index"))):
                if _link in ignore_urls or not _link.startswith('http://goo.gl/'):
                    continue
                _err, _ori_url = util.convert_short_to_ori_url(_link)
                if _link != _ori_url and _ori_url.startswith("https://docs.google.com/"):
                    #logging.info('%s  -->  %s'%(_link, _ori_url))
                    google_stats_api=google_api.format(_link)
                    #logging.info(google_stats_api)
                    stats = util.retrieve_content(google_stats_api)
                    google_url_stats = json.loads(stats)
                    clicks = google_url_stats['analytics']['allTime']['longUrlClicks']
                    all_urls.append((int(clicks), _link))
except:
    pass

finally:
    urls_set = set(all_urls)
    all_urls = list(urls_set)
    all_urls.sort()
    all_urls.reverse()
    for u in all_urls:
        print u