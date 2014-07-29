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
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger( __name__ )
ignore_urls=["http://www.ptt.cc/"]

def util_perf_analyze_log(log):
    for x in ['download', 'uncompress_chk', 'analyze', 'gen_report', 'analyzer']:
        time_start = x + "_start"
        time_end = x + "_end"
        if time_start in log and time_end in log:
            logger.info('%s time_used=%f sec'%(x, log[time_end]-log[time_start]))
        else:
            continue

def get_links_from_content(content):
    soup = BeautifulSoup(content)
    links_list=[]
    for link in soup.findAll('a', href=True):
        _link = link['href']
        links_list.append(_link)
    return links_list

def retrieve_content(link):
    _start=time.time()
    _page_file = urllib2.urlopen(link)
    _page_html = _page_file.read()
    _page_file.close()
    _end=time.time()
    logger.info('download link:%s cost=%f'%(link, _end-_start))
    return _page_html

def convert_short_to_ori_url(short_url):
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

def retrieve_and_span_link(level, indent, page_link, collect):
    if level > 1 or page_link in ignore_urls or page_link in spanned_urls_list:
        return 0

    _indent = '%s    '%indent
    print '%s[%s]'%(_indent, page_link)
    _start = time.time()
    _page_html = _retrieve_content(page_link)
    _end = time.time()
    print 'retrive:%s ,cost=%f'%(page_link, _end-_start)
    soup = BeautifulSoup(_page_html)
    _end = time.time()
    print 'BeautifulSoup:%s ,cost=%f'%(page_link, _end-_start)
    spanned_urls_list.append(page_link)
    _start = time.time()
    total_push_tag=0
    if level==0:
        _push_tag = soup.findAll("span", { "class":"hl push-tag" })
        _reply_tag = soup.findAll("span", { "class":"f1 hl push-tag"})
        total_push_tag = len(_push_tag)+len(_reply_tag)

    for link in soup.findAll('a', href=True):
        #_link = link.get('href')
        _link = link['href']
        if _link and (_link.lower().startswith("http") or _link.lower().startswith("https") or
            (_link.startswith("/bbs/BuyTogether/") and not _link.startswith("/bbs/BuyTogether/index"))):
            _err, _ori_url = _convert_short_to_ori_url(_link)
            if page_link == _ori_url or _ori_url in spanned_urls_list:
                #print 'skip link:%s'%(_ori_url)
                continue
            print '%s[%s]'%(_indent, _ori_url)
            spanned_urls_list.append(_ori_url)
            _retrieve_and_span_link(level+1, _indent, _ori_url, collect)
            collect.append(_ori_url)
            if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
                photo_link_list.append(_link)
    _end = time.time()
    print 'loop:%s ,cost=%f'%(page_link, _end-_start)
    return total_push_tag