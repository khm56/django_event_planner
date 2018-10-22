from django.contrib import admin
from .models import Concert, AttendConcert

admin.site.register(Concert)
admin.site.register(AttendConcert)