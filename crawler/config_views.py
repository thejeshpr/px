from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import ConfigValues


class ConfigValuesListView(ListView):
    model = ConfigValues
    template_name = "crawler/config_values/list.html"
    context_object_name = "config_values"
    paginate_by = 10  # Pagination


class ConfigValuesDetailView(DetailView):
    model = ConfigValues
    template_name = "crawler/config_values/detail.html"
    context_object_name = "config_value"


class ConfigValuesCreateView(CreateView):
    model = ConfigValues
    template_name = "crawler/config_values/create.html"
    fields = ['key', 'val']
    success_url = reverse_lazy('crawler:config-values-list')


class ConfigValuesUpdateView(UpdateView):
    model = ConfigValues
    template_name = "crawler/config_values/edit.html"
    fields = ["key", "val"]
    success_url = reverse_lazy('crawler:config-values-list')
    context_object_name = "config_value"


class ConfigValuesDeleteView(DeleteView):
    model = ConfigValues
    template_name = "crawler/generic/delete.html"
    success_url = reverse_lazy('crawler:config-values-list')
