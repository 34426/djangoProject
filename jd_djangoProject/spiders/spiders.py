import csv
import os
import random
import time

import pandas as pd
from lxml import etree

import requests

cookie = '__jdv=76161171|cn.bing.com|-|referral|-|1730375872742; o2State={%22webp%22:true%2C%22avif%22:true}; 3AB9D23F7A4B3CSS=jdd037M7DEKUXWON3LWHQFUNLD77XWJIZL5XSOECH72SEVUW6FFZXBCD4SVEGGTO3R4YO6RRRBHISXLGOO3YGXI6G4IFM6IAAAAMS4JYHJCQAAAAADUBCYQGV7SMXLUX; _gia_d=1; __jdu=17303758727421276310181; areaId=12; ipLoc-djd=12-988-0-0; PCSYCityID=CN_320000_320500_0; 3AB9D23F7A4B3C9B=7M7DEKUXWON3LWHQFUNLD77XWJIZL5XSOECH72SEVUW6FFZXBCD4SVEGGTO3R4YO6RRRBHISXLGOO3YGXI6G4IFM6I; _pst=jd_54a25ab4deacb; unick=_Funnel_N; pin=jd_54a25ab4deacb; thor=B981A182396C96964470EA9732F40844017D6BE8CBFC4F65965C60482ADCFB629C067113B05BD93DE4C029BECF9418E54A6F6F9A73FFF13946CFE197839EED7FFF820EE2597CAD00CF7E7AD103A33AEEBE7821EA5B116FC9FB573289210DF3B835CBACCEC097CEEDB37541189F3183B0A38972A5E44994128C89C2E8361CF3AB16B9E3AF7D9FB378FDF969E5830DCD7A160CC13D9666838C8553CCF953D20EE5; flash=3_47HUUVF8dpHM9GvBQDYWQG2xbwe5jd85ZERyt7cHjPAMWzN0gpQfWTjNzH2QAt9-WQQIKeCaIyCLjblF21QYQ5oZdz9tggvG5JwBLk2aGKvlD--kYmGyMarciA50TpNpOYUlUzyvj7SQO6qt5mVmkXEbUWmWh7Yjz-iP619ZWMq*; _tp=9KR20TlCraBjINyZW70CJG2azjXXO%2Fv4OU1ArneVd3E%3D; pinId=1KLQNdU-zDHx2qchjX03FbV9-x-f3wj7; __jda=76161171.17303758727421276310181.1730375873.1730375873.1730375873.1; __jdb=76161171.4.17303758727421276310181|1.1730375873; __jdc=76161171; shshshfpa=feca7853-e765-3634-74e8-cd2c5c6511ea-1730375921; shshshfpx=feca7853-e765-3634-74e8-cd2c5c6511ea-1730375921; UseCorpPin=jd_54a25ab4deacb; shshshfpb=BApXS9d154fdAPNZDFSLYgMYhpFvno6AwBnJ2Xg5o9xJ1MkRLPoG2'
# cookie信息每个人都不同，需登录到京东网站，通过浏览器查看cookie信息
headers = [
    {
    'User-Agent': "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "cookie": cookie
    },

]


def getip():  # 随机ip
    with open("spiders/ipdaili.txt") as f:
        iplist = f.readlines()
    proxy = iplist[random.randint(0, len(iplist) - 1)]
    proxy = proxy.replace("\n", "")
    proxies = {
        'http': 'http://' + str(proxy)
    }
    return proxies


def data_processing(inputpath, outputpath):
    def if_wan(x):
        if '万' in str(x):
            x = float(x[:-1]) * 10000
        return x

    df = pd.read_csv(inputpath)
    df = df.dropna(subset=['总评数'])
    df = df.drop_duplicates(subset=['商品id'])
    df['总评数'] = df['总评数'].str.replace('+', '')
    df['总评数'] = df['总评数'].str.replace('万', '0000')
    df['总评数'] = df['总评数'].astype(int)

    df['好评数'] = df['好评数'].str.replace('+', '')
    df['好评数'] = df['好评数'].map(if_wan)
    df['好评数'] = df['好评数'].astype(int)

    df['默认好评'] = df['默认好评'].str.replace('+', '')
    df['默认好评'] = df['默认好评'].map(if_wan)
    df['默认好评'] = df['默认好评'].astype(int)

    df['追评数'] = df['追评数'].str.replace('+', '')
    df['追评数'] = df['追评数'].map(if_wan)
    df['追评数'] = df['追评数'].astype(int)

    df['视频晒单数'] = df['视频晒单数'].str.replace('+', '')
    df['视频晒单数'] = df['视频晒单数'].map(if_wan)
    df['视频晒单数'] = df['视频晒单数'].astype(int)
    df['差评数'] = df['差评数'].str.replace('+', '')
    df['差评数'] = df['差评数'].map(if_wan)
    df['差评数'] = df['差评数'].astype(int)

    df['中评数'] = df['中评数'].str.replace('+', '')
    df['中评数'] = df['中评数'].map(if_wan)
    df['中评数'] = df['中评数'].astype(int)

    df.to_csv(outputpath)

