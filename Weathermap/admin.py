from django.contrib import admin
from django_pyowm.models import Weather

admin.site.register([Weather, ])
