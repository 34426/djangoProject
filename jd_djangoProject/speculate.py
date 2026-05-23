from joblib import load
import pandas as pd
import os

def Speculate(data):
    try:
        # 直接写死模型的绝对路径（根据你的实际路径修改）
        model_path = r"D:\Apyproject\Python京东手机数据分析可视化系统\jd_djangoProject\rf_sales_prediction_model.joblib"
        brand_encoder_path = r"D:\Apyproject\Python京东手机数据分析可视化系统\jd_djangoProject\jd_djangoProject\brand_encoder.joblib"
        target_encoder_path = r"D:\Apyproject\Python京东手机数据分析可视化系统\jd_djangoProject\target_encoder.joblib"

        # 加载模型和编码器
        rf_model = load(model_path)
        brand_encoder = load(brand_encoder_path)
        target_encoder = load(target_encoder_path)

        # 构造特征（列名与训练时一致）
        price, brand, rating, average_score = data
        new_data = pd.DataFrame({
            "price": [float(price)],
            "brand_encoded": [0],
            "GoodRate": [float(rating)],
            "AverageScore": [float(average_score)]
        })

        # 品牌编码
        if brand in brand_encoder.classes_:
            new_data["brand_encoded"] = brand_encoder.transform([brand])[0]
        else:
            new_data["brand_encoded"] = 0  # 未知品牌默认值

        # 预测
        prediction = rf_model.predict(new_data)
        predicted_sales_range = target_encoder.inverse_transform(prediction)
        return predicted_sales_range[0]

    except Exception as e:
        print(f"预测过程中出现错误: {str(e)}")
        return "低销量"