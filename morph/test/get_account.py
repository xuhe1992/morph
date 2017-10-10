# coding=utf8
__author__ = 'Administrator'
import os, sys
os.environ["FURION_ENV"] = "production"
os.environ["MORPH_ENV"] = "production"
sys.path.append("/home/kratos/src/furion")
# sys.path.append("/home/kratos/src/morph")
from furion.lib.model.session import sessionCM
from furion.lib.model.shop import Shop


if __name__ == '__main__':
    with sessionCM() as session:
        shops = session.query(Shop).filter(Shop.platform == "Wish").all()

    with open("/home/kratos/script/accounts.text", 'wb') as f:
        for shop in shops:
            if shop.account:
                f.write(shop.account + '\n')
