import logging
import os
from datetime import timedelta
import json
import uuid
import random


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
# from .job_views import InvokeBackend
from .models import FisherMan, FishType, ShipConfig
from .other_libs import show_dangerous_fish
# from .custom_warpper import custom_required, custom_required_class_based

logger = logging.getLogger(__name__)


# @method_decorator(login_required(login_url='/login/'), name='dispatch')
# @custom_required_class_based
class FishermanListView(ListView):
    model = FisherMan
    template_name = "fleet/fisherman/list.html"
    context_object_name = "fishers"
    paginate_by = 20

    def get_queryset(self):
        ten_days_ago = timezone.now() - timedelta(days=10)
        self.filters = []

        qry = FisherMan.objects.annotate(
            is_old=Case(
                When(Q(last_successful_catch=ten_days_ago) | Q(last_successful_catch__isnull=True), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('name')

        form = FishermanFilterForm(self.request.GET)
        if form.is_valid():
            print(form.cleaned_data)
            if form.cleaned_data['fish_type']:
                qry = qry.filter(fish_type__slug=form.cleaned_data['fish_type'])
                self.filters.append(form.cleaned_data['fish_type'])

            if form.cleaned_data['strategy']:
                qry = qry.filter(strategy=form.cleaned_data['strategy'])
                self.filters.append(form.cleaned_data['strategy'])

            if form.cleaned_data['active']:
                active = form.cleaned_data['active'] == "true"
                qry = qry.filter(active=active)
                self.filters.append(f"active={active}")

            if form.cleaned_data['is_fishing']:
                is_fishing = form.cleaned_data['is_fishing'] == "true"
                qry = qry.filter(is_fishing=is_fishing)
                self.filters.append(f"is_fishing={is_fishing}")

            if form.cleaned_data['dangerous'] and show_dangerous_fish(self.request):
                    qry = qry.filter(is_dangerous=form.cleaned_data['dangerous'])
                    self.filters.append('dangerous')
            else:
                qry = qry.exclude(is_dangerous=True)

            if form.cleaned_data['never_fished']:
                qry = qry.filter(last_successful_catch__isnull=True)
                self.filters.append('never fished')

        return qry.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = list(filter(lambda x: x not in [None, ''], self.filters))
        context['form'] = FishermanFilterForm(self.request.GET)
        context["count"] = self.get_queryset().count()
        return context

class FishermanDetailView(DetailView):
    model = FisherMan
    template_name = "fleet/fisherman/detail.html"
    context_object_name = "fisherman"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fish_type = context['fisherman'].fish_type.name if context['fisherman'].fish_type else ""
        json_data = dict(
            name=context['fisherman'].name,
            base_url=context['fisherman'].base_url,
            active=context['fisherman'].active,
            is_fishing=context['fisherman'].is_fishing,
            strategy=context['fisherman'].strategy,
            is_dangerous=context['fisherman'].is_dangerous,
            fish_type=fish_type,
            store_catching_info=context['fisherman'].store_catching_info
        )

        if context["fisherman"].additional_data and context["fisherman"].additional_data != "{}":
            json_data["additional_data"] = context["fisherman"].additional_data.replace('"', '\"')
        else:
            json_data["additional_data"] = "{}"

        context["json_data"] = json.dumps(json_data, indent=4)
        context["recent_nets"] = context['fisherman'].nets.order_by("-id")[:50]
        context["recent_fishes"] = context['fisherman'].fishes.order_by("-id")[:50]
        return context


class FishermanCreateView(CreateView):
    model = FisherMan
    template_name = "fleet/fisherman/create.html"
    fields = [
        'name',
        'base_url',
        'fish_type',
        'strategy',
        'additional_data',
        'notes',
        # 'is_fishing',
        'active',
        'is_dangerous',
        'store_catching_info'
    ]

    # success_url = reverse_lazy('crawler:siteconf-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print('path:', os.path.realpath(__file__))
        # import pdb; pdb.set_trace()
        return context


class FishermanUpdateView(UpdateView):
    model = FisherMan
    template_name = "fleet/fisherman/edit.html"
    fields = [
        'name',
        'base_url',
        'fish_type',
        'strategy',
        'additional_data',
        'notes',
        'active',
        'is_fishing',
        'is_dangerous',
        'store_catching_info'
    ]
    # success_url = reverse_lazy('crawler:siteconf-list')
    context_object_name = "fisherman"

    def form_valid(self, form):
        response = super().form_valid(form)

        # update dangerous status in related nets and fishes
        fisherman = form.instance
        fisherman.nets.all().update(is_dangerous=fisherman.is_dangerous)
        fisherman.fishes.all().update(is_dangerous=fisherman.is_dangerous)

        messages.success(self.request, "Updated fisherman details successfully.")

        return response
        # return response


class FishermanDeleteView(DeleteView):
    model = FisherMan
    template_name = "fleet/generic/delete.html"
    success_url = reverse_lazy('fleet:fisherman-list')


class CloneFisherman(View):
    def get(self, request, *args, **kwargs):
        original_obj = get_object_or_404(FisherMan, slug=kwargs['slug'])
        obj_dict = model_to_dict(original_obj)

        obj_dict.pop('id')
        obj_dict.pop('fish_type')
        obj_dict.pop('last_successful_catch')
        obj_dict['is_fishing'] = False

        new_uuid = uuid.uuid4()
        # Get the last 4 characters of the UUID's hex string
        short_uuid = new_uuid.hex[-4:]

        new_obj = FisherMan(**obj_dict, fish_type=original_obj.fish_type)
        new_obj.name = f"{new_obj.name} - Clone({short_uuid})"

        new_obj.save()
        return redirect(reverse_lazy('fleet:fisherman-edit', kwargs=dict(slug=new_obj.slug)))


class CreateFishermanByJSONView(FormView):
    template_name = 'fleet/fisherman/create.html'
    form_class = FishermanCreateByJSONForm
    success_url = None

    def form_valid(self, form):
        json_data = json.loads(form.cleaned_data.get("json_data"))
        fish_type, _ = FishType.objects.get_or_create(name=json_data.get("fish_type"))
        fisherman = FisherMan.objects.create(
            name=json_data.get("name"),
            strategy=json_data.get("strategy"),
            base_url=json_data.get("base_url"),
            additional_data=json_data.get("additional_data"),
            active=json_data.get("active"),
            # is_fishing=json_data.get("is_fishing"),
            is_dangerous=json_data.get("is_dangerous"),
            notes=json_data.get("notes"),
            store_catching_info=json_data.get("store_catching_info"),
            fish_type=fish_type
        )
        self.success_url = reverse_lazy('fleet:fisherman-detail', kwargs=dict(slug=fisherman.slug))
        return super().form_valid(form)


# Short & fun fisherman name generator
def generate_fisherman_name(base_name):
    prefixes = [
        "Salty", "Cap", "Hook", "Reel", "Deep", "Tide", "Drifty", "Gill", "Bait", "Sailor",
        "Shark", "Wave", "Moby", "Barnacle", "Anchor", "Fishy", "Buoy", "Marlin", "Chum"
    ]
    suffixes = [
        "Fin", "Tide", "Net", "Reel", "Hook", "Wake", "Bait", "Sail", "Drift", "Gill",
        "Splash", "Chum", "Catch", "Plank", "Rod", "Lure", "Kraken", "Pirate", "Buoy"
    ]

    return f"{random.choice(prefixes)} {base_name}" if random.choice(
        [True, False]) else f"{base_name} {random.choice(suffixes)}"


# JSON response view
def fisherman_name_json(request):
    base_name = request.GET.get("name", "").strip()

    if not base_name:
        return JsonResponse({"error": "Name parameter is required"}, status=400)

    # Generate 10 unique fun fisherman names
    fisherman_names = list(set(generate_fisherman_name(base_name) for _ in range(20)))[:10]  # Ensure 10 unique names

    return JsonResponse({"fisherman_names": fisherman_names})


# @method_decorator(login_required(login_url='/login/'), name='dispatch')
# @custom_required_class_based
# class SiteConfListView(ListView):
#     model = SiteConf
#     template_name = "crawler/siteconf/list.html"
#     context_object_name = "siteconfs"
#     paginate_by = 10  # Pagination
#     # queryset = SiteConf.objects.order_by('-id')
#
#     def get_queryset(self):
#         from pprint import pprint
#
#         ten_days_ago = timezone.now() - timedelta(days=10)
#
#         self.filters = []
#
#         qry = SiteConf.objects.annotate(
#             is_old=Case(
#                 When(Q(last_successful_sync__lt=ten_days_ago) | Q(last_successful_sync__isnull=True), then=Value(True)),
#                 default=Value(False),
#                 output_field=BooleanField()
#             )
#         )
#
#         form = SiteConfFilterForm(self.request.GET)
#         if form.is_valid():
#             if form.cleaned_data['category']:
#                 qry = qry.filter(category__slug=form.cleaned_data['category'])
#                 self.filters.append(form.cleaned_data['category'])
#
#             if form.cleaned_data['scraper_name']:
#                 qry = qry.filter(scraper_name=form.cleaned_data['scraper_name'])
#                 self.filters.append(form.cleaned_data['scraper_name'])
#
#             if form.cleaned_data['enabled']:
#                 enabled = form.cleaned_data['enabled'] == "true"
#                 qry = qry.filter(enabled=enabled)
#                 self.filters.append(f"enabled={enabled}")
#
#             if form.cleaned_data['is_locked']:
#                 is_locked = form.cleaned_data['is_locked'] == "true"
#                 qry = qry.filter(is_locked=is_locked)
#                 self.filters.append(f"is_locked={is_locked}")
#
#             if form.cleaned_data['ns']:
#                 if check_if_ns_enabled(self.request):
#                     qry = qry.filter(ns_flag=form.cleaned_data['ns'])
#                     self.filters.append('ns')
#             else:
#                 qry = qry.exclude(ns_flag=True)
#
#             if form.cleaned_data['never_synced']:
#                 qry = qry.filter(last_successful_sync__isnull=True)
#                 self.filters.append('never-synced')
#
#         return qry.order_by('-id')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['filters'] = list(filter(lambda x: x not in [None, ''], self.filters))
#         context['form'] = SiteConfFilterForm(self.request.GET)
#         context["count"] = self.get_queryset().count()
#         return context


# class SiteConfDetailView(DetailView):
#     model = SiteConf
#     template_name = "crawler/siteconf/detail.html"
#     context_object_name = "siteconf"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         category = context['siteconf'].category.name if context['siteconf'].category else ""
#         json_data = dict(
#             name=context['siteconf'].name,
#             base_url=context['siteconf'].base_url,
#             enabled=context['siteconf'].enabled,
#             is_locked=context['siteconf'].is_locked,
#             scraper_name=context['siteconf'].scraper_name,
#             ns_flag=context['siteconf'].ns_flag,
#             category=category,
#             store_raw_data=context['siteconf'].store_raw_data
#         )
#
#         if context["siteconf"].extra_data_json and context["siteconf"].extra_data_json != "{}":
#             json_data["extra_data_json"] = context["siteconf"].extra_data_json.replace('"', '\"')
#         else:
#             json_data["extra_data_json"] = "{}"
#
#         context["json_data"] = json.dumps(json_data, indent=4)
#         context["recent_jobs"] = context['siteconf'].jobs.order_by("-id")[:50]
#         context["recent_items"] = context['siteconf'].items.order_by("-id")[:50]
#         # context['active_queues'] = context['siteconf'].queues.exclude(status="COMPLETED").order_by("-id")
#         return context


# class SiteConfCreateView(CreateView):
#     model = SiteConf
#     template_name = "crawler/siteconf/create.html"
#     fields = [
#         'name', 'base_url', 'category', 'scraper_name', 'extra_data_json', 'notes', 'is_locked', 'enabled',
#         'ns_flag', 'store_raw_data'
#     ]
#     success_url = reverse_lazy('crawler:siteconf-list')


# class SiteConfUpdateView(UpdateView):
#     model = SiteConf
#     template_name = "crawler/siteconf/edit.html"
#     fields = ['name', 'base_url', 'category', 'scraper_name', 'extra_data_json', 'notes', 'is_locked',
#               'enabled', 'ns_flag', 'store_raw_data']
#     success_url = reverse_lazy('crawler:siteconf-list')
#     context_object_name = "siteconf"


# class SiteConfDeleteView(DeleteView):
#     model = SiteConf
#     template_name = "crawler/generic/delete.html"
#     success_url = reverse_lazy('crawler:siteconf-list')


# class DuplicateSiteConfListView(View):
#     def get(self, request, *args, **kwargs):
#         original_obj = get_object_or_404(SiteConf, slug=kwargs['slug'])
#         obj_dict = model_to_dict(original_obj)
#         # obj_dict.category = original_obj.category
#         obj_dict.pop('id')  # remove the ID field to avoid duplication
#         obj_dict.pop('category')
#         obj_dict.pop('last_successful_sync')
#
#         new_uuid = uuid.uuid4()
#         # Get the last 4 characters of the UUID's hex string
#         short_uuid = new_uuid.hex[-4:]
#
#         new_obj = SiteConf(**obj_dict, category=original_obj.category)
#         new_obj.name = f"{new_obj.name} - Copy({short_uuid})"
#
#         new_obj.save()
#         return redirect(reverse_lazy('crawler:siteconf-edit', kwargs=dict(slug=new_obj.slug)))


# class SiteConfByJSONView(FormView):
#     template_name = 'crawler/siteconf/create.html'
#     form_class = SiteConfFormByJSON
#     success_url = None
#
#     def form_valid(self, form):
#         json_data = json.loads(form.cleaned_data.get("json_data"))
#         category, _ = Category.objects.get_or_create(name=json_data.get("category"))
#         sc_obj = SiteConf.objects.create(
#             name=json_data.get("name"),
#             scraper_name=json_data.get("scraper_name"),
#             base_url=json_data.get("base_url"),
#             extra_data_json=json_data.get("extra_data_json"),
#             enabled=json_data.get("enabled"),
#             is_locked=json_data.get("is_locked"),
#             ns_flag=json_data.get("ns_flag"),
#             notes=json_data.get("notes"),
#             store_raw_data=json_data.get("store_raw_data"),
#             category=category
#         )
#         self.success_url = reverse_lazy('crawler:siteconf-detail', kwargs=dict(slug=sc_obj.slug))
#         return super().form_valid(form)


# def crawl(request, slug):
#     wait_time = int(request.GET.get("wait_time", 0))
#     site_conf: SiteConf = get_object_or_404(SiteConf, slug=slug)
#
#     if not site_conf.enabled:
#         return JsonResponse({'status': 'ERROR', 'message': 'SiteConf crawling is disabled'})
#
#     if site_conf.is_locked:
#         return JsonResponse({'status': 'ERROR', 'message': 'Crawling In-progress'})
#
#     ib = InvokeBackend(site_conf, wait_time=wait_time)
#
#     flag = request.GET.get("redirect_to_job")
#
#     if flag and flag.lower() == 'yes':
#         return redirect(f'/job/{ib.job.id}')
#
#     return JsonResponse({"status": "OK", "message": f"Crawling Started, job_id: {ib.job.id}"})


# class DataDump(View):
#     def get(self, request):
#         categories = list(Category.objects.values('name', 'slug'))
#         config_values = list(ConfigValues.objects.values('key', 'val'))
#
#         site_confs = list(SiteConf.objects.values(
#             'base_url',
#             'category__name',
#             'enabled',
#             "extra_data_json",
#             "is_locked",
#             "last_successful_sync",
#             "name",
#             "notes",
#             "ns_flag",
#             "scraper_name",
#             "slug",
#             "store_raw_data"
#         ))
#         return JsonResponse({
#             "categories": categories,
#             "config_values": config_values,
#             "site_confs": site_confs
#         })



# @method_decorator(login_required(login_url='/login/'), name='dispatch')
# class DataBulkCreate(FormView):
#     template_name = 'crawler/generic/data_bulk_create.html'
#     form_class = BulkCreateForm
#     success_url = reverse_lazy('crawler:siteconf-list')
#
#     def form_valid(self, form):
#         data = json.loads(form.cleaned_data.get("data"))
#         categories = dict()
#
#         created_objects = dict(
#             categories=0,
#             site_confs=0,
#             config_values=0
#         )
#         # create categories
#         for entry in data['categories']:
#             logger.debug(f"creating categories if not exists: {entry}")
#             categories[entry['name']], created = Category.objects.get_or_create(name=entry['name'], slug=entry['slug'])
#
#             if created:
#                 created_objects["categories"] = created_objects["categories"] + 1
#
#         # create config-values
#         for entry in data['config_values']:
#             logger.debug("creating config-values is not exists: {entry}")
#             _, created = ConfigValues.objects.get_or_create(
#                 key=entry.get('key'),
#                 val=entry.get('val'),
#             )
#
#             if created:
#                 created_objects["config_values"] = created_objects["config_values"] + 1
#
#         # create site_confs
#         slug_list = [x['slug'] for x in data['site_confs']]
#         existing_db_obj = SiteConf.objects.filter(slug__in=slug_list)
#         existing_sc_slug = [sc.slug for sc in existing_db_obj]
#
#         for entry in data['site_confs']:
#             logger.debug(f"creating site-confs if not exists")
#
#             if entry['slug'] in existing_sc_slug:
#                 continue
#
#             sc = SiteConf(
#                     base_url=entry.get("base_url"),
#                     category=categories.get(entry.get('category__name', None), {}),
#                     enabled=entry.get("enabled"),
#                     extra_data_json=entry.get("extra_data_json"),
#                     is_locked=False,
#                     last_successful_sync=None,
#                     name=entry.get("name"),
#                     notes=entry.get("notes"),
#                     ns_flag=entry.get("ns_flag"),
#                     scraper_name=entry.get("scraper_name"),
#                     store_raw_data=entry.get("store_raw_data")
#                 )
#             sc.save()
#             created_objects["site_confs"] = created_objects["site_confs"] + 1
#
#         msg = (f'Created - Categories:{created_objects["categories"]}, '
#                f'ConfigValues:{created_objects["config_values"]}, '
#                f'SiteConf:{created_objects["site_confs"]}')
#         messages.add_message(self.request, messages.INFO, message=msg)
#         return super().form_valid(form)