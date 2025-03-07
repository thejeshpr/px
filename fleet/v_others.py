import logging
from datetime import timedelta
import json
import uuid


from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, BooleanField, Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import FishermanFilterForm, FishermanCreateByJSONForm, BulkCreateForm
from .models import FisherMan, FishType, ShipConfig

# from .custom_warpper import custom_required, custom_required_class_based

logger = logging.getLogger(__name__)


class DataDump(View):
    def get(self, request):
        fish_types = list(FishType.objects.values('name', 'slug'))
        ship_configs = list(ShipConfig.objects.values('key', 'val'))

        fishers = list(FisherMan.objects.values(
            'base_url',
            'fish_type__name',
            'active',
            "additional_data",
            # "is_fishing",
            "last_successful_catch",
            "name",
            "notes",
            "is_dangerous",
            "strategy",
            "slug",
            "store_catching_info"
        ))
        return JsonResponse({
            "fish_types": fish_types,
            "ship_configs": ship_configs,
            "fishers": fishers
        })


class DataBulkCreate(FormView):
    template_name = 'fleet/generic/data_bulk_create.html'
    form_class = BulkCreateForm
    success_url = reverse_lazy('fleet:fisherman-list')

    def form_valid(self, form):
        data = json.loads(form.cleaned_data.get("data"))
        fish_types = dict()

        created_objects = dict(
            fish_types=0,
            fishers=0,
            ship_configs=0
        )
        # create fish_types
        for entry in data['fish_types']:
            logger.debug(f"creating fish_type if not exists: {entry}")
            fish_types[entry['name']], created = FishType.objects.get_or_create(name=entry['name'], slug=entry['slug'])

            if created:
                created_objects["fish_types"] = created_objects["fish_types"] + 1

        # create config-values
        for entry in data['ship_configs']:
            logger.debug(f"creating ship configs if not exists: {entry}")
            _, created = ShipConfig.objects.get_or_create(
                key=entry.get('key'),
                val=entry.get('val'),
            )

            if created:
                created_objects["ship_configs"] = created_objects["ship_configs"] + 1

        # create site_confs
        slug_list = [x['slug'] for x in data['fishers']]
        existing_db_obj = FisherMan.objects.filter(slug__in=slug_list)
        existing_fishers_slug = [fisherman.slug for fisherman in existing_db_obj]

        for entry in data['fishers']:
            logger.debug(f"creating fisherman if not exists")

            if entry['slug'] in existing_fishers_slug:
                continue

            fisherman = FisherMan(
                    base_url=entry.get("base_url"),
                    fish_type=fish_types.get(entry.get('fish_type__name', None), {}),
                    active=entry.get("active"),
                    additional_data=entry.get("additional_data"),
                    is_fishing=False,
                    last_successful_catch=None,
                    name=entry.get("name"),
                    notes=entry.get("notes"),
                    is_dangerous=entry.get("is_dangerous"),
                    strategy=entry.get("strategy"),
                    store_catching_info=entry.get("store_catching_info")
                )
            fisherman.save()
            created_objects["fishers"] = created_objects["fishers"] + 1

        msg = (f'Created - FishTypes:{created_objects["fish_types"]}, '
               f'ShipConfigs:{created_objects["ship_configs"]}, '
               f'Fishers:{created_objects["fishers"]}')
        messages.add_message(self.request, messages.INFO, message=msg)
        return super().form_valid(form)
