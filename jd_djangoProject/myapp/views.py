from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
import re
from random import sample
import jieba
from .models import User, XinXi, Comment,PhoneProduct
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import pandas as pd
from collections import Counter
import os
from django.conf import settings
from joblib import load

MODEL_PATH = os.path.join(settings.BASE_DIR, "rf_sales_prediction_model.joblib")
BRAND_ENCODER_PATH = os.path.join(settings.BASE_DIR, "brand_encoder.joblib")
TARGET_ENCODER_PATH = os.path.join(settings.BASE_DIR, "target_encoder.joblib")

# 关键：打印实际加载的模型路径（添加这三行）
print("模型加载路径：", MODEL_PATH)
print("品牌编码器路径：", BRAND_ENCODER_PATH)
print("目标编码器路径：", TARGET_ENCODER_PATH)

# 尝试加载模型和编码器
try:
    rf_model = load(MODEL_PATH)
    brand_encoder = load(BRAND_ENCODER_PATH)
    target_encoder = load(TARGET_ENCODER_PATH)
except Exception as e:
    print(f"模型加载失败: {e}")
    rf_model = None
    brand_encoder = None
    target_encoder = None


def Speculate(data):
    """预测函数：接收特征数据，返回销量区间"""
    if not all([rf_model, brand_encoder, target_encoder]):
        return "模型未加载成功"

    try:
        # 解析输入数据（price, brand, rating, average_score）
        price, brand, rating, average_score = data

        # 品牌编码（必须与训练时的编码规则一致）
        if brand not in brand_encoder.classes_:
            return "未知品牌，无法预测"

        brand_encoded = brand_encoder.transform([brand])[0]

        # 构造特征DataFrame（列顺序与训练时一致）
        features = pd.DataFrame({
            "price": [price],
            "brand": [brand_encoded],
            "GoodRate": [rating],
            "AverageScore": [average_score]
        })

        # 模型预测与解码
        pred_encoded = rf_model.predict(features)[0]
        pred_label = target_encoder.inverse_transform([pred_encoded])[0]
        return pred_label

    except Exception as e:
        print(f"预测失败: {e}")
        return "预测出错"


# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'signin.html')
    elif request.method == 'POST':
        res = request.POST

        obj = User.objects.filter(username=res['username'])

        if obj:
            obj = obj[0]
            if check_password(res['password'], obj.password):
                request.session['user'] = obj.id
            return HttpResponse('<script>alert("登陆成功！");location.href="/index"</script>')
        return HttpResponse('<script>alert("用户名或密码不正确！");location.href="/login/"</script>')
    else:
        return HttpResponse('<script>alert("请求方式不正确")</script>')


def loginout(request):
    try:
        del request.session['user']
    except:
        pass
    return HttpResponse('<script>alert("退出成功！");location.href="/"</script>')


