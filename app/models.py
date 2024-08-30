from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser




class CustomUser(AbstractUser):
    user_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)
    invited_friends = models.IntegerField(default=0)
    invited_friends_usernames = models.TextField(default='[]')
    coins = models.IntegerField(default=0)
    amount = models.IntegerField(default=0) 

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

    def __str__(self):
        return self.username



class Task(models.Model):
    title = models.CharField(max_length=255)
    points = models.IntegerField()
    button_link = models.URLField()

    def __str__(self):
        return self.title


class User(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    invited_friends = models.IntegerField(default=0)
    invited_friends_usernames = models.TextField(default='[]')
    coins = models.IntegerField(default=0) 

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    coins = models.IntegerField(default=0)
    
    
class Friend(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(CustomUser, related_name='friends', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)