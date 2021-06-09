import requests
import re
import urllib.request
import wechatsogou
import pandas as pd
import time
import random

from pprint import pprint
from wechatarticles import ArticlesInfo
from wechatarticles.utils import get_history_urls, verify_url


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        print("Can't get html text.")
        return ""


def articleTitle(html):
    pattern1 = re.compile('var msg_title = ".*"')
    result1 = pattern1.findall(html)[0]
    return result1.lstrip('var msg_title = "').rstrip('"')


def imgURL(html):
    pattern1 = re.compile('var msg_cdn_url = ".*=jpeg"')
    result1 = pattern1.findall(html)[0]
    pattern2 = re.compile('http.*jpeg')
    result2 = pattern2.findall(result1)[0]
    return result2


def getAllURl(gzh_iname):
    # captcha_break_time为验证码输入错误的重试次数，默认为1
    ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
    # 将该公众号最近10篇文章信息以字典形式返回
    data = ws_api.get_gzh_article_by_history(gzh_iname)
    article_list = data['article']
    url_list = []
    for article in article_list:
        url = article['content_url']
        url_list.append(url)
    return url_list


def save_xlsx(fj, lst):
    df = pd.DataFrame(lst, columns=["url", "title", "date", "read_num", "like_num"])
    df.to_excel(fj + ".xlsx", encoding="utf-8")


# 获取大量文章url（利用历史文章获取链接）
def demo(ai, lst):
    # 抓取示例
    fj = "公众号名称"
    item_lst = []
    for i, line in enumerate(lst, 0):
        print("index: ", i)
        # item = json.loads('{' + line + '}', strict=Fasle)
        item = line
        timestamp = item['comm_msg_info']['datetime']
        ymd =time.localtime(timestamp)
        date = "{}-{}-{}".format(ymd.tm_year, ymd.tm_mon, ymd.tm_mday)

        infos = item["app_msg_ext_info"]
        url_title_lst = [[infos["content_url"], infos["title"]]]
        if "multi_app_msg_item_list" in infos.keys():
            url_title_lst += [
                [info["content_url"], info["title"]]
                for info in infos["multi_app_msg_item_list"]
            ]

        for url, title in url_title_lst:
            try:
                if not verify_url(url):
                    continue
                # 获取文章阅读数在看点赞数
                read_num, like_num, old_like_num = ai.read_like_nums(url)
                print(read_num, like_num)
                item_lst.append([url, title, date, read_num, like_num])
                time.sleep(random.randint(5, 10))
            except Exception as e:
                print(e)
                flag = 1
                break
            finally:
                save_xlsx(fj, item_lst)

        if flag == 1:
            break

    save_xlsx(fj, item_lst)


def test_geturl():
    # 需要抓取公众号的__biz参数
    biz = ""
    # 个人微信号登陆后获取的uin
    uin = ""
    # 个人微信号登陆后获取的key，隔段时间更新
    key = ""

    lst = get_history_urls(
        biz, uin, key, lst=[], start_timestamp=0, start_count=0, end_count=10
    )
    print("抓取到的文章链接")
    print(lst)

    # 个人微信号登陆后获取的token
    appmsg_token = "826708820"
    # 个人微信号登陆后获取的cookie
    cookie = "appmsglist_action_3885637666=card; RK=dY7tqZneWT; " \
             "ptcz=027e8714e4f60754f35b0b44b126ffda319be4aeb5864175f8972727e6c7c6bb; pac_uid=0_a871cae4283a4; iip=0; " \
             "pgv_pvid=1497060874; rewardsn=; wxtokenkey=777; ua_id=6asOBIr6Ny3UAAdpAAAAAPKE-N8DmNMgs4PKHolOVAU=; " \
             "wxuin=23142494464717; pgv_info=ssid=s6393486924; cert=rwh2pl6zzXYxKvQIFiDa5ghB6_RGMfyZ; mm_lang=zh_CN; " \
             "noticeLoginFlag=1; master_key=FkAxNNDAJE4MzGC/DRCSD3DqJgnKSysE4Vw/DQz77Lo=; " \
             "sig=h01a5403e54e263823e398fb921ccc230fa034d03663951e73e1f8028057691a898416b4169ba4a2099; " \
             "uuid=1e0dc6b8e62d1053bc9beaf43618b406; rand_info=CAESINqZWWJU/UhXQ4suzS6T0QbUYTxdbR5mG26ePQHPAWYo; " \
             "slave_bizuin=3885637666; data_bizuin=3885637666; bizuin=3885637666; " \
             "data_ticket=uPc/toUinwIEeEmMS6dLCLTxc9PLjYLm0n4Ft/Wun+21OH3qyt9onSbvZJHeNdGi; " \
             "slave_sid" \
             "=bE5nbGNGel9lOHRLMld4a3dRR3ZCdUo3cmcyV2k1bnhlQzhxNFJQSWt2bzRBQ3JFMldpUWJ0bHhYclJUV3Q3M0xBYUNVMlBmamp" \
             "NMXdnc1N5Y1htYVdESWVXeHBxa1BRa2ZlR3pEcnk3a2h0RlZUNGF6WWZzbGJpY2llcEdwVGt0OExSWm11V3FZNEZXb1l0;" \
             "slave_user=gh_460dad26e5c9; xid=551734947a3dda9a817379481c887b26 "
    # 获取点赞数、阅读数、评论信息
    ai = ArticlesInfo(appmsg_token, cookie)

    # url：微信文章链接. lst[0]["app_msg_ext_info"]["content_url"]
    url = lst[0]["app_msg_ext_info"]["content_url"]
    read_num, like_num, old_like_num = ai.read_like_nums(url)
    item = ai.comments(url)
    print("阅读：{}; 在看: {}; 点赞: {}".format(read_num, like_num, old_like_num))
    print("评论信息")
    pprint(item)


def main():
    # gzh_name = input("请粘贴要下载封面的公众号名称：\n")
    # print(gzh_name)
    gzh_name = '盾山实验室'
    url_list = getAllURl(gzh_name)
    i = 0
    for url in url_list:
        html = getHTMLText(url)
        img = urllib.request.urlopen(imgURL(html)).read()
        with open('./wechat_img/'+i+'.jpg', 'wb') as f:
            f.write(img)
        i = i+1


if __name__ == '__main__':
    main()
