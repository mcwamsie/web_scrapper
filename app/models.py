from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Shop Name")
    logo = models.ImageField(upload_to="shops", verbose_name="Logo")
    website = models.URLField(verbose_name="Website")
    location = models.TextField(max_length=2000, verbose_name="Location", null=True, blank=True)
    description = models.TextField(max_length=2000, verbose_name="Description")

    searchQuery = models.CharField(max_length=255, verbose_name="Search Query Format", null=True, blank=True)
    featuredProductSelector = models.CharField(max_length=255, verbose_name="Featured Product Selector", null=True,
                                               blank=True)
    productSelector = models.CharField(max_length=255, verbose_name="Product Selector", null=True, blank=True)
    imageSelector = models.CharField(max_length=255, verbose_name="Image Selector")
    nameSelector = models.CharField(max_length=255, verbose_name="Name Selector")
    priceSelector = models.CharField(max_length=255, verbose_name="Price selector")
    linkSelector = models.CharField(max_length=255, verbose_name="Link selector")

    priceOffset = models.IntegerField(verbose_name="Price Offset Index")
    '''
    oldPriceSelector = models.CharField(max_length=255, null=True, blank=True, verbose_name="Old Price selector")
    oldPriceOffset = models.IntegerField(verbose_name="Old Price Offset Index")
    singleImageSelector = models.CharField(max_length=255, verbose_name="Single Image Selector")
    singleNameSelector = models.CharField(max_length=255, verbose_name="Single Name Selector")
    singlePriceSelector = models.CharField(max_length=255, verbose_name="Single Price selector")
    singleOldPriceSelector = models.CharField(max_length=255, null=True, blank=True, verbose_name="Single Price selector")
    singlePriceOffset = models.IntegerField(verbose_name="Single Price Offset Index")
    singleOldPriceOffset = models.IntegerField(verbose_name="Single Old Price Offset Index")

    specificationKeySelector = models.CharField(max_length=255, null=True, blank=True, verbose_name="Price selector")
    specificationValueSelector = models.CharField(max_length=255, null=True, blank=True, verbose_name="Price selector")

    '''

    currency = models.CharField(max_length=255, verbose_name="Currency Code")
    status = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'shop'
        verbose_name_plural = 'shops'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Category Name")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name="Shop")
    searchQuery = models.CharField(max_length=255, verbose_name="Search Query Format", null=True, blank=True)
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        verbose_name="Parent",
        related_name='parent',
        related_query_name='parent',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class ProductInterest(models.Model):
    link = models.URLField(max_length=2000)
    image = models.URLField(max_length=2000)
    name = models.CharField(max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ": " + self.shop.name

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'


class ProductCompare(models.Model):
    link = models.URLField(max_length=2000)
    image = models.URLField(max_length=2000)
    name = models.CharField(max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ": " + self.shop.name

    class Meta:
        verbose_name = 'Compare Product'
        verbose_name_plural = 'Compare Products'


class FavouriteProduct(models.Model):
    link = models.URLField(max_length=2000)
    image = models.URLField(max_length=2000)
    name = models.CharField(max_length=2000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ": " + self.shop.name

    class Meta:
        verbose_name = 'Favourite Product'
        verbose_name_plural = 'Favourite Products'
