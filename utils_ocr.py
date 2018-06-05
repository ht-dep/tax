import os
import random
import requests
import pytesseract
import pyexcel as p
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

url_img_fj = "http://wssw.fj-n-tax.gov.cn/etax/captcha.jpg?n={}".format(str(random.random()))
url_action_fj = "http://wssw.fj-n-tax.gov.cn/etax/fpcy/action.do"
url_action_zj = "http://www.zjtax.gov.cn/fpcx/include2/fpcy_jg_lscx.jsp"
url_index_zj = "http://www.zjtax.gov.cn/fpcx/include2/wlfpcybd_lscx.jsp"
client = requests.session()

headers = {
    "Accept": "text/plain;charset=utf-8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Content-Length": "64",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "wssw.fj-n-tax.gov.cn",
    "Origin": "http://wssw.fj-n-tax.gov.cn",
    "Referer": "http://wssw.fj-n-tax.gov.cn/etax/135/sscx/fpcy.jsp",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}


def get_current_dir():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    # logging.info("当前目录：",file_dir)
    return file_dir


# def exec_excel(name="demo_fq.xlsx"):
#     '''
#     批量读取excel
#     :return:[{}]
#     '''
#     result = []
#     # clumn = ["fpdm", "fphm", "xhfswdjh", "kpje", "kprq", "fpyzm", "result"]
#     # clumn_excel = ["code", "number", "taxcode", "date", "img", "result"]
#     path_xml = os.path.join(get_current_dir(), name)
#     logging.info(path_xml)
#     data_xml = p.get_records(file_name=path_xml)
#     logging.info("读取xml文件的数据，计 {} 行".format(len(data_xml)))
#     for i in data_xml:
#         res = exec_cal(i)
#         if res["result"] == "验证码不正确":
#             res = exec_cal(i)
#         result.append(res)
#     return result


def exec_stream_fj(data_xml):
    '''
    批量读取excel
    :return:[{}]
    '''
    result = []
    # clumn = ["fpdm", "fphm", "xhfswdjh", "kpje", "kprq", "fpyzm", "result"]
    # clumn_excel = ["code", "number", "taxcode", "date", "img", "result"]
    # path_xml = os.path.join(get_current_dir(), name)
    # logging.info(path_xml)
    # data_xml = p.get_records(file_name=path_xml)
    logging.info("读取xml文件的数据，计 {} 行".format(len(data_xml)))
    for i in data_xml:
        res = exec_cal_fj(i)
        if res["result"] == "验证码不正确":
            res = exec_cal_fj(i)
        result.append(res)
    return result


def exec_cal_fj(x):
    '''
    获取验证码---解析验证码
    提交请求---得到结果
    :return:
    {
        "code":"",
        "number":"",
        "taxcode":"",
        "money":"",
        "date":"",
        "img":"",
        "result":""
    }
    '''
    Param = {
        "fpdm": x["code"],
        "fphm": x["number"],
        "xhfswdjh": x["taxcode"],
        "xhfmc": "",
        "kpje": x["money"],
        "kprq": x["date"],
        "fpyzm": ""
    }

    r = client.get(url_img_fj, stream=True)
    img = Image.open(BytesIO(r.content))
    valid_code = pytesseract.image_to_string(img)
    # logging.info("验证码：{}".format(valid_code))
    Param["fpyzm"] = valid_code
    res = client.post(url_action_fj, Param, headers=headers)
    result = res.text
    logging.info("调用结果：{}".format(result))
    Param["result"] = result
    return Param


def exec_stream_zj(data_xml):
    '''
    批量读取excel
    :return:[{}]
    '''
    result = []
    # clumn = ["fpdm", "fphm", "xhfswdjh", "kpje", "kprq", "fpyzm", "result"]
    # clumn_excel = ["code", "number", "taxcode", "date", "img", "result"]
    # path_xml = os.path.join(get_current_dir(), name)
    # logging.info(path_xml)
    # data_xml = p.get_records(file_name=path_xml)
    logging.info("读取xml文件的数据，计 {} 行".format(len(data_xml)))
    for i in data_xml:
        # logging.info(i)
        res = exec_cal_zj(i)
        result.append(res)
    return result


def exec_cal_zj(x):
    '''
    获取验证码---解析验证码
    提交请求---得到结果
    :return:
    {
        "code":"",
        "number":"",
        "taxcode":"",
        "money":"",
        "date":"",
        "img":"",
        "result":""
    }
    '''
    Param = {
        "fpdm": x["code"],
        "fphm": x["number"],
        "kjfsbh_qp": x["taxcode"],  # 税务登记号
        "je_qp": x["money"],
        "rq_qp": x["date"],
        "ywlx": "FPCX_LXCX",
        "ywlxbf": "FPCX_LXCX",
        "anbz": "wqr",
        "cxbz": "lscx",
    }

    client.get(url_index_zj)
    res = client.post(url_action_zj, Param)
    html = res.content.decode("GBK")
    doc = BeautifulSoup(html)
    t = doc.select("table tbody td")
    for i in t:
        re = i.string
        if re:
            if len(str(re).strip()) > 0:
                result = str(re)
                # logging.info(str(re))
                logging.info("调用结果：{}".format(result))
                Param["result"] = result
    return Param


if __name__ == "__main__":
    # exec_excel()
    pass
