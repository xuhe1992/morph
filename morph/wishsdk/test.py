# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 16/5/26
# @description: 

from furion.lib.model.shop import Shop
shop = Shop(
    account="da6ed36c890e467f983fbc40b99870e2",
    session="6a4d3537a8134ba4b433c00169ab1a22"
)

from wishsdk.product import WishProduct
from wishsdk.variant import WishVariant
wp = WishProduct(shop)

product = {
    "name": "The new black and white slim Korean men's shirts long sleeved shirt mens fashion tide French front jacket",
    "description": "Application scenarios: Daily\nApplicable object: Youth\nSubdivision style: business casual\nPattern: solid color\nClothing craft: iron processing\nListing Year season: Spring 2016\nBasic style: Fashion City\nSleeve length\nType: Slim version\nCollar type: square collar",
    "tags": "men's shirts,long sleeved shirt,men's fashion,french jacket",
    "sku": "ELY-SHIRT-1",
    "color": "Purple",
    "size": "L",
    "inventory": "1000",
    "price": "47.98",
    "shipping": "2.0",
    "msrp": "109.98",
    "shipping_time": "7-14",
    "main_image": "http://img.alicdn.com/bao/uploaded/i3/TB1O4fkJpXXXXaSXVXXXXXXXXXX_!!0-item_pic.jpg",
    "extra_images": "|".join([
        "http://img.alicdn.com/imgextra/i4/2203660064/TB2FV9sepXXXXcFXXXXXXXXXXXX_!!2203660064.jpg"
    ]),
    "parent_sku": "ELY-SHIRT"
}
variant = {
    "color": "Black",
    "size": "L",
    "parent_sku": "ELY-SHIRT",
    "sku": "ELY-SHIRT-2",
    "inventory": "1000",
    "price": "47.98",
    "shipping": "2.0",
    "msrp": "109.98",
    "shipping_time": "7-14",
    "main_image": "https://img.alicdn.com/bao/uploaded/i1/2203660064/TB2xePOaXXXXXasXXXXXXXXXXXX_!!2203660064.jpg"
}
# print WishVariant(shop).update_variant(
#     "ELY-SHIRT-1",
#     main_image="https://img.alicdn.com/bao/uploaded/i2/2203660064/TB2LxoeaFXXXXbaXpXXXXXXXXXX_!!2203660064.jpg")
print WishProduct(shop).retrieve_product_by_id("5746b057572b8161a4a61e10")
# print WishVariant(shop).create_variant(variant)