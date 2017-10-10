# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import re
import traceback
import ujson as json
from sqlalchemy import and_
from morph.lib.utils.logger_util import logger
from morph.lib.model.session import sessionCM
from morph.lib.model.manage import Management
from morph.lib.model.shop import Shop
from morph.lib.model.channel import Channel
from morph.lib.model.evaluation import Evaluation
from morph.controls import CustomerControls
from morph.controls.amazon import AmazonCustomer
from morph.controls.ebay import EbayCustomer
from morph.controls.ebay.ctrl import EbayControls
from morph.controls.smt.ctrl import SmtControls
from morph.controls.wish.ctrl import WishControls
from morph.controls.smt import SmtCustomer
from morph.controls.wish import WishCustomer
from morph.lib.utils.exc import MissArgumentError
from morph.views.base import BaseHandler


class CustomerHandler(BaseHandler):

    controls_map = {
        "AliExpress": SmtCustomer,
        "Amazon": AmazonCustomer,
        "eBay": EbayCustomer,
        "Wish": WishCustomer,
    }
    control_route = {
        "eBay": EbayControls,
        "AliExpress": SmtControls,
        "Wish": WishControls
    }

    def get(self, *args, **kwargs):
        logger_dict = {"args": args, "kwargs": kwargs, "params": self.params, "method": "GET"}
        print logger_dict
        method_route = {
            "channel": self.list_channel,
            "message": self.list_message,
            "channel/search": self.search_channel,
        }

        try:
            shop = self.get_shop()
            if not shop:
                self.write({"status": 0, "message": "错误的店铺ID、ChannelID、EvaluationID！"})
                return

            control = self.control_route[shop.platform](shop, **self.params)
            action = args[0]
            result = method_route[action](control)
            self.write(result)

            # if action == "channel":
            #     self.render("index.html", **result)
            # else:
            #     self.write(result)
        except Exception, e:
            logger.error(traceback.format_exc(e))
            self.write({"status": 0, "data": traceback.format_exc(e)})

    def post(self, *args, **kwargs):
        logger_dict = {"args": args, "kwargs": kwargs, "params": self.params, "method": "POST"}
        print logger_dict
        method_route = {
            "task": self.sync_customer,
            "message": self.reply_message,
        }

        action = args[0]
        if action == "sync":
            handler = CustomerControls(self.current_user, self.params)
            self.write(self.sync_customer(handler))
        else:
            shop = self.get_shop()
            if not shop:
                self.write({"status": 0, "message": "错误的店铺ID、ChannelID、EvaluationID！"})
                return
            self.write(method_route[action](self.control_route[shop.platform](shop, **self.params)))

        # # 回复消息
        # if action == "message" and shop_id:
        #     print "reply message !"
        #     with sessionCM() as session:
        #         shop = Shop.find_by_id(session, shop_id='7612')
        #         shop.token = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
        #         shop.site_id = "0"
        #     handler = EbayControls(shop, **self.params)
        #     self.write(self.reply_message(handler))
        #     handler.immediately_sync_message(shop)

    def put(self, *args, **kwargs):
        logger_dict = {"args": args, "kwargs": kwargs, "params": self.params, "method": "POST"}
        print logger_dict
        method_route = {
            "channel/state": self.change_state,
            "channel/flag": self.change_flag,
            "channel/read": self.change_read,
        }

        action = args[0]
        if str(action).endswith("/"):
            action = action[:len(action)-1]
        if self.params.get("deal", ""):
            action = str(action) + "/state"
        elif self.params.get("rank", ""):
            action = str(action) + "/state"
        else:
            action = str(action) + "/read"

        shop = self.get_shop()
        if not shop:
            self.write({"status": 0, "message": "错误的店铺ID、ChannelID、EvaluationID！"})
            return
        self.write(method_route[action](self.control_route[shop.platform](shop, **self.params)))

    def sync_customer(self, controls):
        self.check_params("sync")
        return controls.sync_customer()

    def list_channel(self, controls):
        self.check_params("channel")
        return controls.list_channel()

    def search_channel(self, controls):
        self.check_params("search")
        return controls.search_channel()

    def list_message(self, controls):
        self.check_params("message")
        return controls.list_message()

    def reply_message(self, controls):
        self.check_params("reply")
        return controls.reply_message()

    def change_state(self, controls):
        self.check_params("state")
        return controls.update_channel_state()

    def change_flag(self, controls):
        self.check_params("flag")
        return controls.update_channel_flag()

    def change_read(self, controls):
        self.check_params("read")
        return controls.update_channel_read()

    def check_params(self, route):
        dic = {
            "sync": {
                "shop_id": "#@\d+",
                "platform": "#@\d+",
            },
            "channel": {},
            "search": {},
            "message": {},
            "reply": {},
        }
        for key, value in dic[route].items():
            command, expression = value.split("@")
            if command == "#" and not self.params.get(key):
                continue
            elif command == "$":
                try:
                    json.loads(self.params.get(key))
                except (ValueError, TypeError):
                    raise MissArgumentError
            else:
                pattern = re.compile(value.strip("#"))
                if not pattern.match(self.params.get(key, "")):
                    raise MissArgumentError

    def get_shop(self):
        shop_id = self.params.get("shop_id", "1")
        with sessionCM() as session:
            shop = Shop.find_by_id(session, "7612")
            shop.token = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
            shop.site_id = "0"
            # shop = Shop.find_by_id(session, shop_id)
            # if not shop:
            #     self.write({"status": 0, "data": "店铺不存在！"})
            #     return ""
            # managements = Management.find_management(session, self.current_user.id, shop.id)
            #
            # if not managements:
            #     self.write({"status": 0, "data": "您没有管理此店铺权限，请让主账号在“账户管理”中添加店铺授权！"})
            #     return ""
            # shop = Shop.find_by_id(session, '7982')
            # shop.platform = 'AliExpress'
            # shop.account = '1be0afca-412a-42a1-b1f3-bc4b34e9bf0b'
            # shop.site_id = 2
            # shop.session = '0bdf6f64-372d-4b6a-b68b-5efe64bc18bd'
            # shop.owner = 'cn1518284505qzvx'
        return shop


        # shop_id = self.params.get("shop_id", "")
        # with sessionCM() as session:
        #     if not shop_id:
        #         if self.params.get("channel_id", ""):
        #             channel = Channel.find_by_id(session, channel_id=self.params.get("channel_id"))
        #             shop_id = str(channel.shop_id) if channel else ""
        #         elif self.params.get("evaluation_id", ""):
        #             evaluation = Evaluation.find_by_id(session, evaluation_id=self.params.get("evaluation_id"))
        #             shop_id = str(evaluation.shop_id) if evaluation else ""
        #         else:
        #             shop_id = ""
        #
        #     managements = Management.find_by_user_id(session, self.current_user.id)
        #     shop_ids = [str(item.shop_id) for item in managements]
        #     if shop_id in shop_ids:
        #         return Shop.find_by_id(session, shop_id)
        #     else:
        #         return None







