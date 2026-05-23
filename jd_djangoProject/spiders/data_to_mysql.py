import numpy as np
import pandas as pd

df = pd.read_csv('result3.csv',index_col=0)
df.dropna(inplace=True)

from sqlalchemy import create_engine
engine = create_engine("mysql://root:root@localhost/django_jd_ksh?charset=utf8mb4")
print(df)

df.columns = ['product_id','product_name','price','shop','brand','img_url','CommentCountStr','AverageScore','GoodCountStr','DefaultGoodCountStr','GoodRate',
              'AfterCountStr','VideoCountStr','PoorCountStr','GeneralCountStr',]
print(df)
df.to_sql('myapp_xinxi',engine,if_exists='append',index_label='id')


df = pd.read_csv('result3.csv',index_col=0)
df2 =  pd.read_csv('comments.csv.csv',names=['name','content'])
df2['product_id'] = None
product_ids = df['商品id']
# 确保product_ids列表足够长
if len(product_ids) >= len(df2):
    # 从product_ids中随机选择len(df2)个值
    random_product_ids = np.random.choice(product_ids, size=len(df2), replace=False)
else:
    # 如果product_ids列表不够长，则重复直到满足长度要求
    random_product_ids = np.tile(product_ids, int(np.ceil(len(df2) / len(product_ids))))[:len(df2)]

# 将随机选取的product_id值赋给df2的'product_id'列
df2['product_id'] = random_product_ids
df2['score'] = 5

df2.reset_index(drop=True, inplace=True)
df2.index += 1  # 确保索引从1开始

# 将生成的随机日期填充到df2的新列中
df2['comment_date'] = '2024-09-26'
print(df2['comment_date'])
df2[['product_id','content','score','comment_date']].to_sql('myapp_comment',engine,if_exists='append',index_label='id')

