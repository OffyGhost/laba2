# Generated by Django 2.1 on 2019-03-27 04:15

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tech_blogs_app', '0006_auto_20190326_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogReadBy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='blogentity',
            name='posted_since',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 27, 11, 15, 13, 626276), verbose_name='Дата публикации'),
        ),
        migrations.AddField(
            model_name='blogreadby',
            name='read_by',
            field=models.ManyToManyField(related_name='read', to='tech_blogs_app.BlogEntity'),
        ),
        migrations.AddField(
            model_name='blogreadby',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
