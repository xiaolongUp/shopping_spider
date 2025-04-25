from django.db import models


class ProductInfo(models.Model):
    platform = models.CharField(max_length=100, verbose_name='商品所属平台')
    city = models.CharField(max_length=255, verbose_name='商品上架平台所属城市')
    platform_product_id = models.CharField(max_length=255, verbose_name='平台产品id')
    product_image = models.TextField(null=True, blank=True, verbose_name='产品图片')
    title = models.TextField(null=True, blank=True, verbose_name='产品标题')
    desc = models.TextField(null=True, blank=True, verbose_name='产品描述')
    brand = models.CharField(max_length=255, null=True, blank=True, verbose_name='产品生产厂家')
    color = models.CharField(max_length=255, null=True, blank=True, verbose_name='产品颜色')
    size = models.CharField(max_length=255, null=True, blank=True, verbose_name='产品尺寸')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='产品价格')
    currency = models.CharField(max_length=100, null=True, blank=True, verbose_name='货币种类')
    estimate_num = models.IntegerField(null=True, blank=True, verbose_name='产品评价数')
    multi = models.BooleanField(null=True, blank=True, verbose_name='是否多变体')
    remark = models.CharField(max_length=255, null=True, blank=True, verbose_name='备注')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    create_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='创建者')
    update_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')
    update_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='更新者')
    del_flag = models.BooleanField(verbose_name='是否已删除')

    class Meta:
        db_table = 'product_info'
        verbose_name = '产品信息'
        verbose_name_plural = '产品信息'
        indexes = [
            models.Index(fields=['platform', 'city']),
            models.Index(fields=['platform_product_id']),
        ]

    def __str__(self):
        return f"{self.platform_product_id} - {self.title}"
