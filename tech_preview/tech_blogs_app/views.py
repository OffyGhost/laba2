from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse, HttpResponse
from django.views.generic.base import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, IntegrityError
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from tech_blogs_app.models import BlogEntity as Post, BlogSubscribedBy as Subs, BlogReadBy as Read
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from tech_blogs_app.forms import CreatePost


# TODO При создании пользователя через админку - у них создается по модели BlogSubscribedBy BlogReadBy
class BlogListSelfView(TemplateView):
    template_name = 'blog.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            User.objects.get(username=self.request.user)
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
        # Пагинацию можно вставить здесь? может ли пагинировать context?
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


# Выдать один пост и все.
class BlogDetailView(TemplateView):

    template_name = 'blogentity.html'

    def get_context_data(self, **kwargs):
        current_user = 1
        context = super().get_context_data(**kwargs)
        context['item'] = get_object_or_404(Post, pk=kwargs['pk'])
        # print(context)
        return context


# TODO Объединить Self и этот по ключу SLUG
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

        # Выдать все записи, где есть подписка
        current_user = User.objects.get(username=self.request.user)
        context = super().get_context_data(**kwargs)
        # Или выдать записи, или будет пустая страничка
        context['all'] = []
        try:
            # Подписка есть -> выдаю ее
            current_query = Subs.objects.get(user=current_user).subscribed_by.all()
            for item in current_query:
                # нельзя использовать метод .append - будет вложенные списки. Вот суммировать списки вот это подходит...
                context['all'] += Post.objects.filter(author=item)
                # print(Post.objects.filter(username=item))
            # У пользователя есть персональная лента новостей, в которой в обратном хронологическом порядке
            # выводятся посты из блогов, на которые он подписан.
            context['all'].sort(key=lambda x: x.posted_since, reverse=True)
            context['other'] = User.objects.filter(~Q(id=current_user.id))
        except ObjectDoesNotExist:
            # TODO Предложить подписаться на случайного пользоватля
            context['other'] = User.objects.filter(~Q(id=current_user.id))
        # print(context)
        return context

    # Подписка\отписка прямо в новостной лист? Этой сущности здесь не место же
    def post(self, *args, **kwargs):
        current_user = User.objects.get(username=self.request.user)

        # Отписка\подписка
        try:
            self.request.POST['subscribe']
            target_user = User.objects.get(id=self.request.POST['id'])
            # Отписываюсь от...
            if str(self.request.POST['subscribe']) == 'false':
                Subs.objects.get(user=current_user).subscribed_by.remove(target_user)
                # сбросить метки о прочтенности
                try:
                    Read.objects.get(user=current_user).delete()
                except ObjectDoesNotExist:
                    # Не было отметок о прочтении
                    pass

                return HttpResponse(f'{current_user} отписывается от {target_user}')
            # Подписываюсь на...
            if str(self.request.POST['subscribe']) == 'true':
                # Subs.objects.create и Read.objects.create делается при создании пользователя
                try:
                    Subs.objects.get(user=current_user)
                except ObjectDoesNotExist:
                    Subs.objects.create(user=current_user)

                Subs.objects.get(user=current_user).subscribed_by.add(target_user)
                return HttpResponse(f'{current_user} подписывается на {target_user}')
        # except django.utils.datastructures.MultiValueDictKeyError
        except KeyError:
            pass

        # Отмечаю пост как прочитанный
        try:
            if str(self.request.POST['read']):
                post_id = self.request.POST['post_id']
                Read.objects.get_or_create(user=current_user)
                try:
                    Read.objects.get(user=current_user).read_by.add(post_id)
                except IntegrityError:
                    # Статья уже отмечена
                    pass
                return HttpResponse(f' {current_user} пометил запись {post_id} как прочитанную')
        except KeyError:
            pass

        return HttpResponseRedirect('/')


def get_read(request):
    current_user = User.objects.get(username=request.user)
    try:
        if request.GET['get_read']:
            # ID, где посты уже прочтенные. Лучше делать такие вещи через JSON -> Jquery или подобное
            Read.objects.get_or_create(user=current_user)
            data = list(Read.objects.get(user=current_user).read_by.all().values('id'))
            return JsonResponse({'read': data})
    except KeyError:
        pass
