from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __repr__(self):
        return f"{self.name} - {self.description}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name='items')
