from django.db import models


class ProductInfo(models.Model):
    platform = models.CharField(max_length=100, verbose_name='商品所属平台')
    city = models.CharField(max_length=255, verbose_name='商品上架平台所属城市')
    platform_product_id = models.CharField(max_length=255, verbose_name='平台产品id')
    collect_time = models.DateTimeField(null=True, blank=True, verbose_name='采集时间')
    product_url = models.TextField(null=True, blank=True, verbose_name='产品链接')
    category_list = models.CharField(max_length=255, null=True, blank=True, verbose_name='榜单类别')
    ranking = models.IntegerField(null=True, blank=True, verbose_name='排名')
    mpn = models.CharField(max_length=255, null=True, blank=True, verbose_name='制造商部件编号')
    ean = models.CharField(max_length=255, null=True, blank=True, verbose_name='欧洲商品编号')
    sku = models.CharField(max_length=255, null=True, blank=True, verbose_name='库存量单位')
    product_image = models.TextField(null=True, blank=True, verbose_name='产品首图图片')
    title = models.TextField(null=True, blank=True, verbose_name='产品标题')
    desc = models.TextField(null=True, blank=True, verbose_name='产品描述')
    block_diagram = models.TextField(null=True, blank=True, verbose_name='方块图')
    color_block_diagram = models.TextField(null=True, blank=True, verbose_name='色块图')
    image_1 = models.TextField(null=True, blank=True, verbose_name='图一')
    image_2 = models.TextField(null=True, blank=True, verbose_name='图二')
    image_3 = models.TextField(null=True, blank=True, verbose_name='图三')
    image_4 = models.TextField(null=True, blank=True, verbose_name='图四')
    image_5 = models.TextField(null=True, blank=True, verbose_name='图五')
    image_6 = models.TextField(null=True, blank=True, verbose_name='图六')
    image_7 = models.TextField(null=True, blank=True, verbose_name='图七')
    image_8 = models.TextField(null=True, blank=True, verbose_name='图八')
    image_9 = models.TextField(null=True, blank=True, verbose_name='图九')
    image_10 = models.TextField(null=True, blank=True, verbose_name='图十')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='产品价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name='产品原价')
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='折扣')
    freight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='运费')
    currency = models.CharField(max_length=100, null=True, blank=True, verbose_name='货币种类')
    color = models.CharField(max_length=255, null=True, blank=True, verbose_name='产品颜色')
    size = models.CharField(max_length=255, null=True, blank=True, verbose_name='产品尺寸')
    level_1_classify = models.CharField(max_length=255, null=True, blank=True, verbose_name='一级类目')
    level_2_classify = models.CharField(max_length=255, null=True, blank=True, verbose_name='二级类目')
    level_3_classify = models.CharField(max_length=255, null=True, blank=True, verbose_name='三级类目')
    level_4_classify = models.CharField(max_length=255, null=True, blank=True, verbose_name='末级类目')
    type_of_sale = models.CharField(max_length=255, null=True, blank=True, verbose_name='售卖类型（全托/半托）')
    release_time = models.DateTimeField(null=True, blank=True, verbose_name='上架时间')
    sales = models.IntegerField(null=True, blank=True, verbose_name='销量')
    comment_num = models.IntegerField(null=True, blank=True, verbose_name='评论数')
    grade = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='评分')
    brand = models.CharField(max_length=255, null=True, blank=True, verbose_name='品牌')
    remark = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    create_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='创建者')
    update_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')
    update_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='更新者')
    del_flag = models.BooleanField(default=False, verbose_name='是否已删除')

    class Meta:
        db_table = 'product_info'
        verbose_name = '产品信息'
        verbose_name_plural = '产品信息集合'
        indexes = [
            models.Index(fields=['platform', 'city'], name='platform_city_idx'),
            models.Index(fields=['platform_product_id'], name='platform_product_id_idx'),
        ]

    def __str__(self):
        return f"{self.title} ({self.platform_product_id})"
