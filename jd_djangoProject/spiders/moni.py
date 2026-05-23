import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime
import os

# ========== 关键：初始化Django环境 ==========
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jd_djangoProject.settings")  # 替换为你的项目配置路径
import django
django.setup()
# ===========================================

from myapp.models import PhoneProduct  # 必须在Django环境初始化后导入
# 初始化Faker生成虚假数据
fake = Faker('zh_CN')

# 品牌及对应系列配置（符合市场定位）
brand_series = {
    'vivo': {
        'series': ['Y系列', 'S系列', 'X系列', 'iQOO Neo', 'iQOO Z', 'iQOO数字系列'],
        'price_ranges': [
            (800, 1500),  # Y系列
            (1500, 2500),  # S系列
            (3000, 5000),  # X系列
            (2000, 3500),  # iQOO Neo
            (1000, 2000),  # iQOO Z
            (3500, 6000)  # iQOO数字系列
        ],
        'sales_range': [  # 对应系列的月销量范围（单位：台）
            (50000, 150000),
            (30000, 100000),
            (15000, 50000),
            (20000, 80000),
            (40000, 120000),
            (10000, 40000)
        ],
        'review_ranges': {  # 评论相关属性范围
            '总评数': [(50000, 200000), (30000, 100000), (15000, 50000), (20000, 80000), (40000, 120000),
                       (10000, 40000)],
            '平均得分': [4.8, 4.8, 4.9, 4.8, 4.7, 4.9],
            '好评率': [0.97, 0.96, 0.98, 0.97, 0.95, 0.98],
            '追评数': [(2000, 8000), (1500, 6000), (1000, 4000), (1500, 6000), (2000, 8000), (1000, 4000)],
            '视频晒单数': [(500, 2000), (300, 1000), (200, 800), (300, 1000), (500, 2000), (200, 800)],
            '差评数': [(500, 2000), (300, 1000), (100, 500), (300, 1000), (500, 2000), (100, 500)],
            '中评数': [(300, 1000), (200, 800), (50, 300), (200, 800), (300, 1000), (50, 300)]
        }
    },
    '华为': {
        'series': ['nova系列', 'Mate系列', 'P系列', '畅享系列', '麦芒系列', '荣耀Play'],
        'price_ranges': [
            (2000, 4000),  # nova系列
            (5000, 12000),  # Mate系列
            (4000, 10000),  # P系列
            (1000, 2000),  # 畅享系列
            (1500, 2500),  # 麦芒系列
            (1800, 3000)  # 荣耀Play
        ],
        'sales_range': [
            (25000, 80000),
            (8000, 30000),  # 高端机型销量相对较低但单价高
            (10000, 40000),
            (40000, 120000),
            (20000, 60000),
            (15000, 50000)
        ],
        'review_ranges': {
            '总评数': [(25000, 80000), (8000, 30000), (10000, 40000), (40000, 120000), (20000, 60000), (15000, 50000)],
            '平均得分': [4.7, 4.9, 4.8, 4.6, 4.5, 4.7],
            '好评率': [0.95, 0.98, 0.97, 0.94, 0.93, 0.95],
            '追评数': [(1500, 6000), (800, 3000), (1000, 4000), (2000, 8000), (1000, 4000), (1500, 6000)],
            '视频晒单数': [(300, 1000), (200, 800), (200, 800), (500, 2000), (300, 1000), (300, 1000)],
            '差评数': [(300, 1000), (100, 500), (100, 500), (500, 2000), (300, 1000), (300, 1000)],
            '中评数': [(200, 800), (50, 300), (50, 300), (300, 1000), (200, 800), (200, 800)]
        }
    },
    '小米': {
        'series': ['数字系列', 'Ultra系列', 'Redmi Note', 'Redmi K系列', 'Civi系列', 'Mix系列'],
        'price_ranges': [
            (3000, 5000),  # 数字系列
            (5000, 8000),  # Ultra系列
            (1000, 2000),  # Redmi Note
            (2000, 3500),  # Redmi K系列
            (2000, 3000),  # Civi系列
            (4000, 6000)  # Mix系列
        ],
        'sales_range': [
            (20000, 70000),
            (10000, 30000),
            (80000, 200000),  # 红米Note系列销量极高
            (30000, 100000),
            (15000, 50000),
            (8000, 30000)
        ],
        'review_ranges': {
            '总评数': [(20000, 70000), (10000, 30000), (80000, 200000), (30000, 100000), (15000, 50000), (8000, 30000)],
            '平均得分': [4.8, 4.9, 4.7, 4.8, 4.7, 4.9],
            '好评率': [0.96, 0.98, 0.95, 0.96, 0.95, 0.98],
            '追评数': [(2000, 8000), (1000, 4000), (8000, 20000), (3000, 10000), (1500, 6000), (1000, 4000)],
            '视频晒单数': [(500, 2000), (200, 800), (800, 3000), (500, 2000), (300, 1000), (200, 800)],
            '差评数': [(500, 2000), (100, 500), (800, 3000), (500, 2000), (300, 1000), (100, 500)],
            '中评数': [(300, 1000), (50, 300), (500, 2000), (300, 1000), (200, 800), (50, 300)]
        }
    },
    '荣耀': {
        'series': ['Magic系列', '数字系列', 'X系列', 'Play系列', '畅玩系列', 'Note系列'],
        'price_ranges': [
            (4000, 8000),  # Magic系列
            (2500, 4500),  # 数字系列
            (1000, 2000),  # X系列
            (1500, 2500),  # Play系列
            (800, 1500),  # 畅玩系列
            (2000, 3000)  # Note系列
        ],
        'sales_range': [
            (10000, 40000),
            (20000, 60000),
            (50000, 150000),
            (30000, 90000),
            (40000, 120000),
            (15000, 50000)
        ],
        'review_ranges': {
            '总评数': [(10000, 40000), (20000, 60000), (50000, 150000), (30000, 90000), (40000, 120000),
                       (15000, 50000)],
            '平均得分': [4.8, 4.7, 4.6, 4.7, 4.5, 4.7],
            '好评率': [0.97, 0.95, 0.94, 0.95, 0.93, 0.95],
            '追评数': [(1000, 4000), (2000, 8000), (5000, 15000), (3000, 9000), (4000, 12000), (1500, 6000)],
            '视频晒单数': [(200, 800), (300, 1000), (500, 2000), (300, 1000), (500, 2000), (300, 1000)],
            '差评数': [(100, 500), (200, 800), (500, 2000), (300, 1000), (500, 2000), (300, 1000)],
            '中评数': [(50, 300), (200, 800), (300, 1000), (200, 800), (300, 1000), (200, 800)]
        }
    },
    'oppo': {
        'series': ['Find X系列', 'Reno系列', 'Ace系列', 'K系列', 'A系列', 'Realme Q系列'],
        'price_ranges': [
            (4000, 8000),  # Find X系列
            (2000, 4000),  # Reno系列
            (3000, 5000),  # Ace系列
            (1500, 2500),  # K系列
            (1000, 2000),  # A系列
            (1000, 2000)  # Realme Q系列
        ],
        'sales_range': [
            (8000, 30000),
            (25000, 80000),
            (15000, 50000),
            (40000, 120000),
            (50000, 150000),
            (30000, 90000)
        ],
        'review_ranges': {
            '总评数': [(8000, 30000), (25000, 80000), (15000, 50000), (40000, 120000), (50000, 150000), (30000, 90000)],
            '平均得分': [4.9, 4.8, 4.8, 4.7, 4.6, 4.7],
            '好评率': [0.98, 0.96, 0.96, 0.95, 0.94, 0.95],
            '追评数': [(800, 3000), (2500, 8000), (1500, 5000), (4000, 12000), (5000, 15000), (3000, 9000)],
            '视频晒单数': [(200, 800), (300, 1000), (300, 1000), (500, 2000), (500, 2000), (300, 1000)],
            '差评数': [(100, 500), (200, 800), (300, 1000), (500, 2000), (500, 2000), (300, 1000)],
            '中评数': [(50, 300), (200, 800), (200, 800), (300, 1000), (300, 1000), (200, 800)]
        }
    },
    '真我': {
        'series': ['GT系列', 'Neo系列', 'Q系列', 'X系列', 'V系列', '数字系列'],
        'price_ranges': [
            (2500, 4000),  # GT系列
            (1500, 3000),  # Neo系列
            (1000, 2000),  # Q系列
            (1500, 2500),  # X系列
            (1000, 1800),  # V系列
            (2000, 3500)  # 数字系列
        ],
        'sales_range': [
            (15000, 50000),
            (30000, 100000),
            (40000, 120000),
            (25000, 80000),
            (35000, 100000),
            (20000, 60000)
        ],
        'review_ranges': {
            '总评数': [(15000, 50000), (30000, 100000), (40000, 120000), (25000, 80000), (35000, 100000),
                       (20000, 60000)],
            '平均得分': [4.8, 4.7, 4.6, 4.7, 4.6, 4.7],
            '好评率': [0.97, 0.95, 0.94, 0.95, 0.94, 0.95],
            '追评数': [(1500, 6000), (3000, 10000), (4000, 12000), (2500, 8000), (3500, 10000), (2000, 6000)],
            '视频晒单数': [(300, 1000), (500, 2000), (500, 2000), (300, 1000), (500, 2000), (300, 1000)],
            '差评数': [(300, 1000), (500, 2000), (500, 2000), (300, 1000), (500, 2000), (300, 1000)],
            '中评数': [(200, 800), (300, 1000), (300, 1000), (200, 800), (300, 1000), (200, 800)]
        }
    }
}

