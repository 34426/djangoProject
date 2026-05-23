# coding=gbk
# -*- coding:uft-8 -*-
# 京东批量评论

import csv

import requests


def collect(skuid):
    # global i
    page = 1

    url = f'https://club.jd.com/comment/productPageComments.action?productId={skuid}&score=0&sortType=5&page={page}&pageSize=10&isShadowSku=0&rid=0&fold=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 SLBrowser/9.0.6.8151 SLBChan/109 SLBVPV/64-bit',
        'Referer': url
    }
    print(skuid, page)
    while True:
        try:
            dic = requests.get(url=url, headers=headers).json()
            break
        except:
            input('error json: ')
    if not dic['comments']:
        return
    for li in dic['comments']:
        name = li['nickname']
        comment = li['content']
        time = li['creationTime']
        score = li['score']
        image = len(li.get('images', []))
        video = len(li.get('videos', []))
        after = li.get('afterUserComment', {}).get('content', '')
        reply = ([i for i in li.get('replies', []) if 'venderShopInfo' in i.keys()] + [{}])[0].get('content', '')
        like = li['usefulVoteCount']
        row = [skuid, name, time, comment, score, image, video, after, reply, like]
        print(row)
        csv.writer(open('comments.csv', 'a', encoding='utf-8-sig', newline='')).writerow(row)
        # i += 1
        # page += 1


if __name__ == '__main__':
    i = 0
    csv.writer(open('京东评论1.csv', 'w', encoding='utf-8-sig', newline='')).writerow(
        ['商品ID', '昵称', '时间', '评论', '评分', '图片', '视频', '追评', '回复', '点赞'])
    collect('100028865338')
    #collect('100001150266')
    #collect('10051470278376')
    # collect('49010631197')
    #collect('100034660869')
    #collect('100036702080')
    #collect('616172')
    #collect('100005845997')
    # collect('100029503766')
    # collect('4564414')
    # collect('100045011817')
    # collect('234431')
    # collect('4564434')
    # collect('323578')
    # collect('4648550')
    # collect('100028254145')
    # collect('10040736822540')
    # collect('100034825145')
    # collect('10050498319813')
    # collect('3934183')
    # collect('10023360392147')
    # collect('100010070065')
    # collect('10040392599998')
    # collect('100001150284')
    # collect('10047240925359')
    # collect('3956533')
    # collect('100036702118')
    # collect('100037123560')
