from django.db import models
from django.contrib.auth.models import User
import datetime, threading
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from tech_preview.settings import DEFAULT_FROM_EMAIL, EMAIL_HOST_DOMAIN


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

    def save(self, *args, **kwargs):
        # При добавлении поста в ленту — подписчики получают почтовое уведомление со ссылкой на новый пост.
        super(BlogEntity, self).save(*args, **kwargs)
        # @start_new_thread чтобы не зависало при отправке
        thread = threading.Thread(target=self.send_email_notification)
        thread.daemon = True
        thread.start()

    def send_email_notification(self):
        
        # отправить этим ребятам почту
        email_list = []

        for item in BlogSubscribedBy.objects.all():
            try:
                item.subscribed_by.get(username=self.author)
                email_list.append(item.user.username)
            except ObjectDoesNotExist:
                pass

        # рассылка почты работать не будет, пока не исправить нужные параметры SETTINGS.EMAIL*
        subject = "Почтовое уведомление со ссылкой на новый пост"
        html_content = f"{self.author} разместил новую запись в блоге. <br> \
            <a href='{EMAIL_HOST_DOMAIN}/detail/{self.id}'>Ссылка на пост</a>"
        msg = EmailMessage(subject, html_content, DEFAULT_FROM_EMAIL, email_list)
        msg.content_subtype = "html"
        msg.send()
        

# Эти свойства лучше заворачивать в объект auth.models.User создавать пустые записи при save(), но не умею
class BlogSubscribedBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed_by = models.ManyToManyField(User, related_name='sub')

class BlogReadBy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_by = models.ManyToManyField(BlogEntity, related_name='read')
