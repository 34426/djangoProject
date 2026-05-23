import csv
import os
import random
import time

import pandas as pd
from lxml import etree
import requests

# 你的Cookie已正确替换，无需修改
cookie = '__jdu=17606842203391438168300; areaId=20; shshshfpa=5fcde206-43a2-6ce9-cb0b-1585e5827f0c-1686826393; shshshfpx=5fcde206-43a2-6ce9-cb0b-1585e5827f0c-1686826393; jcap_dvzw_fp=8xqk2aTAjK9QE3J7GY3SiUayrxUDcY3tIIRGDPzFXd1lsLeIJ6_393t6tI28A_hj1ip28x3qP8b1hg1H_7CmtqWQ9to=; TrackID=1HTRqjbNaWN7l11yc3p8c43XppuLC1jKPqfK8zRf4qXdHYxdZqV6NSk1iKAPRiLC3SVj0tojZDDExBzlJhawqUcdr81oXAz3jmxJMglxJ3VnRjbodCtl_S5jv9zqkA1bS; light_key=AASBKE7rOxgWQziEhC_QY6yaAxd1LQrKVDbayyjNKkyf0p1bJcOdenujEUi0I-OHObdQHSkm; pinId=IFlG0RWg2oSIdpdxVONxlg; pin=wdFpqngVNXrpcR; unick=d3kgqhr6dkj7s5; _tp=GcUQq931qSIEqkqqL9y%2FhA%3D%3D; _pst=wdFpqngVNXrpcR; thor=45A25E07A94275BAA76E4BD48AC01FD3CCE8579EB365476D6AC6EE97BC4CD331F24EA2D8631E6AA2324399A55FDDC2BBFBCD825D4CB9B7748A18CC8A2B828933122442840FF8D1437A9EBD56614101FA343A075DAF6C8CC706289A00C578FEFE3E6499DC0C10BEA70C2438267ADA11D8CF1326D3466342D6C13F9F686C28CAED47E346EF9C69472A40DBE613928822F8; PCSYCityID=CN_450000_450300_0; umc_count=1; ipLoc-djd=20-1726-22884-60713; mail_times=4%2C2%2C1762751989411; jsavif=1; unpl=JF8EAKtnNSttWxxWBE4EE0dEHlVWW1sNTEQEamZWXF9cGVdWEwBPQkJ7XlVdWRRLFx9vZhRXX1NIXA4aBCsSEXtfVl9YCEgXC29XNVNdUQYVV1YyGBIgSm1UWFoJTB4GbGQEVl9QS1EHEgIcGxJKXGRfbQ9LHjNfVwBUXFlMVw0aAhkiEXtfVV9YCEkTBGlgNR8zWQZUAxwDHBsVSF5VXF8ASxIBZmcCXV9ZSmQEKwE; __jdv=76161171|lianmeng__10__kong|t_330412191_|tuiguang|2f30d79ded934746b640b935c2b93eac|1762788547733; 3AB9D23F7A4B3C9B=3BEAK4LDXMJRZ3DYE5TPS6APE4R6QSMXTPYIQJ4JTPK5C5QDKAIFGCWAAZQCHDOD5P3TR6JZXHTXXPWZAV6UVB2KCU; token=1757764d814a81256128ce56dc456a3f,3,979327; flash=3_kCCjb5kYvzug15Y6I8Tvr2Gr7LXK37PT39rr5GE189Og1yoVVrbe3nStPyBFT7q_iZ_VxwrvrtN1CKn-bLu30NnG9seM3kLPE9cx_3D7ihgVzfwauR1qL4NZUvsWWE2nXBw0bhB-ZpxsZlNAmvsZq9FB7fOAJkBEczT2EXeapbRA1lNgqDL*; 3AB9D23F7A4B3CSS=jdd033BEAK4LDXMJRZ3DYE5TPS6APE4R6QSMXTPYIQJ4JTPK5C5QDKAIFGCWAAZQCHDOD5P3TR6JZXHTXXPWZAV6UVB2KCUAAAAM2NZ7HC4YAAAAACZBA4X7NBVBP4MX; _gia_d=1; __jda=181111935.17606842203391438168300.1760684220.1762784700.1762788548.8; __jdc=181111935; __jdb=181111935.15.17606842203391438168300|8.1762788548; shshshfpb=BApXWVeJ2bf9AO0wWseWCXXnCfPJeRM7WB8TDZLxq9xJ1PMtfW5bHnB3dohPoI4VBCiRls8Hs3Iwn; cn=13; sdtoken=AAbEsBpEIOVjqTAKCQtvQu17G3Mtchy7Wd_U7llUtXKMnfypYoAfcEtOfC9rbY-z6eQZyaBDdu8xd3jYP227cZP9UCq1Y8GTYRj6wNCNrj5sXehruNILjZsX0-jGOvF5kdJSRV1sLIgRTQecuO0BQnuKZrX5iSc_Vvs3o6AQhArmUnHFv838zYQuXcDvoKZkqYGcWMv4QA'
headers = [
    {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "cookie": cookie
    },
]

