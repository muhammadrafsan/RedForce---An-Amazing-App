from django.contrib import admin
from .models import UserInfo,TestUser
# Register your models here.
admin.site.register([
   UserInfo,
   TestUser
])