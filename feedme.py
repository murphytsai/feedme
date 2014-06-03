#!/usr/bin/python
# -*- coding: utf-8 -*-
import feedparser
import urllib2
from BeautifulSoup import BeautifulSoup

import time
import socket
import csv

ignore_urls=["http://www.ptt.cc/"]

def _retrieve_content(link):
    _start=time.time()
    _page_file = urllib2.urlopen(_page_link)
    _page_html = _page_file.read()
    _page_file.close()
    _end=time.time()
    print 'download link:%s cost=%f'%(link, _end-_start)
    return _page_html

def _convert_short_to_ori_url(short_url):
    ori_url=short_url
    try:
        if short_url in ignore_urls:
            #return '[i]:%s'%ori_url
            return ori_url
        request = urllib2.urlopen(urllib2.Request(url=short_url, headers = {'User-Agent':'Mozilla/8.0 (compatible; MSIE 8.0; Windows 7)'}))
        socket.setdefaulttimeout(5)
        ori_url = request.url
        return ori_url
        """
        if short_url != ori_url:
            return '[#]:%s --> %s'%(short_url, ori_url)
        else:
            return '[=]:%s'%ori_url
        """
    except:
        #print short_url, 'no change'
        return '[=]:%s'%ori_url

def _retrieve_and_span_link(level, indent, page_link, collect):
    if level > 1 or page_link in ignore_urls or page_link in spanned_urls_list:
        return

    _indent = '%s    '%indent
    print '%s[%s]'%(_indent, page_link)
    _page_html = _retrieve_content(page_link)
    soup = BeautifulSoup(_page_html)
    spanned_urls_list.append(page_link)
    for link in soup.findAll('a'):
        _link = link.get('href')
        if _link and (_link.lower().startswith("http") or _link.lower().startswith("https")):
            _ori_url = _convert_short_to_ori_url(_link)
            if page_link == _ori_url or _ori_url in spanned_urls_list:
                #print 'skip link:%s'%(_ori_url)
                continue
            #print '%s[%s]'%(_indent, _ori_url)
            spanned_urls_list.append(_ori_url)
            _retrieve_and_span_link(level+1, _indent, _ori_url, collect)
            collect.append(_ori_url)
            if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
                photo_link_list.append(_link)

CONFIG_FEEDS_URL="http://feeds.feedburner.com/rocksaying"
CONFIG_FEEDS_URL="http://www.mobile01.com/rss/topiclist506.xml"
CONFIG_FEEDS_URL="http://rss.ptt.cc/BuyTogether.xml"
#CONFIG_FEEDS_URL="http://rss.ptt.cc/MacShop.xml"
photo_link_list = []
d=feedparser.parse(CONFIG_FEEDS_URL)
#print d.entries[0].title
link_collect=[]
with open('./out.csv', 'awb') as _csv:
    _csv_writer = csv.writer(_csv, delimiter=' ')
    for _entry in d.entries:
        link_dict={}
        link_dict["title_name"]=_entry.title
        link_dict["title_link"]=_entry.link
        _page_link = _entry.link
        #print 'open: ', _page_link
        print 'title: ', _entry.title
        #continue
        _indent="    "
        spanned_urls_list=ignore_urls
        level=0
        link_dict["inside_links"]=[]
        _retrieve_and_span_link(level, _indent, _page_link, link_dict["inside_links"])
        #print link_dict["inside_links"]
        _row = '%s , %s , %s\n'%(link_dict["title_name"],link_dict["title_link"],' , '.join(link_dict["inside_links"]))
        _row=[]
        _row.append(link_dict["title_name"].encode('utf-8'))
        _row.append(link_dict["title_link"].encode('utf-8'))
        for _lnk in link_dict["inside_links"]:
            _row.append(_lnk.encode('utf-8'))

        _csv_writer.writerow(_row)
        break
        #print _row.encode('utf-8')


#photo_link_list.append("http://www.taaze.tw/new_include/images/logo.jpg")
for pl in photo_link_list:
    _filename = pl.split('/')[-1]
    #urllib.urlretrieve(pl, _filename)
print "Done"

#if __name__=="__main__":

