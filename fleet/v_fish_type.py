from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import FishType


class FishTypeListView(ListView):
    model = FishType
    template_name = "fleet/fish_type/list.html"
    context_object_name = "fish_types"
    paginate_by = 10  # Pagination


class FishTypeDetailView(DetailView):
    model = FishType
    template_name = "fleet/fish_type/detail.html"
    context_object_name = "fish_type"


class FishTypeCreateView(CreateView):
    model = FishType
    template_name = "fleet/fish_type/create.html"
    fields = ['name']
    success_url = reverse_lazy('fleet:fish-type-list')


class FishTypeUpdateView(UpdateView):
    model = FishType
    template_name = "fleet/fish_type/edit.html"
    fields = ["name"]
    success_url = reverse_lazy('fleet:fish-type-list')
    context_object_name = "fish_type"


class FishTypeDeleteView(DeleteView):
    model = FishType
    template_name = "fleet/generic/delete.html"
    success_url = reverse_lazy('fleet:fish-type-list')
