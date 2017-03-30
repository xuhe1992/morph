# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/1/23
# @description: some utils method such as signature computing and so on


import hmac
import hashlib


def api_signature_rule(secret_key, path, params):
    """
    该方法用于生成所有api请求的签名
    :param path: 完整url请求中path,从host后面开始，到?符号之间的字符串
    :param params: 所有参数key-value组成的字典
    :return: 返回经过hamc_sha1加密过的字符串
    """
    sign_factor = list()
    sign_factor.append(path)

    sorted_params = sorted(params.iteritems(), key=lambda d: d[0])
    for sorted_param in sorted_params:
        sign_factor.append(str(sorted_param[0]))
        sign_factor.append(str(sorted_param[1]))

    data = "".join(sign_factor)
    return str2sha1(secret_key, data)


def param_signature_rule(secret_key, params):
    """
    该方法用于生成授权请求时需要的签名
    :param params: 所有参数key-value组成的字典
    :return: 返回经过hamc_sha1加密过的字符串
    """
    sign_factor = list()

    sorted_params = sorted(params.iteritems(), key=lambda d: d[0])
    for key, value in sorted_params:
        sign_factor.append(str(key))
        sign_factor.append(str(value))

    data = "".join(sign_factor)
    return str2sha1(secret_key, data)


def str2sha1(secret_key, source_str):
    """
    该方法用于计算hamc_sha1加密
    :param secret_key: 用户的密钥
    :param source_str: 要加密的字符串
    :return:
    """
    digest_maker = hmac.new(secret_key, source_str, hashlib.sha1)
    return digest_maker.hexdigest().upper()


