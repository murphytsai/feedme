from django.test import TestCase
from django.utils import timezone
from django.db import models

class Author(models.Model):
    idname=models.CharField(max_length=30)
    nickname=models.CharField(max_length=30)

    def __unicode__(self):
        return self.idname

class Link(models.Model):
    short_link=models.CharField(max_length=256)
    long_link=models.CharField(max_length=256)
    click_counter=models.IntegerField(default=0)

    def __unicode__(self):
        return self.short_link

class Post(models.Model):
    title=models.CharField(max_length=256)
    post_date=models.DateTimeField()
    author=models.ForeignKey(Author)
    source_link=models.CharField(max_length=256)
    content=models.TextField()
    links=models.ManyToManyField(Link)
    author_from=models.CharField(max_length=64)

    def __unicode__(self):
        return '%s %s %s'% (self.author, self.title, self.post_date)

class Comment(models.Model):
    pid = models.ForeignKey(Post)
    aid = models.ForeignKey(Author)
    post_date=models.DateTimeField()
    type=models.IntegerField()
    content=models.TextField()

    def __unicode__(self):
        return self.content


class ImportOldDB(TestCase):
    def test_create_db(self):
        import feedparser
        import urllib2
        import urlparse
        from BeautifulSoup import BeautifulSoup
        from datetime import datetime
        import time
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
        DB='/Users/momo/Code/github/feedme/bbs/bbs/db.sqlite'
        conn=sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('select author, postdate, title, source, content, links from posts')
        _all_posts=c.fetchall()
        conn.commit()
        conn.close()
        all_urls=[]
        count=0
        try:
            for _p in _all_posts:
                author=_p[0]
                author=author[:author.find(' (')]
                _db_author = Author.objects.filter(idname="%s"%author)
                if not _db_author:
                    _db_author = Author()
                    _db_author.idname = author
                    _db_author.save()
                    print 'new Author %s is created' % author
                else:
                    _db_author=_db_author[0]

                links=_p[5]
                links_list = links.split(',')
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
                        print 'new Link %s is created' % _db_link
                    else:
                        _db_link=_db_link[0]
                        print 'Link %s is existed!' % _db_link
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
                if count >5:
                    break
            posts=Post.objects.all()
            print posts
        except:
            print 'failed !'
