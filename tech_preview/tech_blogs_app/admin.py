from django.contrib import admin
from tech_blogs_app.models import BlogEntity, BlogReadBy, BlogSubscribedBy


admin.site.register(BlogEntity)
admin.site.register(BlogSubscribedBy)
admin.site.register(BlogReadBy)
