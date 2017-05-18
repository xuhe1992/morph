# -*- coding=utf-8 -*-

"""
@author: xuhe
@date:
@version:
@description:
"""

from morph.config import settings
from ebaysdk.trading import Connection as Trading


class EbayMessage(Trading):

    """
    eBay消息系统SDK，是对ebaysdk.trading.Connection的继承，用于实现相应的Message业务逻辑
    eBay消息系统调用简介：http://developer.ebay.com/Devzone/guides/ebayfeatures/Development/CRM-Communications.html
    注意1：Message本身与发送者、接收者本身无关，通过API获取发送者发出的消息与接收者接收的消息「内容、时间」是完全一样的。
    接收的消息中ReceiveDate就是接收的时间，发出的消息中ReceiveDate就是对方接收的时间，对于消息本身而言就是消息被投递到对方InBox的时间。
    注意2：GetMyMessages可以获取到全部类型的消息，所有的消息都有MessageID，而GetMemberMessages只获取来自买家的消息，称作Question，
    GetMemberMessages返回的Question中的MessageID对应的是GetMyMessages中返回的ExternalMessageID，可以视为QuestionID。
    """

    def __init__(self, site_id, token, production=True):
        self.token = token
        self.site_id = site_id
        self.domain = "api.ebay.com" if production else "api.sandbox.ebay.com"
        Trading.__init__(
            self,
            domain=self.domain,
            config_file=settings.ebay_yaml,
            siteid=self.site_id,
            token=self.token
        )

    def get_my_messages(self, detail_level, folder_id=None, current_page=None, page_size=None,
                        start_time=None, end_time=None, message_ids=None):
        """
        获取消息列表，如果不指定时间，则获取到的是60天内获取到的消息，比GetMemberMessages获取到更多类型的消息，
        包括来自eBay的消息，来自买家的消息，High priority消息等，GetMemberMessages只获取来自买家的消息，
        消息可以转移到文件夹中，被删除，被归档。也可以区分是否被read，是否被flagged，flagged只有True和False。
        1.GetSummary应在同步最开始时执行，获取FolderID还有消息数量，用于计算分页
        2.GetHeaders在第二步执行，获取MessageID, Sender, Receiver的信息
        3.GetMessages根据MessageID获取消息详情
        :param detail_level:  有三个可选值
               ReturnHeaders:     返回消息头，即简要信息
               ReturnMessages:    返回消息详情，必须提供MessageIDs
               ReturnSummary:     返回消息总结数据，包括有哪些Folder，有多少未读消息，有多少被flagged的消息
        :param current_page:  当前页
        :param page_size:     每页消息数
        :param start_time:    筛选消息的起始时间
        :param end_time:      筛选消息的结束时间
        :param message_ids:   消息ID列表，最多10个
        :param folder_id:     文件夹ID，通过ReturnSummary可以查看有多少Folder，以及每个Folder中包含的消息数，
                              ID为0代表Inbox，ID为1代表Sent，ID为6代表Archive，Trash的没有ID。
        :return:
        """
        req = {
            "DetailLevel": detail_level,
            "WarningLevel": "High",
        }
        if page_size and current_page:
            req["Pagination"] = {"EntriesPerPage": page_size, "PageNumber": current_page}
        if start_time and end_time:
            req["StartTime"] = start_time
            req["EndTime"] = end_time
        if folder_id:
            req["FolderID"] = folder_id
        if message_ids:
            req["MessageIDs"] = {"MessageID": message_ids}
        response = self.execute("GetMyMessages", req)
        print response.dict()
        return response.dict()

    def get_member_messages(self, mail_message_type, sender_id=None, item_id=None,
                            member_message_id=None, message_status=None, current_page=None,
                            page_size=None, start_create_time=None, end_create_time=None):
        """
        获取来自买家的消息，买家对卖家提出的问题即为ASQ[Ask Seller A Question]，这些消息可以是买前询问，
        也可以是询问订单中的某件商品，反正都与在线产品有关，因而通过该请求获取到的消息必然包含一个ItemID，
        比GetMyMessages获取到更多节点的消息，GetMyMessages中返回的ExternalMessageID即为QuestionID，
        也是当前返回的Question.MessageID。
        :param mail_message_type:
        :param sender_id:
        :param item_id:
        :param member_message_id:
        :param message_status:
        :param current_page:
        :param page_size:
        :param start_create_time:
        :param end_create_time:
        :return:
        """
        req = {
            "MailMessageType": mail_message_type,
            "WarningLevel": "High",
        }
        if page_size and current_page:
            req["Pagination"] = {"EntriesPerPage": page_size, "PageNumber": current_page}
        if start_create_time and end_create_time:
            req["StartCreateTime"] = start_create_time
            req["EndCreateTime"] = end_create_time
        if item_id:
            req["ItemID"] = item_id
        if sender_id:
            req["SenderID"] = sender_id
        if member_message_id:
            req["MemberMessageID"] = member_message_id
        if message_status:
            req["MessageStatus"] = message_status
        response = self.execute("GetMemberMessages", req)
        print response.dict()
        return response.dict()

    def reverse_my_message(self, message_ids, flagged=None, read=None, folder_id=None):
        """
        将指定的Messages更改为已读，或者更改为被标记flagged
        :param message_ids: 被指定的MessageIDs
        :param flagged:     标记状态，True/False
        :param read:        已读状态，True/False
        :param folder_id:   文件夹ID
        :return:
        """
        req = {
            "MessageIDs": message_ids,
            "WarningLevel": "High",
        }
        if folder_id:
            req["FolderID"] = folder_id
        if flagged is not None:
            req["Flagged"] = flagged
        if read is not None:
            req["Read"] = read
        response = self.execute("ReviseMyMessages", req)
        print response.dict()
        return response.dict()

    def add_message_rtq(self, parent_message_id, item_id, recipient_id, body,
                        display_to_public=False, email_copy_to_sender=False, media_list=None):
        """
        回复用户的提问，ParentMessageID必须，代表被回复的MessageID，当RecipientID被填写后，ItemID可以为空
        :param parent_message_id:     使用的是QuestionID，也是GetMyMessages中返回的ExternalMessageID
        :param item_id:               Listing ID
        :param recipient_id:          收件人ID
        :param body:                  回复内容，2000字符内
        :param display_to_public:     是否向公众展示
        :param email_copy_to_sender:  是否将邮件拷贝到发送者邮箱
        :param media_list:
        :return:
        """
        req = {
            "ItemID": item_id,
            "MemberMessage": {
                "Body": body,
                "DisplayToPublic": display_to_public,
                "EmailCopyToSender": email_copy_to_sender,
                "RecipientID": recipient_id,
                "ParentMessageID": parent_message_id,
            }
        }
        if media_list:
            req["MemberMessage"]["MessageMedia"] = [{
                "MediaName": media["name"],
                "MediaURL": media["url"]
            } for media in media_list]
        response = self.execute("AddMemberMessageRTQ", req)
        print response.dict()
        return response.dict()

    def add_message_aqq_to_bidder(self):
        pass

    def add_message_aqq_to_partner(self):
        pass


