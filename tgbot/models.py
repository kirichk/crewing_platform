from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID пользователя',
        unique=True,
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
        blank=True,
    )
    phone = models.TextField(
        verbose_name='Номер телефона',
        blank=True,
    )
    full_name = models.TextField(
        verbose_name='Полное имя',
        blank=True,
    )
    title_subscriptions = models.TextField(
        verbose_name='Подписки на должности',
        blank=True,
    )
    salary_range = models.TextField(
        verbose_name='Промежуток зарплат',
        blank=True,
    )
    def __str__(self):
        return f'#{self.external_id} {self.name}'