# 常见手机配置特征
feature_tags = [
    '5G', '6400万像素', '1亿像素', 'OIS光学防抖', '快充', '无线充电',
    '高刷新率', '曲面屏', '轻薄机身', '大电池', '骁龙处理器', '天玑处理器',
    '自研芯片', '游戏优化', '拍照神器', '全面屏'
]

# 生成数据
data = []
total_records = 2000

for i in range(total_records):
    # 随机选择品牌
    brand = random.choice(list(brand_series.keys()))
    brand_info = brand_series[brand]

    # 随机选择系列及对应配置
    series_idx = random.randint(0, len(brand_info['series']) - 1)
    series = brand_info['series'][series_idx]
    price_min, price_max = brand_info['price_ranges'][series_idx]
    sales_min, sales_max = brand_info['sales_range'][series_idx]
    review_ranges = brand_info['review_ranges']

    # 生成具体数据
    price = round(random.uniform(price_min, price_max), 1)
    sales = random.randint(sales_min, sales_max)

    # 随机选择2-4个特征
    features = random.sample(feature_tags, random.randint(2, 4))
    feature_str = ' '.join(features)

    # 生成标题
    title = f"{brand} {series} {feature_str}"

    # 生成商品ID（模拟京东格式）
    product_id = f"100{random.randint(100000000000, 999999999999)}"

    # 生成店铺（官方旗舰店为主）
    if brand == 'vivo' and 'iQOO' in series:
        shop = 'iQOO京东自营官方店'
    elif brand == 'oppo' and 'Realme' in series:
        shop = 'realme真我京东自营官方旗舰店'
    else:
        shop = f"{brand}京东自营官方旗舰店"

    # 生成图片URL（模拟）
    img_url = f"//img{random.randint(10, 20)}.360buyimg.com/n7/jfs/{fake.md5()[:10]}.jpg"

    # 生成评论相关属性
    total_reviews = random.randint(review_ranges['总评数'][series_idx][0], review_ranges['总评数'][series_idx][1])
    avg_score = review_ranges['平均得分'][series_idx]
    praise_rate = review_ranges['好评率'][series_idx]
    follow_reviews = random.randint(review_ranges['追评数'][series_idx][0], review_ranges['追评数'][series_idx][1])
    video_reviews = random.randint(review_ranges['视频晒单数'][series_idx][0],
                                   review_ranges['视频晒单数'][series_idx][1])
    negative_reviews = random.randint(review_ranges['差评数'][series_idx][0], review_ranges['差评数'][series_idx][1])
    neutral_reviews = random.randint(review_ranges['中评数'][series_idx][0], review_ranges['中评数'][series_idx][1])

    # 计算好评数（总评数 - 差评数 - 中评数）
    praise_reviews = total_reviews - negative_reviews - neutral_reviews
    # 默认好评设为总评数的80%-95%（模拟平台默认好评逻辑）
    default_praise = random.randint(int(total_reviews * 0.8), int(total_reviews * 0.95))

    # 添加到数据列表
    # 添加到数据列表（键名与修改后的模型字段完全一致）
    data.append({
        'id': random.randint(100000000000, 999999999999),  # 生成唯一大整数ID
        'product_id': product_id,
        'product_name': title,  # 原脚本的“标题”对应“商品名”
        'price': str(price),  # 转为字符串，与模型字段类型匹配
        'shop': shop,
        'brand': brand,
        'img_url': img_url,
        'sales': sales , # 月销量字段
        'CommentCountStr': total_reviews,
        'AverageScore': str(avg_score),  # 转为字符串，与真实数据格式一致
        'GoodCountStr': str(praise_reviews),  # 转为字符串
        'DefaultGoodCountStr': str(default_praise),  # 转为字符串
        'GoodRate': f"{praise_rate:.2%}",  # 转为百分比字符串（如“98.00%”）
        'AfterCountStr': str(follow_reviews),  # 转为字符串
        'VideoCountStr': str(video_reviews),  # 转为字符串
        'PoorCountStr': str(negative_reviews),  # 转为字符串
        'GeneralCountStr': str(neutral_reviews),  # 转为字符串

    })

