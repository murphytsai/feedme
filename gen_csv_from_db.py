#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup

import time
import csv
import re

import sqlite3
import logging
import argparse
from termcolor import colored

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger( __name__ )

class style:
    BOLD = '\033[1m'
    END = '\033[0m'


def util_perf_analyze_log(log):
    for x in ['download', 'uncompress_chk', 'analyze', 'gen_report', 'analyzer', 'parse']:
        time_start = x + "_start"
        time_end = x + "_end"
        if time_start in log and time_end in log:
            logging.info('%s time_used=%f sec'%(x, log[time_end]-log[time_start]))
        else:
            continue

def get_push_cnt(content):
    soup = BeautifulSoup(content)
    _push_tag=_reply_tag=0
    _push_tag = soup.findAll("span", { "class":"hl push-tag" })
    _reply_tag = soup.findAll("span", { "class":"f1 hl push-tag"})
    return len(_push_tag)+len(_reply_tag)

def gen_csv_from_db(db_path, output_name):
    scanlog={}
    DB=db_path
    conn=sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('select postdate, author, title, source, links, content from posts')
    _all_posts=c.fetchall()
    conn.commit()
    conn.close()
    with open(output_name, 'wb') as _csv:
        _csv_writer = csv.writer(_csv)
        for _p in _all_posts:
            scanlog['parse_start']=time.time()
            _title=_p[2]
            _title_enc=_title.encode('utf8')
            _title_split = re.match(ur"\[(.*[\u2E80-\u9FFF]+)\](.*)-(.*)", _title_enc.decode('utf8'))
            _title_type=_title_subtitle=_title_how=_date=_author=None
            try:
                _title_type = _title_split.group(1).strip()
            except:
                _title_type = ""
            try:
                if _title_split.group(2):
                    _title_subtitle = _title_split.group(2).strip().encode('big5')
                else:
                    _title_subtitle=""
            except UnicodeEncodeError:
                _title_subtitle = _title_split.group(2).strip().encode('utf8')
            except:
                _title_subtitle = ""
            try:
                _title_how = _title_split.group(3).strip()
            except:
                _title_how = ""
            try:
                _date = _p[0].strip().encode('big5')
            except:
                _date = ""
            try:
                _author = _p[1].strip().encode('big5')
            except:
                try:
                    _author = _p[1].strip().encode('utf-8')
                except:
                    _author = ""

            _row=[]
            _row.append(_date)
            _row.append(_author)
            _row.append(_title_type.encode('big5'))
            _row.append(_title_subtitle)
            _row.append(_title_how.encode('big5'))
            _row.append(get_push_cnt(_p[5]))
            _row.append(_p[3].strip().encode('big5'))
            _row.append(_p[4].strip().encode('utf-8'))
            _csv_writer.writerow(_row)
            scanlog['parse_end']=time.time()
            util_perf_analyze_log(scanlog)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='gen_csv_from_db', description="generate csv by sqlite db")
    parser.add_argument('--log-lvl', '--lvl', help="change log verbosity", dest="loglevel", choices=["DEBUG","INFO","WARNING","ERROR"], default="WARNING")
    parser.add_argument('-i', '--input', dest='db_path', help="/from/to/sqlite.db", default="db.sqlite")
    parser.add_argument('-o', '--output', dest='output_name', help="/from/to/output_name", default="db.csv")
    args=parser.parse_args()

    loglevel=logging.WARNING
    if args.loglevel=="ERROR":
        loglevel=logging.ERROR
    elif args.loglevel=="DEBUG":
        loglevel=logging.DEBUG
    elif args.loglevel=="INFO":
        loglevel=logging.INFO
    else:
        loglevel=logging.WARNING
    logging.basicConfig(format='%(asctime)-15s - %(levelname)-5s - %(message)s')
    logging.getLogger().setLevel(loglevel)

    db_path = args.db_path
    output_name = args.output_name
    print colored(style.BOLD + 'db_path=%s' + style.END, 'green') % db_path
    print colored(style.BOLD + 'output_name=%s' + style.END, 'red') % output_name
    gen_csv_from_db(db_path, output_name)
