from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import SiteConf


class SiteConfListView(ListView):
    model = SiteConf
    template_name = "crawler/siteconf/list.html"
    context_object_name = "siteconfs"
    paginate_by = 10  # Pagination


class SiteConfDetailView(DetailView):
    model = SiteConf
    template_name = "crawler/siteconf/detail.html"
    context_object_name = "siteconf"


class SiteConfCreateView(CreateView):
    model = SiteConf
    template_name = "crawler/siteconf/create.html"
    fields = ['base_url', 'category', 'enabled', 'extra_data_json', 'icon', 'is_locked', 'name', 'notes', 'ns_flag', 'scraper_name']
    success_url = reverse_lazy('siteconf-list')


class SiteConfUpdateView(UpdateView):
    model = SiteConf
    template_name = "crawler/siteconf/edit.html"
    fields = ['base_url', 'category', 'enabled', 'extra_data_json', 'icon', 'is_locked', 'name', 'notes', 'ns_flag', 'scraper_name']
    success_url = reverse_lazy('siteconf-list')


class SiteConfDeleteView(DeleteView):
    model = SiteConf
    template_name = "crawler/siteconf/delete.html"
    success_url = reverse_lazy('siteconf-list')
