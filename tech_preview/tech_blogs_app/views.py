from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.views.generic.base import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from tech_blogs_app.models import BlogEntity as Post, BlogSubscribedBy as Subs
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from tech_blogs_app.forms import CreatePost


class BlogListSelfView(TemplateView):

    template_name = 'blog.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            current_user = User.objects.get(username=self.request.user)
        except ObjectDoesNotExist:
            return redirect('/login/')

        return super(BlogListSelfView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        current_user = User.objects.get(username=self.request.user)
        context = super().get_context_data(**kwargs)
        # Автор самого блога
        context['author'] = current_user
        context['all'] = Post.objects.filter(author=current_user)
        context['form'] = CreatePost
        # Пагинацию можно вставить здесь
        return context

    # Пользователь создает запись
    def post(self, *args, **kwargs):
        self.form = CreatePost(self.request.POST)
        if self.form.is_valid():
            # TODO переделать на сохранение через форму
            # current_user = self.request.user
            current_user = User.objects.get(username=self.request.user)
            Post.objects.create(author=current_user, header=self.request.POST['header'],
                                content=self.request.POST['content'])

            return HttpResponseRedirect('/')


# Нужен ли этот класс вообще?
class BlogDetailView(TemplateView):

    template_name = 'blogentity.html'

    def get_context_data(self, **kwargs):
        current_user = 1
        context = super().get_context_data(**kwargs)
        context['item'] = get_object_or_404(Post, pk=kwargs['pk'])
        # Пагинацию можно вставить здесь
        # print(context)
        return context


# Объединить Self и этот по ключу SLUG
class BlogListView(TemplateView):

    template_name = 'blog.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        target_user = User.objects.get(username=kwargs['slug'])
        # current - текущий пользователь, "вы", а target - этот тот, к кому вы зашли на страницу
        current_user = User.objects.get(username=self.request.user)
        context['author'] = target_user
        # Проверяю - подписан ли пользователь на целевого или нет
        try:
            Subs.objects.get(user=current_user.id).subscribed_by.get(id=target_user.id)
            context['subscribed'] = True
        except ObjectDoesNotExist:
            context['subscribed'] = False
        context['all'] = Post.objects.filter(author=target_user)
        # Пагинацию можно вставить здесь
        # print(context)
        return context


class NewsListView(TemplateView):

    template_name = 'blog.html'

    def get_context_data(self, **kwargs):

        # Выдать все записи, где есть
        current_user = User.objects.get(username=self.request.user)
        context = super().get_context_data(**kwargs)
        # Или выдать записи, или будет пустая страничка
        context['all'] = []
        try:
            # Подписка есть -> выдаю ее
            current_query = Subs.objects.get(user=current_user).subscribed_by.all()
            for item in current_query :
                # нельзя использовать метод .append - будет вложенные списки. Вот суммировать списки вот это подходит...
                context['all'] += Post.objects.filter(author=item)
                # print(Post.objects.filter(username=item))
            # У пользователя есть персональная лента новостей, в которой в обратном хронологическом порядке
            # выводятся посты из блогов, на которые он подписан.
            context['all'].sort(key=lambda x: x.posted_since, reverse=True)
        except ObjectDoesNotExist:
            # TODO Предложить подписаться на случайного пользоватля
            pass
        # print(context)
        return context

    # Подписка\отписка прямо в новостной лист? Этой сущности здесь не место же
    def post(self, *args, **kwargs):
        # Подписываюсь на...
        print(self.request.POST)
        if self.request.POST['to_sub_true']:
            pass
        # Отписываюсь от...
        if self.request.POST['to_sub_true']:
            pass
        return HttpResponseRedirect('/')