def register(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    elif request.method == 'POST':
        try:
            obj = User()
            obj.username = request.POST['username']
            obj.password = make_password(request.POST['password'], None, "pbkdf2_sha256")

            obj.save()
            return HttpResponse('<script>alert("注册成功，跳转登陆！");location.href="/"</script>')
        except:
            return HttpResponse('<script>alert("注册失败，请重新尝试！");location.href="/register/"</script>')
    else:
        return HttpResponse('<script>alert("请求方式不正确！");location.href="/register/"</script>')


def index(request):
    # 1. 按总评数降序排序，取前5条（已添加排序，无分页警告问题）
    products = XinXi.objects.order_by('-CommentCountStr')[:5]  # 已有order_by，无需担心分页警告

    for product in products:
        try:
            # 2. 安全处理好评率转换（处理空值、非数字格式）
            # 假设GoodRate是小数（如0.95）或字符串格式的小数（如"0.95"）
            good_rate = float(product.GoodRate) if product.GoodRate else 0.0
            # 转换为百分比字符串（如0.95 → "95%"）
            product.GoodRatePercent = f"{int(good_rate * 100)}%"
        except (ValueError, TypeError) as e:
            # 处理转换失败的情况（如非数字字符串、None等）
            product.GoodRatePercent = "0%"
            # 可选：打印错误日志便于调试
            print(f"好评率转换错误：{e}，商品ID：{product.id}")

    # 3. 传递数据到模板
    context = {'products': products}
    return render(request, 'index.html', context)


def ecommerce_products(request):
    query = request.GET.get('search', '')
    page_number = request.GET.get('page')  # 获取请求中的页码参数
    if query:
        products = XinXi.objects.filter(product_name__icontains=query)
    else:
        products = XinXi.objects.all()

    # 创建分页器对象，设置每页显示的数量为 10
    paginator = Paginator(products, 10)

    # 获取请求的页码对应的Page对象
    page_obj = paginator.get_page(page_number)

    # 计算评分星星
    for product in page_obj.object_list:
        product.full_stars = ['bx bxs-star text-warning'] * int(product.AverageScore)
        product.empty_stars = ['bx bxs-star text-secondary'] * (5 - int(product.AverageScore))
        product.GoodRatePercent = "{:.0f}%".format(float(product.GoodRate) * 100)

    context = {
        'products': [
            {'product': product, 'full_stars': product.full_stars, 'empty_stars': product.empty_stars}
            for product in page_obj.object_list
        ],
        'page_obj': page_obj,
        'query': query,  # 添加搜索参数到上下文中
    }

    return render(request, 'ecommerce-products.html', context)


def products_details(request):
    id = request.GET.get('id')
    product = get_object_or_404(XinXi, id=id)
    product.full_stars = ['bx bxs-star text-warning'] * int(product.AverageScore)
    product.empty_stars = ['bx bxs-star text-secondary'] * (5 - int(product.AverageScore))

    # 查询同一品牌的其他商品
    brand = product.brand
    other_products = XinXi.objects.filter(brand=brand).exclude(id=id)[:3]

    # 如果不足三个商品，则随机选取
    if len(other_products) < 3:
        other_products = XinXi.objects.filter(brand=brand).exclude(id=id)
        other_products = sample(list(other_products), min(len(other_products), 3))

    # 计算评分星星
    for product in other_products:
        product.full_stars = ['bx bxs-star text-warning'] * int(product.AverageScore)
        product.empty_stars = ['bx bxs-star text-secondary'] * (5 - int(product.AverageScore))
    comments = Comment.objects.filter(product_id=product.product_id).order_by('-comment_date')[:5]
    context = {
        'product': product,
        'other_products': other_products,
        'comments': comments,
    }

    return render(request, 'ecommerce-products-details.html',context)


def ecommerce_comment_list(request):
    query = request.GET.get('search', '')
    page_number = request.GET.get('page')  # 获取请求中的页码参数
    if query:
        comments = Comment.objects.filter(content__icontains=query)
    else:
        comments = Comment.objects.all()

    # 创建分页器对象，设置每页显示的数量为 10
    paginator = Paginator(comments, 10)

    # 获取请求的页码对应的Page对象
    page_obj = paginator.get_page(page_number)

    context = {
        'comments': page_obj,
        'page_obj': page_obj,
        'query': query,  # 添加搜索参数到上下文中
    }
    return render(request, 'ecommerce_comment_list.html',context)


def widgets(request):
    return render(request, 'widgets.html')


def chart(request):
    return render(request, 'charts-apex-chart.html')

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    words = jieba.lcut(text)
    filtered_words = [word for word in words if len(word) > 1]

    return filtered_words

def comment_chart(request):
    df = pd.read_csv('spiders/comments.csv')
    df = df[['评论']]

    all_text = ' '.join(df.values.flatten().astype(str))

    words = preprocess_text(all_text)
    word_count = Counter(words)
    top_50_words = word_count.most_common(200)

    result = [{'name': word, 'value': count} for word, count in top_50_words]

    # --------------------------
    # 2. 新增：情感分布和品牌对比数据统计（基于你的模型字段）
    # --------------------------
    # 品牌标准化函数
    def standardize_brand(brand):
        if not brand:
            return "未知品牌"
        brand_str = str(brand).strip()
        # 去除中文/英文括号及内容，统一小写避免重复
        brand_str = re.sub(r'（.*?）|\(.*?\)', '', brand_str)
        return brand_str.strip().lower()

    # 处理真实数据（XinXi表）
    real_data = []
    for item in XinXi.objects.all():
        try:
            # 提取并转换好评/中评/差评数（处理空值和非数字）
            good = int(str(item.GoodCountStr).strip()) if item.GoodCountStr else 0
            mid = int(str(item.GeneralCountStr).strip()) if item.GeneralCountStr else 0
            bad = int(str(item.PoorCountStr).strip()) if item.PoorCountStr else 0
        except (ValueError, TypeError):
            good = mid = bad = 0
        real_data.append({
            'brand': standardize_brand(item.brand),
            'good': good,
            'mid': mid,
            'bad': bad
        })

    # 处理模拟数据（PhoneProduct表）
    sim_data = []
    for item in PhoneProduct.objects.all():
        try:
            good = int(str(item.GoodCountStr).strip()) if item.GoodCountStr else 0
            mid = int(str(item.GeneralCountStr).strip()) if item.GeneralCountStr else 0
            bad = int(str(item.PoorCountStr).strip()) if item.PoorCountStr else 0
        except (ValueError, TypeError):
            good = mid = bad = 0
        sim_data.append({
            'brand': standardize_brand(item.brand),
            'good': good,
            'mid': mid,
            'bad': bad
        })

    # 合并数据并统计
    all_data = real_data + sim_data
    df_stats = pd.DataFrame(all_data)

    # 总好评/中评/差评数
    total_good = df_stats['good'].sum()
    total_mid = df_stats['mid'].sum()
    total_bad = df_stats['bad'].sum()

    # 按品牌统计（排除未知品牌，取前6个有数据的品牌）
    brand_stats = df_stats.groupby('brand').agg({
        'good': 'sum',
        'bad': 'sum'
    }).reset_index()
    valid_brands = brand_stats[
        (brand_stats['brand'] != '未知品牌') &
        (brand_stats['good'] + brand_stats['bad'] > 0)
        ].sort_values(by='good', ascending=False).head(6)

    # --------------------------
    # 3. 传递数据（保留词云图result，新增统计数据）
    # --------------------------
    context = {
        # 词云图数据（完全不变，确保原有功能正常）
        'result': result,
        # 评论情感分布数据（给前端图表使用）
        'total_good': total_good,
        'total_mid': total_mid,
        'total_bad': total_bad,
        # 品牌对比数据（给前端图表使用）
        'brand_list': valid_brands['brand'].tolist(),
        'brand_good': valid_brands['good'].tolist(),
        'brand_bad': valid_brands['bad'].tolist(),
    }

    return render(request, 'comment_chart.html', context)

from speculate import Speculate


def predict(request):
    result = None
    if request.method == 'POST':
        # 获取表单数据
        brand = request.POST.get('brand', '').strip()
        rating = request.POST.get('rating', 0)
        price = request.POST.get('price', 0)
        average_score = request.POST.get('average_score', 5)

        try:
            # 数据清洗
            price = float(price)
            rating = float(rating)
            average_score = float(average_score)

            # 好评率处理（0-1范围）
            if rating > 1:
                rating /= 100
            rating = max(0, min(1, rating))

            # 平均得分处理（1-5范围）
            average_score = max(1, min(5, average_score))

            # 品牌验证
            valid_brands = ["荣耀", "华为", "小米", "vivo", "真我", "OPPO"]
            if not brand or brand not in valid_brands:
                result = "请选择有效的品牌"
            else:
                result = Speculate([price, brand, rating, average_score])

        except ValueError:
            result = "输入格式错误，请检查数字类型"
        except Exception as e:
            result = f"系统错误: {str(e)[:20]}"

    return render(request, 'predict.html', {'result': result})

def index(request):
    # 1. 查询各表数据量
    total_real_data = XinXi.objects.count()  # 真实数据表（XinXi）数据量
    total_simulated_data = PhoneProduct.objects.count()  # 模拟数据表（PhoneProduct）数据量
    total_comment_data = Comment.objects.count()  # 评论表（Comment）数据量
    total_all_data = total_real_data + total_simulated_data  # 真实+模拟的总数据量

    # 2. 原有商品排行查询（保持不变）
    products = XinXi.objects.all().order_by('-CommentCountStr')[:10]  # 按总评数倒序取前10

    # 3. 传递所有数据到模板
    context = {
        # 新增：真实数据、模拟数据、总数据量
        'total_real_data': total_real_data,
        'total_simulated_data': total_simulated_data,
        'total_all_data': total_all_data,
        # 原有变量保留
        'products': products,
        'processed_data_count': total_comment_data  # 原评论数据量变量名保持一致，避免模板报错
        # 其他变量...
    }

    # 4. 渲染模板
    return render(request, 'index.html', context)


def widgets(request):
    # 1. 读取真实和模拟数据的品牌
    real_brands = list(XinXi.objects.values_list('brand', flat=True))  # 真实数据（含大写OPPO）
    simulated_brands = list(PhoneProduct.objects.values_list('brand', flat=True))  # 模拟数据

    # 2. 清洗函数：处理括号+统一OPPO为小写
    def standardize_brand(brand):
        if not brand:
            return "未知品牌"
        brand_str = str(brand).strip()  # 转字符串并去空格

        # 步骤1：去除中文括号及内部内容（如“OPPO（欧珀）”→“OPPO”）
        cleaned = re.sub(r'（.*?）', '', brand_str).strip()

        # 步骤2：将“OPPO”统一转为小写“oppo”
        if cleaned.upper() == "OPPO":  # 不区分原始大小写，只要是OPPO就转小写
            return "oppo"

        # 其他品牌保持原样（如小米、华为等）
        return cleaned

    # 3. 应用清洗规则
    real_cleaned = [standardize_brand(b) for b in real_brands]  # 真实数据清洗后（OPPO→oppo）
    simulated_cleaned = [standardize_brand(b) for b in simulated_brands]  # 模拟数据同步处理

    # 4. 合并统计
    combined_df = pd.DataFrame({'brand': real_cleaned + simulated_cleaned})
    brand_distribution = combined_df['brand'].value_counts().to_dict()
    brand_data = [{'name': name, 'value': count} for name, count in brand_distribution.items()]
    # ========== 2. 只统计模拟数据的店铺商品数量 ==========
    # 只读取模拟数据（PhoneProduct）的店铺字段
    simulated_shops = list(PhoneProduct.objects.values_list('shop', flat=True))

    # 统计模拟数据中各店铺的商品数量
    simulated_shop_df = pd.DataFrame({'shop': simulated_shops})
    shop_distribution = simulated_shop_df['shop'].value_counts().to_dict()
    # 转换为 ECharts 格式
    shop_data = [{'name': name, 'value': count} for name, count in shop_distribution.items()]

    # 3.1 读取真实和模拟数据的价格字段（假设字段名为price，确保模型中有此字段）
    # 注意：需将价格转换为数值类型（处理可能的字符串/空值）
    def get_price_list(model):
        price_list = []
        for price in model.objects.values_list('price', flat=True):
            try:
                # 处理可能的字符串价格（如"¥1999"→1999）
                if isinstance(price, str):
                    # 去除非数字字符（如¥、,）
                    price_clean = re.sub(r'[^\d.]', '', price)
                    price_num = float(price_clean)
                else:
                    price_num = float(price)
                price_list.append(price_num)
            except:
                # 无法转换的价格视为无效值，跳过
                continue
        return price_list

    # 读取真实数据价格和模拟数据价格
    real_prices = get_price_list(XinXi)
    simulated_prices = get_price_list(PhoneProduct)

    # 3.2 合并价格数据并划分区间
    all_prices = real_prices + simulated_prices  # 合并真实+模拟价格
    price_df = pd.DataFrame({'price': all_prices})

    # 定义价格区间（可根据需求调整）
    bins = [0, 1000, 2000, 3000, 4000, float('inf')]  # 区间：0-1000、1000-2000、...、4000+
    labels = ["0-1000", "1000-2000", "2000-3000", "3000-4000", "4000+"]  # 区间名称

    # 划分区间并统计数量
    price_df['price_range'] = pd.cut(price_df['price'], bins=bins, labels=labels, include_lowest=True)
    price_distribution = price_df['price_range'].value_counts().reindex(labels, fill_value=0).to_dict()

    # 转换为ECharts需要的格式：[{name: "区间名", value: 数量}, ...]
    price_data = [{'name': name, 'value': count} for name, count in price_distribution.items()]
    real_counts = list(XinXi.objects.values_list('CommentCountStr', flat=True))  # 真实数据
    simulated_counts = list(PhoneProduct.objects.values_list('CommentCountStr', flat=True))  # 模拟数据

    # 合并数据并转换为数值类型（确保统计有效）
    all_counts = []
    for count in real_counts + simulated_counts:
        try:
            all_counts.append(float(count))  # 直接转数值，无需额外清洗
        except:
            continue  # 跳过极个别无效值（若数据完全干净，可删除try-except）

    # 万级区间划分（可根据数据调整）
    bins = [0, 10000, 50000, 100000, 150000, float('inf')]  # 0-1万、1-5万、5-10万、10-50万、50万+
    labels = ["0-1万", "1-5万", "5-10万", "10-15万", "15万+"]

    # 统计各区间数量
    counts_df = pd.DataFrame({'count': all_counts})
    counts_df['range'] = pd.cut(
        counts_df['count'],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    range_distribution = counts_df['range'].value_counts().reindex(labels, fill_value=0).to_dict()

    # 转换为ECharts格式
    comment_range_data = [{'name': k, 'value': v} for k, v in range_distribution.items()]
    # ========== 4. 传递所有数据到模板 ==========
    context = {
        'brand_data': brand_data,
        'shop_data': shop_data,
        'price_data': price_data,  # 新增价格区间数据
        'comment_range_data': comment_range_data  # 万级评论数区间数据
    }
    return render(request, 'widgets.html', context)




import re
import pandas as pd
from django.shortcuts import render
from .models import XinXi, PhoneProduct


def brand_analysis(request):
    # 1. 手机类型判断函数（按价格划分）
    def get_phone_type(price):
        if price >= 5000:
            return "旗舰机"
        elif 3000 <= price < 5000:
            return "中端机"
        else:
            return "入门机"

    # 2. 品牌标准化函数
    def standardize_brand(brand):
        if not brand:
            return "未知品牌"
        brand_str = str(brand).strip()
        cleaned = re.sub(r'（.*?）', '', brand_str).strip()
        if cleaned.upper() == "OPPO":
            return "oppo"
        return cleaned

    # 3. 处理真实评论数据（XinXi表）
    real_comments = []
    for item in XinXi.objects.all():
        standardized_brand = standardize_brand(item.brand)
        # 价格清洗
        price_str = str(item.price).strip() if item.price else "0"
        price = float(re.sub(r'[^\d.]', '', price_str)) if price_str else 0.0
        # 计算手机类型
        phone_type = get_phone_type(price)
        # 其他字段处理
        avg_score = float(item.AverageScore) if item.AverageScore else 0.0
        good_rate = float(item.GoodRate) * 100 if item.GoodRate else 0
        poor_count = int(item.PoorCountStr) if item.PoorCountStr else 0

        real_comments.append({
            'brand': standardized_brand,
            'type': phone_type,
            'price': price,
            'avg_score': avg_score,
            'good_rate': good_rate,
            'poor_count': poor_count
        })
    real_df = pd.DataFrame(real_comments)

    # 4. 处理模拟销售数据（PhoneProduct表）
    sim_sales = []
    for item in PhoneProduct.objects.all():
        standardized_brand = standardize_brand(item.brand)
        # 价格清洗
        price_str = str(item.price).strip() if item.price else "0"
        price = float(re.sub(r'[^\d.]', '', price_str)) if price_str else 0.0
        # 计算手机类型
        phone_type = get_phone_type(price)
        # 其他字段处理
        sales = int(item.sales) if item.sales else 0
        avg_score = float(item.AverageScore) if item.AverageScore else 0.0
        good_rate_str = str(item.GoodRate).strip() if item.GoodRate else "0%"
        good_rate = float(re.sub(r'[%]', '', good_rate_str)) if good_rate_str else 0
        poor_count = int(item.PoorCountStr) if item.PoorCountStr else 0

        sim_sales.append({
            'brand': standardized_brand,
            'type': phone_type,
            'price': price,
            'sales': sales,
            'avg_score': avg_score,
            'good_rate': good_rate,
            'poor_count': poor_count
        })
    sim_df = pd.DataFrame(sim_sales)

    # 5. 保留原有数据聚合（用于原有图表）
    # 5.1 全价位品牌聚合（原有逻辑）
    real_agg_old = real_df.groupby('brand').agg(
        avg_score=('avg_score', 'mean'),
        avg_good_rate=('good_rate', 'mean'),
        total_poor=('poor_count', 'sum')
    ).reset_index()

    sim_agg_old = sim_df.groupby('brand').agg(
        total_sales=('sales', 'sum'),
        avg_score=('avg_score', 'mean'),
        avg_good_rate=('good_rate', 'mean'),
        total_poor=('poor_count', 'sum')
    ).reset_index()

    all_brands_old = list(set(real_agg_old['brand'].tolist() + sim_agg_old['brand'].tolist()))
    all_brands_df_old = pd.DataFrame({'brand': all_brands_old})
    merged_real_old = pd.merge(all_brands_df_old, real_agg_old, on='brand', how='left').fillna(0)
    merged_sim_old = pd.merge(all_brands_df_old, sim_agg_old, on='brand', how='left').fillna(0)

    brand_df_old = pd.DataFrame({
        'brand': all_brands_old,
        'total_sales': merged_sim_old['total_sales'],
        'avg_score': (merged_real_old['avg_score'] + merged_sim_old['avg_score']) / 2,
        'avg_good_rate': (merged_real_old['avg_good_rate'] + merged_sim_old['avg_good_rate']) / 2,
        'total_poor': merged_real_old['total_poor'] + merged_sim_old['total_poor']
    }).round(1)

    # ------------ 核心修改：将3000-4000元扩展为0-6000元多价位段 ------------
    # 定义包含6000元以上的价位段
    price_ranges = [
        ("0-2000元", 0, 2000),
        ("2000-4000元", 2000, 4000),
        ("4000-6000元", 4000, 6000),
        ("6000元以上", 6000, float('inf'))  # 新增6000元以上区间，用inf表示无穷大
    ]

    # 处理多价位数据
    multi_price_data = []
    for range_name, min_p, max_p in price_ranges:
        # 筛选该价位段的真实数据（包含6000元以上）
        real_range = real_df[(real_df['price'] >= min_p) & (real_df['price'] < max_p)]
        # 筛选该价位段的模拟数据
        sim_range = sim_df[(sim_df['price'] >= min_p) & (sim_df['price'] < max_p)]

        # 计算该价位段的总销量和平均好评率
        total_sales = sim_range['sales'].sum()
        avg_good_rate = (real_range['good_rate'].mean() + sim_range['good_rate'].mean()) / 2

        if total_sales > 0:
            multi_price_data.append({
                'price_range': range_name,
                'sales': int(total_sales),
                'good_rate': round(avg_good_rate, 1) if not pd.isna(avg_good_rate) else 0
            })
    # 6. 新增：品牌+类型双维度聚合（用于新增图表）
    # 6.1 真实数据按品牌+类型聚合
    real_agg = real_df.groupby(['brand', 'type']).agg(
        avg_score_real=('avg_score', 'mean'),
        good_rate_real=('good_rate', 'mean'),
        poor_real=('poor_count', 'sum')
    ).reset_index()

    # 6.2 模拟数据按品牌+类型聚合
    sim_agg = sim_df.groupby(['brand', 'type']).agg(
        sales=('sales', 'sum'),
        avg_score_sim=('avg_score', 'mean'),
        good_rate_sim=('good_rate', 'mean'),
        poor_sim=('poor_count', 'sum')
    ).reset_index()

    # 6.3 合并真实与模拟数据
    merged_df = pd.merge(real_agg, sim_agg, on=['brand', 'type'], how='outer').fillna(0)

    # 6.4 计算最终指标
    final_df = merged_df.assign(
        avg_score=(merged_df['avg_score_real'] + merged_df['avg_score_sim']) / 2,
        good_rate=(merged_df['good_rate_real'] + merged_df['good_rate_sim']) / 2,
        total_poor=merged_df['poor_real'] + merged_df['poor_sim']
    ).round(1)

    # 7. 格式化所有前端所需数据
    # 7.1 原有图表数据
    brand_sales_data = [
        {'brand': row['brand'], 'total_sales': int(row['total_sales']), 'avg_score': row['avg_score']}
        for _, row in brand_df_old.iterrows()
    ]
    reputation_data = [
        {'brand': row['brand'], 'avg_good_rate': row['avg_good_rate'], 'total_poor': int(row['total_poor']),
         'avg_score': row['avg_score']}
        for _, row in brand_df_old.iterrows()
    ]
    sales_rate_data = [
        {'brand': row['brand'], 'sales': int(row['total_sales']), 'good_rate': row['avg_good_rate']}
        for _, row in brand_df_old.iterrows()
    ]

    # 7.2 新增图表数据（品牌+类型）
    brand_type_data = [
        {
            'brand': row['brand'],
            'type': row['type'],
            'sales': int(row['sales']),
            'avg_score': row['avg_score'],
            'good_rate': row['good_rate'],
            'total_poor': int(row['total_poor'])
        }
        for _, row in final_df.iterrows()
        if row['sales'] > 0
    ]

    # 8. 传递所有数据到前端（用multi_price_data替代原mid_price_data）
    return render(request, 'charts-apex-chart.html', {
        'brand_sales_data': brand_sales_data,
        'reputation_data': reputation_data,
        'sales_rate_data': sales_rate_data,
        'brand_type_data': brand_type_data,
        'multi_price_data': multi_price_data  # 新增多价位数据
    })