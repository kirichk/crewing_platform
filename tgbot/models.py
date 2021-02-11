from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID пользователя',
        unique=True,
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
        blank=True,
        null=True
    )
    phone = models.TextField(
        verbose_name='Номер телефона',
        blank=True,
        null=True
    )
    full_name = models.TextField(
        verbose_name='Полное имя',
        blank=True,
        null=True
    )
    title_subscriptions = models.TextField(
        verbose_name='Подписки на должности',
        blank=True,
        null=True
    )
    fleet_subscriptions = models.TextField(
        verbose_name='Подписки на флот',
        blank=True,
        null=True
    )
    salary_subscription = models.TextField(
        verbose_name='Промежуток зарплат',
        blank=True,
        null=True
    )
    contract_subscription = models.TextField(
        verbose_name='Длительность контракта',
        blank=True,
        null=True
    )
    crew_subscription = models.TextField(
        verbose_name='Экипаж',
        blank=True,
        null=True
    )
    date_ready = models.TextField(
        verbose_name='Дата готовности',
        blank=True,
        null=True
    )
    email = models.TextField(
        verbose_name='Email',
        blank=True,
        null=True
    )
    subscription = models.BooleanField(
        verbose_name='Подписка на рассылку',
        default=False,
        null=True
    )

    def __str__(self):
        return f'#{self.external_id} {self.name}'
