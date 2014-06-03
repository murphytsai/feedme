import feedparser
import urllib2
from BeautifulSoup import BeautifulSoup

import time
import socket

ignore_urls=["http://www.ptt.cc/"]
spanned_urls_list=[]
def _retrieve_content(link):
    _page_file = urllib2.urlopen(_page_link)
    _page_html = _page_file.read()
    _page_file.close()
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

def _retrieve_and_span_link(level, indent, page_link):
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
                continue
            #print '%s[%s]'%(_indent, _ori_url)
            _retrieve_and_span_link(level+1, _indent, _ori_url)
            if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
                photo_link_list.append(_link)

CONFIG_FEEDS_URL="http://feeds.feedburner.com/rocksaying"
CONFIG_FEEDS_URL="http://www.mobile01.com/rss/topiclist506.xml"
CONFIG_FEEDS_URL="http://rss.ptt.cc/BuyTogether.xml"
#CONFIG_FEEDS_URL="http://rss.ptt.cc/MacShop.xml"
photo_link_list = []
d=feedparser.parse(CONFIG_FEEDS_URL)
#print d.entries[0].title
for _entry in d.entries:
    _page_link = _entry.link
    #print 'open: ', _page_link
    print 'title: ', _entry.title
    #continue
    _indent="    "
    spanned_urls_list=[]
    level=0
    _retrieve_and_span_link(level, _indent, _page_link)

#photo_link_list.append("http://www.taaze.tw/new_include/images/logo.jpg")
for pl in photo_link_list:
    _filename = pl.split('/')[-1]
    #urllib.urlretrieve(pl, _filename)
print "Done"
