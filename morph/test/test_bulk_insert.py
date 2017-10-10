# coding=utf8
__author__ = 'Administrator'
import os, sys
import datetime
import time
import MySQLdb
os.environ["FURION_ENV"] = "development"
sys.path.append("/home/kratos/src/morph")
from sqlalchemy.sql import table, column, select, and_
from morph.lib.model.session import sessionCM
from morph.lib.model.base import db
from morph.lib.model.message import Message
from morph.lib.model.channel import Channel
from morph.lib.model.attachment import Attachment

# conn_kw = {
#     # "host": "10.1.15.194",
#     "host": "localhost",
#     "user": "root",
#     "passwd": "qZeEg43S34j3wzMW89MUPcOSS",
#     "db": "fr",
#     "charset": "utf8"
# }
# db = MySQLdb.connect(**conn_kw)


def bulk_insert(session, count=1, step=10000, flag="a"):
    kw = {
        "shop_id": 1,
        "seller_id": "1",
        "seller_name": "1",
        "buyer_id": "1",
        "buyer_name": "1",
        "read_stat": 1,
        "deal_stat": 1,
        "open_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "close_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "closed_by": "1",
        "origin_id": "1",
        "relation_id": "1",
        "relation_type": "1",
        "last_msg_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "last_msg_id": "1",
        "last_msg_content": u"测试数据"
    }
    for i in range(1, count+1):
        kw["seller_id"] = str(int(kw["seller_id"]) + i)
        channel = Channel.create(session, **kw)
        print "第 %d 个 %d 万" % ( i, step/10000)
        msgs = [dict(channel_id=channel.id, origin_id=str(1+j) + flag, content=u"测试数据",
                     receive_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                     source="1"
                  ) for j in xrange(1, step+1)]

        # session.bulk_insert_mappings(Message, msgs)
        # msgs = list()
        # for j in xrange(1, step+1):
        #     m = Message()
        #     m.channel_id = channel.id
        #     m.origin_id=str(1+j) + flag
        #     m.content=u"测试数据"
        #     m.receive_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        #     m.source="1"
        #     msgs.append(m)
        db.execute(Message.__table__.insert(), msgs)
        # session.bulk_save_objects(msgs)
        session.commit()


def bulk_insert_N(session, cursor, count=1, step=10000, flag="a"):

    insert_sql = "INSERT INTO message (channel_id, origin_id, content, image_urls, receive_time, source)" \
                 "VALUES (%s, %s, %s, %s, %s, %s)"

    kw = {
        "shop_id": 1,
        "seller_id": "1",
        "seller_name": "1",
        "buyer_id": "1",
        "buyer_name": "1",
        "read_stat": 1,
        "deal_stat": 1,
        "open_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "close_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "closed_by": "1",
        "origin_id": "1",
        "relation_id": "1",
        "relation_type": "1",
        "last_msg_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "last_msg_id": "1",
        "last_msg_content": u"测试数据"
    }
    for i in range(1, count + 1):
        kw["seller_id"] = str(int(kw["seller_id"]) + i)
        channel = Channel.create(session, **kw)
        print "第 %d 个 %d 万" % (i, step / 10000)
        msgs = ((channel.id, str(1 + j) + flag, "asd", "test_data",
                 datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "1") for j in xrange(1, step + 1))
        cursor.executemany(insert_sql, msgs)
        # session.bulk_insert_mappings(Message, msgs)
        # msgs = list()
        # for j in xrange(1, step+1):
        #     m = Message()
        #     m.channel_id = channel.id
        #     m.origin_id=str(1+j) + flag
        #     m.content=u"测试数据"
        #     m.receive_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        #     m.source="1"
        #     msgs.append(m)
        # # db.execute(Message.__table__.insert().values(msgs))
        # session.bulk_save_objects(msgs)
        # session.commit()


def select_something(session):
    # msgs = session.query(Message).filter(Message.origin_id.like("%11c%"), ).all()
    # msgs = session.query(Message).filter(Message.channel_id == 706).order_by(Message.receive_time.desc()).offset(10).limit(10).all()
    # count = session.query(Message).filter(Message.channel_id == 706).order_by(Message.receive_time.desc()).offset(10).limit(10).count()
    # print len(msgs)
    # print count
    # for msg in msgs:
    #     print msg.id, msg.channel_id, msg.origin_id, msg.receive_time
    x = getattr(Channel, "buyer_name").ilike("%e%")
    y = getattr(Channel, "shop_id") == '7612'
    cc = [x, y]
    print x
    condition = and_(*cc)
    channels = session.query(Channel).filter(and_(*cc)).all()
    # channels = session.query(Channel).filter(Channel.shop_id).all()
    for item in channels:
        print item.id, item.buyer_name


if __name__ == "__main__":
    start = time.time()
    with sessionCM() as session:
        # bulk_insert(session,  count=1, flag="e", step=10000)
        select_something(session)
    # print type(db)
    # with sessionCM() as session:
    #     bulk_insert_N(session, db.cursor(), count=10)
    print "End!"
    end = time.time()
    print end - start
