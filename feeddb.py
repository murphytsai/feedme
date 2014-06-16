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
import random
import sqlite3
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger( __file__)

photo_link_list=[]

def _random_sleep():
    _time=random.randrange(1, 20, 5)
    logger.info('ready to sleep: %d sec'%_time)
    time.sleep(_time)
    logger.info('finish sleeping')

def _convert_short_to_ori_url(short_url):
    ori_url=short_url
    try:
        if short_url in ignore_urls:
            #return '[i]:%s'%ori_url
            return 0, ori_url
        request = urllib2.urlopen(urllib2.Request(url=short_url, headers = {'User-Agent':'Mozilla/8.0 (compatible; MSIE 8.0; Windows 7)'}))
        socket.setdefaulttimeout(5)
        ori_url = request.url
        return 1, ori_url
        """
        if short_url != ori_url:
            return '[#]:%s --> %s'%(short_url, ori_url)
        else:
            return '[=]:%s'%ori_url
        """
    except:
        #print short_url, 'no change'
        return -1, ori_url

def _retrieve_content(link):
    while 1:
        _start=time.time()
        try:
            _page_file = urllib2.urlopen(urllib2.Request(url=link, headers = {'User-Agent':'Mozilla/8.0 (compatible; MSIE 8.0; Windows 7)'}))
        except urllib2.HTTPError, e:
            logger.warning(e)
            if e.code == 500 or e.code==503:
                logger.info('sleep '+link)
                _random_sleep()
                continue
            elif e.code == 404:
                logger.warning(link + ' 404 not found.')
                return None
        except urllib2.URLError, e:
            logger.warning(e)
            logger.warning(e.reason)
            logger.warning('sleep '+link)
            return None
        else:
            _page_html = _page_file.read().decode('utf-8')
            _page_file.close()
            _end=time.time()
            logger.info('download link:%s cost=%f'%(link, _end-_start))
            return _page_html

def _get_page_info(page_link, skip_urls):
    _page={}
    _page[page_link]={}
    _skip_urls = skip_urls
    _page_html = _retrieve_content(page_link)
    _skip_urls.append(page_link)
    if not _page_html:
        return None

    soup = BeautifulSoup(_page_html)
    _page[page_link]['inside_links']=[]
    _link_set = set()
    for link in soup.findAll('a', href=True):
        _link = link['href']
        if _link and (_link.lower().startswith("http") or _link.lower().startswith("https") or
            (_link.startswith("/bbs/BuyTogether/") and not _link.startswith("/bbs/BuyTogether/index"))):
            _err, _ori_url = _convert_short_to_ori_url(_link)
            if page_link == _ori_url or _ori_url in _skip_urls:
                #print 'skip link:%s'%(_ori_url)
                continue
            _link_set.add(_ori_url)
            if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
                photo_link_list.append(_link)
    _page[page_link]['inside_links']=list(_link_set)
    return _page

def _get_il_page_info(page_link, skip_urls):
    _page={}
    _page[page_link]={}
    _skip_urls = skip_urls
    _page_html = _retrieve_content(page_link)
    _skip_urls.append(page_link)
    if not _page_html:
        return None 

    soup = BeautifulSoup(_page_html)
    _page[page_link]['inside_links']=[]
    _link_set = set()
    _page_data = soup.findAll("span", { "class":"article-meta-value" })
    
    try:
        _page[page_link]['author'] = _page_data[0].string
    except:
        _page[page_link]['author'] = ""
    try:
        _page[page_link]['title'] = _page_data[2].string
    except:
        _page[page_link]['title'] = ""
    try:
        _page[page_link]['post_date'] = _page_data[3].string
    except:
        _page[page_link]['post_date'] = ""

    _page[page_link]['content'] = _page_html

    for link in soup.findAll('a', href=True):
        _link = link['href']
        if _link and (_link.lower().startswith("http") or _link.lower().startswith("https") or
            (_link.startswith("/bbs/BuyTogether/") and not _link.startswith("/bbs/BuyTogether/index"))):
            _err, _ori_url = _convert_short_to_ori_url(_link)
            if page_link == _ori_url or _ori_url in _skip_urls:
                #print 'skip link:%s'%(_ori_url)
                continue
            _link_set.add(_ori_url)
            if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
                photo_link_list.append(_link)
    _page[page_link]['inside_links']=list(_link_set)
    return _page

def _db_insert_one_post(author,date,title,source,content,links):
    try:
        _sql="INSERT INTO posts (pid, author, postdate, title, source, content, links)values(null, ?,?,?,?,?,?)"
        DB='db.sqlite'
        conn=sqlite3.connect(DB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute(_sql,(author.encode('utf-8'), date.encode('utf-8'), title.encode('utf-8'), source.encode('utf-8'), content, links.encode('utf-8')))
        logger.info(author.encode('utf-8'))
        logger.info(date.encode('utf-8'))
        logger.info(title.encode('utf-8'))
        logger.info(source.encode('utf-8'))
        #logger.info(content.encode('utf-8'))
        conn.commit()
        conn.close()
    except:
        logger.info('pass '+ source)
        pass

DB='db.sqlite'
conn=sqlite3.connect(DB)
c = conn.cursor()
c.execute('''create table if not exists posts 
    (pid INTEGER , author text, postdate text, title text, source text PRIMARY KEY, content text, links text)''')
conn.commit()
conn.close()

conn=sqlite3.connect(DB)
c = conn.cursor()
c.execute('select source from posts')
_processed_urls=[]
for _s in c:
    _processed_urls.append(_s[0])
conn.commit()
conn.close()
_page_link=r'http://www.ptt.cc/bbs/BuyTogether/index%d.html'
ignore_urls=["http://www.ptt.cc/"]
ptt_site="http://www.ptt.cc"
ignore_urls+=_processed_urls
for _index in xrange(2577,2500,-1):
    _site_url=_page_link%_index
    logger.info('process '+ _site_url)
    _page_info=_get_page_info(_site_url, ignore_urls)
    if not _page_info:
        continue
    for _source, _urls in _page_info.iteritems():
        _ptt_site_urls=[ ptt_site + _u for _u in _urls['inside_links']]
        for _il in _ptt_site_urls:
            if _il in ignore_urls:
                logger.info('--> processed & pass' +_il) 
                continue
            _il_page_info=_get_il_page_info(_il, ignore_urls)
            if not _il_page_info:
                continue
            _random_sleep()
            for _il_source, _il_value in _il_page_info.iteritems():
                #print _il_value['content']
                #print _il_source, _il_value['author'], _il_value['post_date'], _il_value['title'], ','.join(_il_value['inside_links'])
                logger.info(_il_source)
                _a=_il_value['author']
                _s=_il_source
                _d=_il_value['post_date']
                _t=_il_value['title']
                _l=','.join(_il_value['inside_links'])
                _c=_il_value['content']
                _db_insert_one_post(_a,_d,_t,_s,_c,_l)
                _random_sleep()
       
