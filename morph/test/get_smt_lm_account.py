# coding=utf8
__author__ = 'Administrator'
import os, sys
import datetime
import time
import MySQLdb
from morph.lib.model.shop import Shop
from smtsdk.message import AliMessage


def search_account():
    # with sessionCM() as session:
    count = 1
    f = open("smt_ccounts.text", 'rb')
    shop = Shop()
    shop.session = "0bdf6f64-372d-4b6 a-b68b-5efe64bc18bd"
    shop.site_id = 2
    shop.platform = "AliExpress"
    shop.name = 'Limerence'
    while True:
        line = f.readline()
        if not line:
            break
        shop.account = line.strip()
        print "第 %d 个..." % count
        handler = AliMessage(shop)
        result = handler.get_msg_relation_list(msg_source="order_msg")
        lens = len(result.get("result", []))
        if len(result.get("result", [])):
            print line, len(result.get("result", []))
            raw_input("continue ... ")
        count += 1


if __name__ == '__main__':
    print "begin ... "
    search_account()
    print "end ..."