def getdata(url, pinpai):
    res = requests.get(url, headers=random.choice(headers), proxies=getip())
    res.encoding = 'utf-8'
    text = res.text

    selector = etree.HTML(text)
    list = selector.xpath('//*[@id="J_goodsList"]/ul/li')

    rows = []
    for i in list:
        title = i.xpath('.//div[@class="p-name p-name-type-2"]/a/em/text()')
        price = i.xpath('.//div[@class="p-price"]/strong/i/text()')[0]
        img = i.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img')[0]
        product_id = i.xpath('.//div[@class="p-commit"]/strong/a/@id')[0].replace("J_comment_", "")
        try:
            shop = i.xpath('.//div[@class="p-shop"]/span/a/text()')[0]
        except IndexError:
            shop = ''
        title = ' '.join(title)
        rows.append([product_id, title.replace('\n', ''), price, shop, pinpai,img])
    return rows


def getcommit(data):
    kv = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "cookie": cookie
    }
    '''抓评论'''
    pids = data[0]
    endnum = int(len(data)/100)
    for i in range(1, endnum):
        # print(pids[100*(i-1):100*i],type(pids))
        newpids = pids[100 * (i - 1):100 * i]
        comment_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds="
        for pid in newpids:
            if pid == '商品id':
                continue
            else:
                comment_url += pid + ","
        comment_r = requests.get(comment_url, headers=headers[0], proxies=getip())
        p_comment = []
        for comment in comment_r.json()["CommentsCount"]:
            p_comment.append([comment['ProductId'], comment["CommentCountStr"], comment["AverageScore"],
                              comment["GoodCountStr"], comment["DefaultGoodCountStr"],
                              comment["GoodRate"], comment["AfterCountStr"], comment["VideoCountStr"],
                              comment["PoorCountStr"], comment["GeneralCountStr"]])
            # 总评数，平均得分，好评数，默认好评，好评率，追评数，视频晒单数，差评数，中评数
        # 将抓取的结果保存到本地CSV文件中
        with open('result1.csv', mode='a', encoding='utf-8', newline='') as f1:

            writer = csv.writer(f1)
            writer.writerow(['商品id', '总评数', '平均得分', '好评数', '默认好评', '好评率', '追评数', '视频晒单数', '差评数', '中评数'])
            for item in p_comment:
                writer.writerow(item)


def getpinpai(url):
    res = requests.get(url, headers=headers[0], proxies=getip())
    res.encoding = 'utf-8'
    text = res.text

    selector = etree.HTML(text)
    list = selector.xpath('.//ul[@class="J_valueList v-fixed"]/li')
    # print(list)
    rows = []
    for i in list:
        pinpai1 = i.xpath('.//a/text()')[-1].replace('\n\t\t\t\t\t\t\t\t\t\t', '').replace('\n\t\t\t\t\t\t\t\t\t', '')
        rows.append(pinpai1)
    return rows


def savedata(data):
    if os.path.exists('result.csv'):
        with open('result.csv', mode='a+', encoding='utf-8', newline='') as f:
            wirter = csv.writer(f)
            for item in data:
                wirter.writerow(item)
    else:
        with open('result.csv', mode='a+', encoding='utf-8', newline='') as f:
            wirter = csv.writer(f)
            wirter.writerow(['商品id', '标题', '价格', '店铺', '品牌', '图片'])
            for item in data:
                wirter.writerow(item)


pinpai =getpinpai('https://search.jd.com/Search?keyword=手机&enc=utf-8&wq=手机&pvid=519c67582fd9416cb4d94075fe428969')
print(pinpai)
for item in pinpai:
    for i in range(1,20):
        time.sleep(random.random()*10)
        url = 'https://search.jd.com/search?keyword=手机&wq=手机&ev=exbrand_{}%5E'.format(
            item)
        n = i*2-1
        url = url+"&pvid=519c67582fd9416cb4d94075fe428969&page={}".format(n)
        savedata(getdata(url,item))
        print(url)

data = pd.read_csv('spiders/result.csv', header=None)
getcommit(data)

df1 = pd.read_csv('spiders/result.csv', encoding='utf-8')#读取第一个文件
df2 = pd.read_csv('spiders/result1.csv', encoding='utf-8')#读取第二个文件
df1['商品id'] = df1['商品id'].astype(str)
df2['商品id'] = df2['商品id'].astype(str)
outfile = pd.merge(df1, df2,  left_on='商品id', right_on='商品id')#
outfile.to_csv('spiders/result2.csv', index=False,encoding='utf-8')#输出文件

data_processing('spiders/result2.csv', 'spiders/result3.csv')


