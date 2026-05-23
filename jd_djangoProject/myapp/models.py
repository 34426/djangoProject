from django.db import models

# Create your models here.
class User(models.Model):
    # 登录账号
    username = models.CharField(max_length=50, verbose_name='登录账号')
    # 密码
    password = models.CharField(max_length=255, verbose_name='密码')
    # 昵称
    nickname = models.CharField(max_length=50,  verbose_name='昵称')
    # 邮箱
    email = models.EmailField(max_length=100, unique=True, verbose_name='邮箱')
    # 电话
    phone = models.CharField(max_length=15,  verbose_name='电话')
    # 地址
    address = models.CharField(max_length=255, verbose_name='地址')
    # 用户类型
    user_type = models.CharField(max_length=20, choices=[('normal', '普通用户'), ('admin', '管理员')], default='normal',
                                 verbose_name='用户类型')
    # 头像
    avatar = models.ImageField(upload_to='avatars/', null=True, verbose_name='头像')
    # 注册时间
    addtime = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = verbose_name_plural = "用户表"


class XinXi(models.Model):
    id = models.BigIntegerField(primary_key=True)
    product_id = models.CharField(verbose_name='商品id',default='',max_length=255)
    product_name = models.CharField(verbose_name='商品名',max_length=255)
    price = models.CharField(verbose_name='价格',default='',max_length=255)
    shop = models.CharField(verbose_name='店铺',default='',max_length=255)
    brand = models.CharField(verbose_name='品牌',default='',max_length=255)
    img_url = models.CharField(verbose_name='图片',default='',max_length=255)
    CommentCountStr = models.IntegerField(verbose_name='总评数',default=0)
    AverageScore = models.CharField(verbose_name='平均得分',default='',max_length=255)
    GoodCountStr = models.CharField(verbose_name='好评数',default='',max_length=255)
    DefaultGoodCountStr = models.CharField(verbose_name='默认好评',default='',max_length=255)
    GoodRate = models.CharField(verbose_name='好评率',default='',max_length=255)
    AfterCountStr = models.CharField(verbose_name='追评数',default='',max_length=255)
    VideoCountStr = models.CharField(verbose_name='视频晒单数',default='',max_length=255)
    PoorCountStr = models.CharField(verbose_name='差评数',default='',max_length=255)
    GeneralCountStr = models.CharField(verbose_name='中评数',default='',max_length=255)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "商品信息表"
        verbose_name_plural = verbose_name

class Comment(models.Model):
    # 主键 id，默认情况下Django会自动添加一个AutoField类型的主键id
    id = models.AutoField(primary_key=True)
    # 产品ID，可以假设为外键关联到Product模型
    product_id = models.CharField(verbose_name='商品id',default='',max_length=255)
    # 评论内容
    content = models.TextField(verbose_name='评论内容')
    score = models.IntegerField(verbose_name='评分')
    # 评论日期
    comment_date = models.DateTimeField(verbose_name='评论日期',auto_now_add=True)  # 自动记录创建时间

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '商品评论表'
        verbose_name_plural = verbose_name
        ordering = ['-comment_date']



# 注意：这个类要和 User、XinXi、Comment 同级，缩进一致
class PhoneProduct(models.Model):
    # 与 XinXi 模型字段名、类型完全一致，仅保留 unique=True 确保商品ID不重复
    id = models.BigIntegerField(primary_key=True)
    product_id = models.CharField(verbose_name='商品id', default='', max_length=255)
    product_name = models.CharField(verbose_name='商品名', max_length=255)
    price = models.CharField(verbose_name='价格', default='', max_length=255)
    shop = models.CharField(verbose_name='店铺', default='', max_length=255)
    brand = models.CharField(verbose_name='品牌', default='', max_length=255)
    img_url = models.CharField(verbose_name='图片', default='', max_length=255)
    sales = models.IntegerField(verbose_name='月销量', default=0)  # 保留销售量字段
    CommentCountStr = models.IntegerField(verbose_name='总评数', default=0)
    AverageScore = models.CharField(verbose_name='平均得分', default='', max_length=255)
    GoodCountStr = models.CharField(verbose_name='好评数', default='', max_length=255)
    DefaultGoodCountStr = models.CharField(verbose_name='默认好评', default='', max_length=255)
    GoodRate = models.CharField(verbose_name='好评率', default='', max_length=255)
    AfterCountStr = models.CharField(verbose_name='追评数', default='', max_length=255)
    VideoCountStr = models.CharField(verbose_name='视频晒单数', default='', max_length=255)
    PoorCountStr = models.CharField(verbose_name='差评数', default='', max_length=255)
    GeneralCountStr = models.CharField(verbose_name='中评数', default='', max_length=255)


    class Meta:
        verbose_name = "手机商品"
        verbose_name_plural = "手机商品"
        db_table = "simulated_phone_products"  # 数据库表名（可根据需要修改，或保持不变）
