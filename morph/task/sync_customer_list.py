# -*- coding: utf-8 -*-

"""
@author: xuhe
@date: 17/3/31
@description: 
"""

import traceback
from morph.controls.ebay.sync import SyncEbayCustomer
from morph.controls.ebay.sync import SyncEbayEvaluation
from morph.controls.smt.sync import SyncSmtCustomer
from morph.controls.smt.sync import SyncSmtEvaluation
from morph.controls.wish.sync import SyncWishCustomer
from morph.lib.model.session import sessionCM
from morph.lib.model.shop import Shop
from morph.lib.model.task import Task
from morph.lib.utils.logger_util import logger
from morph.task import morph_celery
from morph.task.sync_customer_detail import sync_customer_detail


@morph_celery.task(ignore_result=True)
def sync_customer_list(task_id, shop_id, timestamp):
    method_route = {
        "eBay": SyncEbayCustomer,
        "Wish": SyncWishCustomer,
    }
    with sessionCM() as session:
        task = Task.find_by_id(session, task_id)
        shop = Shop.find_by_id(session, shop_id)

        handler = method_route[shop.platform](shop, timestamp)
        try:
            logger.info(timestamp)
            handler.execute()
            task.status = 1
            task.remark = timestamp
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            task.status = -1
        finally:
            Task.update(session, task)
            pass


@morph_celery.task(ignore_result=True)
def sync_smt_customer_list(task_id, shop_id, timestamp):
    with sessionCM() as session:
        task = Task.find_by_id(session, task_id)
        shop = Shop.find_by_id(session, shop_id)
        handler = SyncSmtCustomer(shop, timestamp)
        try:
            handler.execute()
            task.status = 1
            task.remark = timestamp
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            task.status = -1
        finally:
            Task.update(session, task)
            pass


@morph_celery.task(ignore_result=True)
def sync_ebay_msg_list(task_id, shop_id, timestamp):
    sync_smt_customer_list(task_id, shop_id, timestamp)


def sync_evaluation_list(task_id, shop_id, timestamp):
    method_route = {
        "eBay": SyncEbayEvaluation,
        "AliExpress": SyncSmtEvaluation
    }
    with sessionCM() as session:
        task = Task.find_by_id(session, task_id)
        shop = Shop.find_by_id(session, shop_id)
        handler = method_route[shop.platform](shop)
        try:
            logger.info(timestamp)
            handler.execute()
            task.status = 1
            task.remark = timestamp
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            task.status = -1
        finally:
            Task.update(session, task)
            pass

if __name__ == "__main__":

    # shop.token = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
    # shop.site_id = "0"
    # smt
    # shop.platform = 'AliExpress'
    # shop.account = '1be0afca-412a-42a1-b1f3-bc4b34e9bf0b'
    # shop.site_id = 2
    # shop.session = '0bdf6f64-372d-4b6a-b68b-5efe64bc18bd'
    # shop.owner = 'cn1518284505qzvx'

    # evaluation
    # shop.token = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
    # shop.account = "AgAAAA**AQAAAA**aAAAAA**C6d8Vw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6AAkIGgC5GKqAudj6x9nY+seQ**94UCAA**AAMAAA**eCsndGWz9QGRmaERU4mzDBDmCBIgLA2Yk1PaZLnrOjPvIMXNITpIeH9PRAqAPdykJ9AihKAFLRKl4AfIS6c2sNf9AomUiUXlmm5j+OpTS+/C9c/gIpAQrBY2AELmkq8QIpWQ5bmgvFDr7jn3BxpwwcUDCeAv/pUcvQYpXnyDxI8H0bIsKQudUKaL7sS/5gVqgtzN561rt3s5lBSpfoP4qzdQ9iSfaIWIX7z40XE18BRLDsY/3rrsGlASwaShSul7StJWkjd0NL3AiYPiPuJtRzahUTtPRLP5NxxKJNJZhEHXRqXNcFVN3FYEAuiKDb0hE2Jr9KXL3A4lJNjaNhNquGkqTyA9NB3Vei2zCZgVWvlaQAavJhn+ZFBdQBFjNBdahK78s+Ve+Ym7bbEXKlhQYUFmBcXIUgOTr3MR2ghe3peHlRSSbKeaPDTIKcJ5f6PNKqGjHaQYOnu8igGluHVxb2gKiXkT/UXH08lFzOcC3bP7WkEoo/DLPBbxFsguCbuY0gtjyeVUcDU3idpFbjrCpy2bBlPBp9Qts3Fdw87O1guOk+B6UU/LEuGYbcRRyzWQie1QWbgiFSPbA4rLYemIrsh6iIRgKxASFI+ZIeqVdYsALy8PHsEE6jNzQMcf5R2e/DBhW7Rf/20by6yZ3eb6ONBlm9UWVqsxMRL0aYfKi1PIG1V1RKaq+ul5ypiTDPK6lLadihibYn2I8BvD4n+VdRVNcDCYpBppjKrNtR+UgI+1Jr+n2tAc5B9xOq/0NCnr"
    # shop.account = "AgAAAA**AQAAAA**aAAAAA**7HTjVw**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6ABkoGoD5aHpAqdj6x9nY+seQ**94UCAA**AAMAAA**UGJaMLGzkw/V30Q7yrFVpkDxh9+F1v7X7taOlLW6WeEQCY/F6PhqPrjJfFLfw5rg93LNBvSQV4hO/cLtHS1K059mXzg61q4xHToNFk2uK+DdoFlCGbc1BD0TRyZ9zOSw4peeHJy/XUG2GwzkyPSrkBlU8X8e2IcZiyqCEILF0yl0ffDJy4Yz62JZVYCCX7HzvI/39N3ROGcUpCVbmxPE+QJI4a2Xst9ApBikHreVDntERITCRj8FhnnmAoDHGWziGN5GlNOQ40ETGX9GUX9yjK31haSpTpIsJRQBYhYeOYwo+F+LV5mFR55XDtuKD837jmKGZvpwll2pN4XhJfVbU7VFWbqyi2p4ccjxNEKXqmbJSSESvXmhiNK5J5EmAZVxh0BmXnNAHYCMJ1gZ7+sa4shnnzH12wcjMjK679iwXyYiK1YTrNmLNei4UeDFBfb2fzqm+eSDQIBK9g+HX/fZkTssU0O1m59wTeS+9GG6Bu7wTZyjU5cbCbjlQl6J4xhy4rs+efJLLAx/PfXmAODHgPF1Ai4rF/YYogFy+V9G0SiQJLQz31yxD3uJuDNyVoEB7/voPAvVutUvZcJzw2LAHIETfHG7GNMoHFA1fyLOF76YIZzsxBylxRY/x12gLlHFaKrtNAJRWpbKHO6usD0GMehDd9a/ALlSqHMPolKyaN6RMWEdov/Drq5PYTW+2OmO8GYyzrmCSk8s+OEv4LhLwkL4YBdYZyKoGo7Qf2FTqbfuYOKMblMi2MDACFSYKuvZ"
    # shop.account = "a36c6039-cca4-4638-a84a-dc1ec9c4200f"
    # shop.site_id = "2"

    print("begin ... ")
    # sync_customer_list("1", "7612", "2017-05-27T16:57:52;2017-08-31T17:28:07")
    # sync_smt_customer_list("1", "", "2017-07-29T16:57:52;2017-08-31T17:28:07")
    # sync_evaluation_list('1', '6638', "2017-07-29T16:57:52;2017-08-31T17:28:07")
    sync_evaluation_list('1', '710', "2017-07-29T16:57:52;2017-08-31T17:28:07")
    print("end ... ")