# 1. 删除getip()函数（不再使用代理，避免找不到ipdaili.txt文件）
# def getip():  # 随机代理（如果代理不稳定，可注释掉proxies参数）
#     with open("spiders/ipdaili.txt") as f:
#         iplist = f.readlines()
#     proxy = iplist[random.randint(0, len(iplist) - 1)].replace("\n", "")
#     return {'http': f'http://{proxy}'}


def data_processing(inputpath, outputpath):
    def if_wan(x):
        if '万' in str(x):
            x = float(x[:-1]) * 10000
        return x

    df = pd.read_csv(inputpath)
    df = df.dropna(subset=['总评数'])
    df = df.drop_duplicates(subset=['商品id'])
    df['总评数'] = df['总评数'].str.replace('+', '').str.replace('万', '0000').astype(int)
    df['好评数'] = df['好评数'].str.replace('+', '').map(if_wan).astype(int)
    df['默认好评'] = df['默认好评'].str.replace('+', '').map(if_wan).astype(int)
    df['追评数'] = df['追评数'].str.replace('+', '').map(if_wan).astype(int)
    df['视频晒单数'] = df['视频晒单数'].str.replace('+', '').map(if_wan).astype(int)
    df['差评数'] = df['差评数'].str.replace('+', '').map(if_wan).astype(int)
    df['中评数'] = df['中评数'].str.replace('+', '').map(if_wan).astype(int)
    df.to_csv(outputpath, index=False)


def getdata(url, pinpai):
    try:
        # 2. 去掉proxies=getip()参数（关键修改：不使用代理）
        res = requests.get(url, headers=random.choice(headers), timeout=10)
        res.encoding = 'utf-8'
        selector = etree.HTML(res.text)
        list = selector.xpath('//*[@id="J_goodsList"]/ul/li')
        rows = []
        for i in list:
            # 商品id（添加异常捕获，避免部分商品无id导致报错）
            try:
                product_id = i.xpath('.//div[@class="p-commit"]/strong/a/@id')[0].replace("J_comment_", "")
            except IndexError:
                continue
            # 商品名称
            title = i.xpath('.//div[@class="p-name p-name-type-2"]/a/em/text()')
            title = ' '.join(title).replace('\n', '').strip()
            # 价格（添加异常捕获）
            try:
                price = i.xpath('.//div[@class="p-price"]/strong/i/text()')[0]
            except IndexError:
                price = '0'
            # 图片
            img = i.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img')[0] if i.xpath(
                './/div[@class="p-img"]/a/img/@data-lazy-img') else ''
            # 店铺
            shop = i.xpath('.//div[@class="p-shop"]/span/a/text()')[0] if i.xpath(
                './/div[@class="p-shop"]/span/a/text()') else ''
            # 销售量
            try:
                sales = i.xpath('.//div[@class="p-commit"]/strong/a/text()')[0].replace('条评价', '').strip()
            except IndexError:
                sales = '0'
            rows.append([product_id, title, price, shop, pinpai, img, sales])
        return rows
    except Exception as e:
        print(f"爬取失败：{e}")
        return []


