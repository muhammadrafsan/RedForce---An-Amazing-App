from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserInfo(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True, unique=True)
    img= models.TextField(unique=True,null=False)
    key =models.CharField(max_length=100, null=True)
    
class TestUser(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    img= models.TextField(unique=True,null=False)