from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.
class BlogEntity(models.Model):
    class Meta:
        ordering = ["-posted_since"]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
    # элементарная запись с заголовком, текстом и временем создания.
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='profile')
    header = models.CharField(max_length=512, verbose_name='Заголовок записи')
    content = models.TextField(verbose_name='Полное содержание записи')
    posted_since = models.DateTimeField(default=datetime.datetime.now(), verbose_name='Дата публикации')

    def __str__(self):
        return f'Статья {self.header} от {self.posted_since}, автор: {self.author}'


# Эти свойства лучше заворачивать в объект Model, но не умею
class BlogSubscribedBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed_by = models.ManyToManyField(User, related_name='sub')


class BlogReadBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_by = models.ManyToManyField(BlogEntity, related_name='read')