my = "AgAAAA**AQAAAA**aAAAAA**MJHQWA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AGmICmDpCAoQ+dj6x9nY+seQ**94UCAA**AAMAAA**o+iZNTyOWGAyS8INiizhLa3SUxczTZAzZLrtD3fC0gYdQsNx202XzduoMKYXpMSfOKU3xmBQ+jJLd4yTTKLjkqTmLXHXskAup900s3CdxWfsb016BvDafG3sSO8/XV10eZcyudah6I+uCn2cLGLLlydwwJfpmjBWrlhup6WYfONnGwLwvnyvH2fDvQ9JYbjwbn3MxMuOUrGW+pjQiJ1F4LIV8os+H3EzCdof5x7qK/ID6IEzS0BulgB1SV2PVBnLQLejtY3gH5CiTP2JWZWM4JWJW9Eh5DEnjCiTSElmEEC1xc+v949AedcD/lXdml3dgBGIQHvhXo4sozO8vA+Ifp34PznxIURHv6Wu/SJUS+PqerwfwA5Vh2Cpm/lHILpOoyKQHPKvRdl7Z58pCftt9pv1sJvPq11HK3C20AbNO2oG7ANlT33z8iOlONrfC+HPED0hBheVOO25NGGz+834tIGws+WPRL6tqL41jD293/M4G+IfCsKBxE6U8ZNuoNKroBNn+vD9gMKsbCh/0xDw4f407kSMATrvRihZ24+hs6S7djfaopLjIC8w8bYDoE93u7xinsVeVcVe80D9tzHc9qtq1qzFTCQyMwe1MPXMkazlYjYwCl0fJHOSWHgzTSe3tISnmmT/MKCakXQuKr4q4uFYhh28/SX1j2aNUeoNT4krAQZ2BZOllnN/ItYNv9/LBTpzuFRgEZee6Z7E6CHV4r3Mgw0XdkanRhmZBcxHr93Kwbv/GAKsO4ubQWjQbn7D"
nm = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
si = "0"
print EbayMessage(si, nm).get_my_messages(
    detail_level="ReturnHeaders",
    message_ids=["87006649816"]
)