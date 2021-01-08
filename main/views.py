from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView

from main.forms import PostForm, ImageForm
from main.models import *
from main.permissions import UserHasPermissionMixin

# def index(request):
#     posts= Post.objects.all()
#     return render(request, 'index.html')



class MainPageView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_template_names(self):
        template_name = super(MainPageView, self).get_template_names()
        search = self.request.GET.get('q')
        if search:
            ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5, formset=BaseImageFormSet)
            template_name = 'search.html'
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            context['posts'] = Post.objects.filter(Q(title__icontains=search)|Q(description__icontains=search))
        elif filter:
            start_date = timezone.now() - timedelta(days=1)
            context['posts'] = Post.objects.filter(created__gte=start_date)
        else:
            context['posts'] = Post.objects.all()
        return context

# def category_detail(request, slug):
#     category = Category.objects.get(slug=slug)
#     posts = Post.objects.filter(category_id=slug)
#     return render(request, 'category-detail.html', locals())

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category-detail.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.slug = kwargs.get('slug', None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(category_id=self.slug)
        return context

# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     image = post.get_image
#     images = post.images.exclude(id=image.id)
#     return render(request, 'post-detail.html', locals())

class PostDetailView(DetailView):
    model = Post
    template_name = 'post-detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object().get_image
        if isinstance(image, type(Image)):
            context['images'] = self.get_object().images.exclude(id=image.id)
        return context



@login_required(login_url='login')



def add_post(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=1)
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if post_form.is_valid() and formset.is_valid():
            post = post_form.save()

            for form in formset.cleaned_data:
                image = form['image']
                Image.objects.create(image=image, post=post)
            return redirect(post.get_absolute_url())
    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())
    return render(request, 'add-post.html', locals())


def update_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.user == post.user:
        ImageFormSet = modelformset_factory(Image,form=ImageForm, max_num=1)
        post_form= PostFormForm(request.POST or None, instance=post)
        formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.filter(post=post))
        if post_form.is_valid() and formset.is_valid():
           post = post_form.save()

        for form in formset:
            image = form.save(commit=False)
            image.post = post
            image.save()
        return redirect(post.get_absolute_url())
        return render(request, 'update-post.html', locals())
    else:
        return HttpResponse('<h1>403 Forbidden<h/1>')


# def delete_post(request,pk):
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == "POST":
#         post.delete()
#         messages.add_message(request,messages.SUCCESS, 'Your post is uccessfully deleted!')
#         return redirect('home')
#     return render(request, 'delete-post.html')

class DeleteRecipeView(UserHasPermissionMixin, DeleteView):
    model = Post
    template_name = 'delete-post.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.SUCCESS, 'Your post is deleted!!!')
        return HttpResponseRedirect(success_url)
