from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import ShipConfig


class ShipConfigListView(ListView):
    model = ShipConfig
    template_name = "fleet/ship_config/list.html"
    context_object_name = "ship_configs"
    paginate_by = 10  # Pagination


class ShipConfigDetailView(DetailView):
    model = ShipConfig
    template_name = "fleet/ship_config/detail.html"
    context_object_name = "ship_config"


class ShipConfigCreateView(CreateView):
    model = ShipConfig
    template_name = "fleet/ship_config/create.html"
    fields = ['key', 'val']
    success_url = reverse_lazy('fleet:ship-config-list')


class ShipConfigUpdateView(UpdateView):
    model = ShipConfig
    template_name = "fleet/ship_config/edit.html"
    fields = ["key", "val"]
    success_url = reverse_lazy('fleet:ship-config-list')
    context_object_name = "ship_config"


class ShipConfigDeleteView(DeleteView):
    model = ShipConfig
    template_name = "fleet/generic/delete.html"
    success_url = reverse_lazy('fleet:ship-config-list')
