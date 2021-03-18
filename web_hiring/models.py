from django.db import models
from django.utils import timezone
from django.urls import reverse
from crewing.settings import (TITLE_CHOICES, FLEET_CHOICES,
                                VESSEL_CHOICES, ENGLISH_CHOICES)
import datetime

# Create your models here.


class Post(models.Model):
    author = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    fleet = models.CharField(max_length=200, choices=FLEET_CHOICES)
    vessel = models.CharField(max_length=200, choices=VESSEL_CHOICES)
    salary = models.CharField(max_length=200)
    text = models.TextField(blank=True, null=True)
    joining_date = models.DateField(blank=False)
    voyage_duration = models.CharField(blank=True, null=True, max_length=200)
    sailing_area = models.CharField(blank=True, null=True, max_length=200)
    dwt = models.CharField(max_length=200, blank=True, null=True)
    years_constructed = models.PositiveIntegerField(blank=True, null=True)
    crew = models.CharField(blank=True, null=True, max_length=200)
    crewer = models.CharField(blank=True, null=True, max_length=200)
    contact = models.CharField(blank=True, null=True, max_length=200)
    email = models.CharField(blank=True, null=True, max_length=200)
    english = models.CharField(max_length=200, choices=ENGLISH_CHOICES)
    link = models.CharField(blank=True, null=True, max_length=200)
    create_date = models.DateTimeField(default=timezone.now)
    publish_date = models.DateTimeField(blank=True, null=True)


    def publish(self):
        self.publish_date = timezone.now()
        self.save()


    def get_absolute_url(self):
        return reverse('web_hiring:post_detail', kwargs={'pk': self.pk})


    def __str__(self):
        return self.title


    def __unicode__(self):
        return self.title
