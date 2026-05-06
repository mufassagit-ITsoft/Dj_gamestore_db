from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=250, unique=True)

    class Meta:
        verbose_name_plural = 'topics'

    def __str__(self):
        return self.name


class Category(models.Model):
    topic = models.ForeignKey(
        Topic, related_name='categories',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=250, db_index=True)
    slug = models.SlugField(max_length=250, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='product',
        on_delete=models.CASCADE, null=True
    )
    title = models.CharField(max_length=250)
    brand = models.CharField(max_length=250, default='un-branded')
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    image = models.CharField(max_length=500, blank=True)  # stores Cloudinary URL
    date_uploaded = models.DateTimeField(auto_now_add=True)
    quantity_available = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    total_price_sold = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_sold_date = models.DateTimeField(null=True, blank=True)
    payment_successful = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'products'

    def __str__(self):
        return self.title


class Order(models.Model):
    full_name = models.CharField(max_length=300)
    email = models.EmailField(max_length=255)
    shipping_address = models.TextField(max_length=10000)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Order - #{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Order Item - #{self.id}'


class RewardAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reward_account')
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lifetime_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ${self.total_points}"


class RewardTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_transactions')
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    points_earned = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ${self.points_earned}"
