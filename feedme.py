import feedparser
import urllib2
from BeautifulSoup import BeautifulSoup

import time

def _retrieve_content(link):
    _page_file = urllib2.urlopen(_page_link)
    _page_html = _page_file.read()
    _page_file.close()
    return _page_html

CONFIG_FEEDS_URL="http://feeds.feedburner.com/rocksaying"
CONFIG_FEEDS_URL="http://www.mobile01.com/rss/topiclist506.xml"
CONFIG_FEEDS_URL="http://rss.ptt.cc/BuyTogether.xml"
photo_link_list = []
d=feedparser.parse(CONFIG_FEEDS_URL)
#print d.entries[0].title
for _entry in d.entries:
    _page_link = _entry.link
    #print 'open: ', _page_link
    print 'title: ', _entry.title
    continue
    _page_html = _retrieve_content(_page_link)
    soup = BeautifulSoup(_page_html)
    print soup
    break
    for link in soup.findAll('a'):
        _link = link.get('href')
        print '    ', _link
        if _link and (_link.lower().endswith(".jpg") or _link.lower().endswith(".png") or _link.lower().endswith(".bmp")):
            photo_link_list.append(_link)

#photo_link_list.append("http://www.taaze.tw/new_include/images/logo.jpg")
for pl in photo_link_list:
    _filename = pl.split('/')[-1]
    #urllib.urlretrieve(pl, _filename)
print "Done"
