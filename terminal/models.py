import uuid

from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Баланс')

    class Meta:
        verbose_name = 'кошелёк'
        verbose_name_plural = "кошельки"