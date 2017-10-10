# coding=utf8
__author__ = 'Administrator'
import os, sys
os.environ["FURION_ENV"] = "production"
os.environ["MORPH_ENV"] = "production"
# sys.path.append("/home/kratos/src/morph")
# sys.path.append("/home/kratos/src/morph")
import sqlalchemy as sa
import threading
from morph.lib.model.shop import Shop
from wishsdk.ticket import WishTicket


db = sa.create_engine(
    "mysql://%s:%s@%s/%s?charset=utf8" % ("kratos", "3vUbY52IJ2fJq7KwWPeItNrz8", '119.23.150.193', 'fr'),
    echo=False,
    pool_recycle=3600,
    pool_size=30,
    max_overflow=60
)


def search_account():
    # with sessionCM() as session:
    count = 1
    f = open("accounts.text", 'rb')
    shop = Shop()
    while True:
        line = f.readline()
        if not line:
            break
        shop.account = line.strip()
        print "第 %d 个..." % count
        handler = WishTicket(shop)
        result = handler.list_all_tickets()

        if len(result.get("data", [])):
            print line, len(result.get("data", []))
            raw_input("continue ... ")
        count += 1


if __name__ == '__main__':
    print "begin ... "
    search_account()
    print "end ..."
