from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Category


class CategoryListView(ListView):
    model = Category
    template_name = "crawler/category/list.html"
    context_object_name = "categories"
    paginate_by = 10  # Pagination


class CategoryDetailView(DetailView):
    model = Category
    template_name = "crawler/category/detail.html"
    context_object_name = "category"


class CategoryCreateView(CreateView):
    model = Category
    template_name = "crawler/category/create.html"
    fields = ['name']
    success_url = reverse_lazy('crawler:category-list')


class CategoryUpdateView(UpdateView):
    model = Category
    template_name = "crawler/category/edit.html"
    fields = ["name"]
    success_url = reverse_lazy('crawler:category-list')
    context_object_name = "category"


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "crawler/category/delete.html"
    success_url = reverse_lazy('crawler:category-list')
