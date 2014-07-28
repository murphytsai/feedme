from models import *
import feedparser
import urllib2
import urlparse
from datetime import datetime
import time
import socket
import csv
import re
import json

import sqlite3
import logging
import util
import os

logging.basicConfig(level=logging.error)
logger = logging.getLogger( __name__ )
ignore_urls=["http://www.ptt.cc/"]
google_api=r'https://www.googleapis.com/urlshortener/v1/url?shortUrl={0}&projection=FULL'
scanlog={}
DB=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../db.sqlite')
conn=sqlite3.connect(DB)
c = conn.cursor()
c.execute('select author, postdate, title, source, content, links from posts')
_all_posts=c.fetchall()
conn.commit()
conn.close()
all_urls=[]
count=0
for _p in _all_posts:
    try:
        author=_p[0]
        if _p[0] == "" or _p[1]=="" or _p[2]=="":
            continue

        author=author[:author.find(' (')]
        _db_author = Author.objects.filter(idname="%s"%author)
        if not _db_author:
            _db_author = Author()
            _db_author.idname = author
            _db_author.save()
            logger.info('new Author %s is created' % author)

        _db_content=_p[4]
        links_list = util.get_links_from_content(_db_content)
        db_link_list=[]
        for link in links_list:
            _db_link = Link.objects.filter(short_link=link)
            if not _db_link:
                _db_link = Link(short_link=link)
                _err, _ori_url = util.convert_short_to_ori_url(link)
                _db_link.long_link = _ori_url
                if link.startswith('http://goo.gl/'):
                    google_stats_api=google_api.format(link)
                    stats = util.retrieve_content(google_stats_api)
                    google_url_stats = json.loads(stats)
                    clicks = google_url_stats['analytics']['allTime']['longUrlClicks']
                    _db_link.click_counter=clicks
                _db_link.save()
                logger.info('new Link %s is created' % _db_link)
            db_link_list.append(_db_link)

        post = Post()
        db_posttime = _p[1]
        dt=datetime.strptime(db_posttime, '%c')
        post.title=_p[2]
        post.post_date=dt
        post.author=_db_author
        post.source_link=_p[3]
        post.content=_p[4]
        post.author_from=""
        post.save()
        for _dl in db_link_list:
            post.links.add(_dl)
        post.save()
        count += 1
        logger.info('[%d] record is added'%count)
        # if count >5:
        #     break
    #posts=Post.objects.all()
    #print posts
    except:
        logger.error('failed !------------------------------')
        logger.error(_p[0])
        logger.error(_p[1])
        logger.error(_p[2])
        logger.error(_p[3])
        logger.error('failed !++++++++++++++++++++++++++++++')
