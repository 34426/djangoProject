import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from joblib import dump
from django.db.models import F
import os
import django
import sys
# ----------------------
# 1. 定位根目录（关键修改）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 2. 加入搜索路径（关键修改）
sys.path.append(BASE_DIR)
# 3. 设置配置文件路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jd_djangoProject.settings')
# 4. 初始化Django
django.setup()

# 导入模型（避免重复导入）
from myapp.models import XinXi, PhoneProduct


# ----------------------
# 2. 读取并处理真实数据（XinXi）
# ----------------------
real_queryset = XinXi.objects.values(
    'price', 'brand', 'GoodRate', 'AverageScore',
    total_comments=F('CommentCountStr')  # 用总评数代理销量
)
real_df = pd.DataFrame(list(real_queryset))

# 数据清洗（兼容1.0.2版本，处理空值和格式）
real_df['price'] = real_df['price'].str.extract(r'(\d+\.?\d*)').astype(float)
real_df['GoodRate'] = real_df['GoodRate'].astype(float, errors='ignore')  # 容错处理
real_df['AverageScore'] = real_df['AverageScore'].astype(float, errors='ignore')
real_df['sales'] = real_df['total_comments'].astype(float, errors='ignore')  # 销量代理列


# ----------------------
# 3. 读取并处理模拟数据（PhoneProduct）
# ----------------------
sim_queryset = PhoneProduct.objects.values(
    'price', 'brand', 'GoodRate', 'AverageScore', 'sales'
)
sim_df = pd.DataFrame(list(sim_queryset))

# 数据清洗
sim_df['price'] = sim_df['price'].str.extract(r'(\d+\.?\d*)').astype(float)
sim_df['GoodRate'] = sim_df['GoodRate'].str.replace('%', '').astype(float, errors='ignore') / 100
sim_df['AverageScore'] = sim_df['AverageScore'].astype(float, errors='ignore')
sim_df['sales'] = sim_df['sales'].astype(float, errors='ignore')  # 确保销量为数值型


# ----------------------
# 4. 合并数据并处理缺失值
# ----------------------
combined_df = pd.concat([
    real_df[['price', 'brand', 'GoodRate', 'AverageScore', 'sales']],
    sim_df[['price', 'brand', 'GoodRate', 'AverageScore', 'sales']]
], ignore_index=True)

# 缺失值填充（更稳健的处理）
combined_df['price'] = combined_df['price'].fillna(combined_df['price'].median())  # 中位数抗异常值
combined_df['brand'] = combined_df['brand'].fillna(combined_df['brand'].mode()[0] if not combined_df['brand'].mode().empty else '未知品牌')
combined_df['GoodRate'] = combined_df['GoodRate'].fillna(combined_df['GoodRate'].mean())
combined_df['AverageScore'] = combined_df['AverageScore'].fillna(combined_df['AverageScore'].mean())
combined_df['sales'] = combined_df['sales'].fillna(combined_df['sales'].median())

# 过滤异常值（避免极端值影响模型）
combined_df = combined_df[
    (combined_df['price'] > 0) &
    (combined_df['GoodRate'] >= 0) & (combined_df['GoodRate'] <= 1) &
    (combined_df['AverageScore'] >= 0) & (combined_df['AverageScore'] <= 5) &
    (combined_df['sales'] >= 0)
]


# ----------------------
# 5. 定义销量区间（目标变量）
# ----------------------
# 动态计算分位数划分区间（比固定区间更适配数据分布）
sales_bins = [0] + list(combined_df['sales'].quantile([0.25, 0.5, 0.75])) + [float('inf')]
sales_labels = ['低销量', '中等销量', '高销量', '超高销量']
combined_df['sales_range'] = pd.cut(
    combined_df['sales'],
    bins=sales_bins,
    labels=sales_labels,
    right=False,
    include_lowest=True  # 包含0值
)

# 处理可能的空区间（1.0.2版本对空标签敏感）
combined_df = combined_df.dropna(subset=['sales_range'])


# ----------------------
# 6. 特征编码
# ----------------------
# 品牌编码（确保训练集中的品牌覆盖预测场景）
brand_encoder = LabelEncoder()
combined_df['brand_encoded'] = brand_encoder.fit_transform(combined_df['brand'])

# 目标变量编码
target_encoder = LabelEncoder()
combined_df['sales_range_encoded'] = target_encoder.fit_transform(combined_df['sales_range'])


# ----------------------
# 7. 划分训练集和测试集
# ----------------------
X = combined_df[['price', 'brand_encoded', 'GoodRate', 'AverageScore']]  # 明确特征列
y = combined_df['sales_range_encoded']

# 分层抽样（兼容1.0.2版本的stratify参数）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique()) > 1 else None
)


# ----------------------
# 8. 训练模型（适配1.0.2版本）
# ----------------------
# 1.0.2版本兼容的参数设置
rf_model = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    min_samples_split=10,
    n_jobs=-1,  # 利用所有CPU核心加速（1.0.2支持）
    random_state=42,
    bootstrap=True  # 确保与版本默认行为一致
)
rf_model.fit(X_train, y_train)


# ----------------------
# 9. 评估模型
# ----------------------
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"模型准确率：{accuracy:.4f}")
print(f"测试集预测分布：{pd.Series(y_pred).value_counts().to_dict()}")


# ----------------------
# 10. 保存模型（覆盖原文件）
# ----------------------
# 建议使用绝对路径，与预测代码保持一致
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
model_path = os.path.join(BASE_DIR, 'rf_sales_prediction_model.joblib')
brand_encoder_path = os.path.join(BASE_DIR, 'brand_encoder.joblib')
target_encoder_path = os.path.join(BASE_DIR, 'target_encoder.joblib')

dump(rf_model, model_path)
dump(brand_encoder, brand_encoder_path)
dump(target_encoder, target_encoder_path)

print(f"模型已保存至：{model_path}")
print(f"品牌编码器已保存至：{brand_encoder_path}")