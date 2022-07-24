from .tools import rich_media_consctructor
from django.conf import settings


TITLE_MEDIA = rich_media_consctructor(settings.TITLE_CHOICES, 'title')
SALARY_MEDIA = rich_media_consctructor(settings.SALARY_MATCHES, 'salary')
