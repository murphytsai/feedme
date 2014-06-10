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

import sqlite3

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
    _start=time.time()
    _page_file = urllib2.urlopen(link)
    _page_html = _page_file.read().decode('utf-8')
    _page_file.close()
    _end=time.time()
    print 'download link:%s cost=%f'%(link, _end-_start)
    return _page_html

def _get_page_info(page_link, skip_urls):
    _page={}
    _page[page_link]={}
    _skip_urls = skip_urls
    _page_html = _retrieve_content(page_link)
    soup = BeautifulSoup(_page_html)
    _skip_urls.append(page_link)
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
    soup = BeautifulSoup(_page_html)
    _skip_urls.append(page_link)
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
        DB='feed.db'
        conn=sqlite3.connect(DB)
        conn.text_factory = str
        c = conn.cursor()
        c.execute(_sql,(author.encode('utf-8'), date.encode('utf-8'), title.encode('utf-8'), source.encode('utf-8'), content, links.encode('utf-8')))
        print author.encode('utf-8')
        print date.encode('utf-8')
        print title.encode('utf-8')
        print source.encode('utf-8')
        #print content.encode('utf-8')
        conn.commit()
        conn.close()
    except:
        print 'pass ', source
        pass

DB='db.sqlite'
conn=sqlite3.connect(DB)
c = conn.cursor()
c.execute('''create table if not exists posts 
    (pid INTEGER , author text, postdate text, title text, source text PRIMARY KEY, content text, links text)''')
conn.commit()
conn.close()
_page_link=r'http://www.ptt.cc/bbs/BuyTogether/index%d.html'
ignore_urls=["http://www.ptt.cc/"]
ptt_site="http://www.ptt.cc"
for _index in xrange(2500,2400,-1):
    _site_url=_page_link%_index
    print 'process ', _site_url
    _page_info=_get_page_info(_site_url, ignore_urls)
    for _source, _urls in _page_info.iteritems():
        _ptt_site_urls=[ ptt_site + _u for _u in _urls['inside_links']]
        for _il in _ptt_site_urls:
            _il_page_info=_get_il_page_info(_il, ignore_urls)
            time.sleep(1)
            for _il_source, _il_value in _il_page_info.iteritems():
                #print _il_value['content']
                #print _il_source, _il_value['author'], _il_value['post_date'], _il_value['title'], ','.join(_il_value['inside_links'])
                _a=_il_value['author']
                _s=_il_source
                _d=_il_value['post_date']
                _t=_il_value['title']
                _l=','.join(_il_value['inside_links'])
                _c=_il_value['content']
                _db_insert_one_post(_a,_d,_t,_s,_c,_l)
                time.sleep(4)
        


'''
ignore_urls=["http://www.ptt.cc/"]

def util_perf_analyze_log(log):
    for x in ['download', 'uncompress_chk', 'analyze', 'gen_report', 'analyzer']:
        time_start = x + "_start"
        time_end = x + "_end"
        if time_start in log and time_end in log:
            logger.info('%s time_used=%f sec'%(x, log[time_end]-log[time_start]))
        else:
            continue

def _retrieve_content(link):
    _start=time.time()
    _page_file = urllib2.urlopen(link)
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

def _retrieve_and_span_link(level, indent, page_link, collect):
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

CONFIG_FEEDS_URL={"rocksaying":"http://feeds.feedburner.com/rocksaying",
            "buytogether":"http://rss.ptt.cc/BuyTogether.xml",
            "mobile01":"http://www.mobile01.com/rss/topiclist506.xml",
            "macshop":"http://rss.ptt.cc/MacShop.xml"}
scanlog={}
#CONFIG_FEEDS_URL="http://rss.ptt.cc/MacShop.xml"
photo_link_list = []
site="rocksaying"
site="buytogether"
#site="macshop"
#d=feedparser.parse(CONFIG_FEEDS_URL[site])
_indent="    "
link_dict={}
link_dict["inside_links"]=[]
spanned_urls_list=ignore_urls
_page_link=r'http://www.ptt.cc/bbs/BuyTogether/index.html'
#_page_link='http://www.ptt.cc/bbs/BuyTogether/index2570.html'
level=0
all_urls = []
for _index in xrange(2570,2568,-1):
    _site_url=_page_link%_index
    _retrieve_and_span_link(level, _indent, _site_url, link_dict["inside_links"])
    all_urls += link_dict["inside_links"]
    link_dict["inside_links"] = []
    time.sleep(1)

link_collect=[]
with open('%s.csv'%site, 'awb') as _csv:
    _csv_writer = csv.writer(_csv)
    for _entry in all_urls:
        link_dict={}
        ptt_site="http://www.ptt.cc"
        link_dict["title_link"]=ptt_site+_entry
        """
        link_dict["published"]=_entry.published
        link_dict["author"]=_entry.author
        _title = _entry.title
        _title_enc=_entry.title.encode('utf8')
        _title_split = re.match(ur"\[(.*[\u2E80-\u9FFF]+)\](.*)-(.*)", _title_enc.decode('utf8'))
        try:
            _title_type = _title_split.group(1)
            _title_subtitle = _title_split.group(2)
            _title_how = _title_split.group(3)
        except:
            _title_type = ""
            _title_subtitle = ""
            _title_how = ""
            print 'cant parse:', _title

        link_dict["title_title"]=_title.strip()
        link_dict["title_type"]=_title_type.strip()
        link_dict["title_subtitle"]=_title_subtitle.strip()
        link_dict["title_how"]=_title_how.strip()
        link_dict["title_link"]=_entry.link
        """
        _page_link = link_dict["title_link"]
        #print 'open: ', _page_link
        #continue
        _indent="    "
        spanned_urls_list=ignore_urls
        level=0
        link_dict["inside_links"]=[]
        link_dict["cnt_push_tag"] = _retrieve_and_span_link(level, _indent, _page_link, link_dict["inside_links"])
        #print link_dict["inside_links"]
        #_row = '%s , %s , %s\n'%(link_dict["title_name"],link_dict["title_link"],' , '.join(link_dict["inside_links"]))
        _row=[]
        #_row.append(link_dict["published"])
        _row.append(link_dict["cnt_push_tag"])
        #_row.append(link_dict["author"])
        #_row.append(link_dict["title_name"].encode('big5'))
        #_row.append(link_dict["title_title"].encode('big5'))
        #_row.append(link_dict["title_type"].encode('big5'))
        #_row.append(link_dict["title_subtitle"].encode('big5'))
        #_row.append(link_dict["title_how"].encode('big5'))
        _row.append(link_dict["title_link"].encode('utf-8'))
        _site_set=set()
        for _lnk in link_dict["inside_links"]:
            _url=_lnk.encode('utf-8')
            _site_set.add(urlparse.urlparse(_url).netloc)
            _row.append(_lnk.encode('utf-8'))
        for _s in _site_set:
            _row.append(_s)
        _csv_writer.writerow(_row)


#photo_link_list.append("http://www.taaze.tw/new_include/images/logo.jpg")
for pl in photo_link_list:
    _filename = pl.split('/')[-1]
    #urllib.urlretrieve(pl, _filename)
print "Done"
'''
    