# 将数据转换为DataFrame
df = pd.DataFrame(data)

# 保存为固定名称的CSV文件（覆盖原有文件，若需保留历史可加时间戳）
csv_path = "result4.csv"  # 固定文件名
df.to_csv(csv_path, index=False, encoding='utf-8-sig')  # utf-8-sig确保中文正常显示

print(f"数据生成完成！共{total_records}条记录")
print(f"CSV文件已保存至：{os.path.abspath(csv_path)}")  # 显示完整路径
# 转换data列表为PhoneProduct对象列表
phone_objects = [
    PhoneProduct(
        id=item['id'],
        product_id=item['product_id'],
        product_name=item['product_name'],
        price=item['price'],
        shop=item['shop'],
        brand=item['brand'],
        img_url=item['img_url'],
        sales=item['sales'],
        CommentCountStr=item['CommentCountStr'],
        AverageScore=item['AverageScore'],
        GoodCountStr=item['GoodCountStr'],
        DefaultGoodCountStr=item['DefaultGoodCountStr'],
        GoodRate=item['GoodRate'],
        AfterCountStr=item['AfterCountStr'],
        VideoCountStr=item['VideoCountStr'],
        PoorCountStr=item['PoorCountStr'],
        GeneralCountStr=item['GeneralCountStr']
    ) for item in data
]

# 批量写入数据库
PhoneProduct.objects.bulk_create(phone_objects)

print(f"成功写入{len(data)}条数据到数据库！")