def getcommit(data):
    kv = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "cookie": cookie}
    pids = data[0].tolist() if len(data) > 0 else []
    endnum = int(len(pids) / 100) + 1
    for i in range(endnum):
        newpids = pids[100 * i: 100 * (i + 1)]
        if not newpids:
            continue
        comment_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" + ",".join(newpids)
        try:
            # 3. 去掉proxies=getip()参数（关键修改：不使用代理）
            comment_r = requests.get(comment_url, headers=kv, timeout=10)
            p_comment = []
            for comment in comment_r.json()["CommentsCount"]:
                p_comment.append([
                    comment['ProductId'], comment["CommentCountStr"], comment["AverageScore"],
                    comment["GoodCountStr"], comment["DefaultGoodCountStr"], comment["GoodRate"],
                    comment["AfterCountStr"], comment["VideoCountStr"], comment["PoorCountStr"],
                    comment["GeneralCountStr"]
                ])
            with open('spiders/result1.csv', mode='a', encoding='utf-8', newline='') as f1:
                writer = csv.writer(f1)
                if i == 0:
                    writer.writerow(
                        ['商品id', '总评数', '平均得分', '好评数', '默认好评', '好评率', '追评数', '视频晒单数',
                         '差评数', '中评数'])
                writer.writerows(p_comment)
        except Exception as e:
            print(f"评论爬取失败：{e}")


def savedata(data):
    file_path = 'spiders/result.csv'
    exists = os.path.exists(file_path)
    with open(file_path, mode='a+', encoding='utf-8', newline='') as f:
        wirter = csv.writer(f)
        if not exists:
            wirter.writerow(['商品id', '标题', '价格', '店铺', '品牌', '图片', '销售量'])
        wirter.writerows(data)


if __name__ == "__main__":
    brands = ['华为', '苹果', '小米', 'OPPO', 'vivo', '荣耀']
    # 先创建spiders文件夹（避免保存文件时报错）
    if not os.path.exists('spiders3'):
        os.makedirs('spiders3')
    # 每个品牌爬取10页（约300条）
    for brand in brands:
        print(f"开始爬取品牌：{brand}")
        total_data = []
        for page in range(1, 11):
            url = f'https://search.jd.com/search?keyword=手机&wq=手机&ev=exbrand_{brand}%5E&page={2 * page - 1}'
            print(f"爬取第{page}页：{url}")
            page_data = getdata(url, brand)
            if page_data:
                total_data.extend(page_data)
                savedata(page_data)
            time.sleep(random.uniform(2, 5))
        print(f"{brand}爬取完成，共{len(total_data)}条数据\n")

    # 处理评论（可选，若不需要可注释）
    try:
        data = pd.read_csv('spiders/result.csv', header=None)
        getcommit(data)
    except Exception as e:
        print(f"处理评论数据失败：{e}")

    # 数据合并（修正文件名为实际爬取的文件名）
    try:
        df1 = pd.read_csv('spiders/result4.csv', encoding='utf-8')  # 商品基础数据
        df2 = pd.read_csv('spiders/result5.csv', encoding='utf-8')  # 评论数据
        df1['商品id'] = df1['商品id'].astype(str)
        df2['商品id'] = df2['商品id'].astype(str)
        outfile = pd.merge(df1, df2, on='商品id')
        outfile.to_csv('spiders/result_merge.csv', index=False, encoding='utf-8')
        # 数据清洗
        data_processing('spiders/result_merge.csv', 'spiders/result_final.csv')
        print("所有数据处理完成！最终文件：spiders/result_final.csv")
    except Exception as e:
        print(f"数据合并失败：{e}")