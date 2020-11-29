from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from web_hiring.models import Post
from django.db.models import Q
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse_lazy
from web_hiring.forms import PostForm
from django.views.generic import (TemplateView, ListView,
                                    DetailView,CreateView,
                                    UpdateView,DeleteView,)
from django.conf import settings
from web_hiring.notificators import vacancy_notification
# Create your views here.


class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post
    paginate_by = 30

    def get_queryset(self):
        return Post.objects.filter(publish_date__lte=timezone.now()).order_by('-publish_date')

class SearchResultsView(ListView):
    model = Post
    paginate_by = 30
    template_name = 'post_search.html'

    def get_queryset(self): # новый
        query = self.request.GET.get('q')
        object_list = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query),
            publish_date__lte=timezone.now()).order_by('-publish_date')
        return object_list

class PostDetailView(DetailView):
    model = Post

class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'web_hiring/post_detail.html'
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.salary = form.instance.salary + ' $'
        new_form = form.save(commit=False)
        if new_form.title == "Другое":
            form.instance.title = self.request.POST.get('titlespecify')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'web_hiring/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('web_hiring:post_list')

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'web_hiring/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(publish_date__isnull=True).order_by('create_date')

class PublihedListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'web_hiring/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user,publish_date__isnull=False).order_by('create_date')

##################################################################
##################################################################


@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    form = model_to_dict(Post.objects.get(pk=pk))
    vacancy_notification(form)
    post.publish()
    return redirect('web_hiring:post_detail',pk=pk)
