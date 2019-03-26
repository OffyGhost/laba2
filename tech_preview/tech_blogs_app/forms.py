from django.forms import ModelForm
from tech_blogs_app.models import BlogEntity as Post


class CreatePost(ModelForm):
    class Meta:
        model = Post
        fields = ('header', 'content')
