from datetime import timedelta
import json
import uuid

from django.db.models import Case, When, Value, BooleanField, Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import SiteConfFormByJSON, SiteConfFilterForm
from .job_views import InvokeBackend
from .models import SiteConf, Category

def convert_qp_to_qf(request, type_):
    """
    this function converts query params to query filter
    :param request:
    :return:
    """
    col_mapping = {
        "site_conf": {
            "cat": "category__slug",
            "scraper": "scraper_name"
        }
    }

    filters = dict()
    for key, val in request.GET.items():
        if key.startswith('f-'):
            k = key[2:]
            if k in col_mapping[type_]:
                filters[col_mapping[type_][k]] = val


class SiteConfListView(ListView):
    model = SiteConf
    template_name = "crawler/siteconf/list.html"
    context_object_name = "siteconfs"
    paginate_by = 10  # Pagination
    # queryset = SiteConf.objects.order_by('-id')

    def get_queryset(self):
        ten_days_ago = timezone.now() - timedelta(days=10)
        # ns_flag = True if self.request.GET.get('ns', 'no').lower() == "yes" else False

        self.filters = []

        qry = SiteConf.objects.annotate(
            is_old=Case(
                When(Q(last_successful_sync__lt=ten_days_ago) | Q(last_successful_sync__isnull=True), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        form = SiteConfFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['category']:
                qry = qry.filter(category__slug=form.cleaned_data['category'])
                self.filters.append(form.cleaned_data['category'])

            if form.cleaned_data['scraper_name']:
                qry = qry.filter(scraper_name=form.cleaned_data['scraper_name'])
                self.filters.append(form.cleaned_data['scraper_name'])

            if form.cleaned_data['enabled']:
                enabled = form.cleaned_data['enabled'] == "true"
                qry = qry.filter(enabled=enabled)
                self.filters.append(f"enabled={enabled}")

            if form.cleaned_data['is_locked']:
                is_locked = form.cleaned_data['is_locked'] == "true"
                qry = qry.filter(is_locked=is_locked)
                self.filters.append(f"is_locked={is_locked}")

            if form.cleaned_data['ns']:
                qry = qry.filter(ns_flag=form.cleaned_data['ns'])
                self.filters.append('ns')
            else:
                qry = qry.exclude(ns_flag=True)

            if form.cleaned_data['never_synced']:
                qry = qry.filter(last_successful_sync__isnull=True)
                self.filters.append('never-synced')


        # if ns_flag:
        #     qry = qry.exclude(ns_flag=False)
        # else:
        #     qry = qry.exclude(ns_flag=True)
        return qry.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = list(filter(lambda x: x not in [None, ''], self.filters))
        context['form'] = SiteConfFilterForm(self.request.GET)
        context["count"] = self.get_queryset().count()
        return context


class SiteConfDetailView(DetailView):
    model = SiteConf
    template_name = "crawler/siteconf/detail.html"
    context_object_name = "siteconf"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        json_data = dict(
            name=context['siteconf'].name,
            base_url=context['siteconf'].base_url,
            enabled=context['siteconf'].enabled,
            is_locked=context['siteconf'].is_locked,
            scraper_name=context['siteconf'].scraper_name,
            ns_flag=context['siteconf'].ns_flag,
            category=context['siteconf'].category.name,
            store_raw_data=context['siteconf'].store_raw_data
        )

        if context["siteconf"].extra_data_json and context["siteconf"].extra_data_json != "{}":
            json_data["extra_data_json"] = context["siteconf"].extra_data_json.replace('"', '\"')
        else:
            json_data["extra_data_json"] = "{}"

        context["json_data"] = json.dumps(json_data, indent=4)
        context["recent_jobs"] = context['siteconf'].jobs.order_by("-id")[:50]
        context["recent_items"] = context['siteconf'].items.order_by("-id")[:50]
        # context['active_queues'] = context['siteconf'].queues.exclude(status="COMPLETED").order_by("-id")
        return context


class SiteConfCreateView(CreateView):
    model = SiteConf
    template_name = "crawler/siteconf/create.html"
    fields = [
        'name', 'base_url', 'category', 'scraper_name', 'extra_data_json', 'notes', 'is_locked', 'enabled',
        'ns_flag', 'store_raw_data'
    ]
    success_url = reverse_lazy('crawler:siteconf-list')


class SiteConfUpdateView(UpdateView):
    model = SiteConf
    template_name = "crawler/siteconf/edit.html"
    fields = ['name', 'base_url', 'category', 'scraper_name', 'extra_data_json', 'notes', 'is_locked',
              'enabled', 'ns_flag', 'store_raw_data']
    success_url = reverse_lazy('crawler:siteconf-list')
    context_object_name = "siteconf"


class SiteConfDeleteView(DeleteView):
    model = SiteConf
    template_name = "crawler/generic/delete.html"
    success_url = reverse_lazy('crawler:siteconf-list')


class DuplicateSiteConfListView(View):
    def get(self, request, *args, **kwargs):
        # sc: SiteConf = get_object_or_404(SiteConf, pk=pk)

        original_obj = get_object_or_404(SiteConf, slug=kwargs['slug'])
        obj_dict = model_to_dict(original_obj)
        # obj_dict.category = original_obj.category
        obj_dict.pop('id')  # remove the ID field to avoid duplication
        obj_dict.pop('category')
        obj_dict.pop('last_successful_sync')

        new_uuid = uuid.uuid4()
        # Get the last 4 characters of the UUID's hex string
        short_uuid = new_uuid.hex[-4:]

        new_obj = SiteConf(**obj_dict, category=original_obj.category)
        new_obj.name = f"{new_obj.name} - Copy({short_uuid})"

        new_obj.save()
        return redirect(reverse_lazy('crawler:siteconf-edit', kwargs=dict(slug=new_obj.slug)))


class SiteConfByJSONView(FormView):
    template_name = 'crawler/siteconf/create.html'
    form_class = SiteConfFormByJSON
    success_url = None

    def form_valid(self, form):
        json_data = json.loads(form.cleaned_data.get("json_data"))
        category, _ = Category.objects.get_or_create(name=json_data.get("category"))
        sc_obj = SiteConf.objects.create(
            name=json_data.get("name"),
            scraper_name=json_data.get("scraper_name"),
            base_url=json_data.get("base_url"),
            extra_data_json=json_data.get("extra_data_json"),
            enabled=json_data.get("enabled"),
            is_locked=json_data.get("is_locked"),
            ns_flag=json_data.get("ns_flag"),
            notes=json_data.get("notes"),
            store_raw_data=json_data.get("store_raw_data"),
            category=category
        )
        self.success_url = reverse_lazy('crawler:siteconf-detail', kwargs=dict(slug=sc_obj.slug))
        return super().form_valid(form)


def crawl(request, slug):
    wait_time = int(request.GET.get("wait_time", 0))
    site_conf: SiteConf = get_object_or_404(SiteConf, slug=slug)

    if not site_conf.enabled:
        return JsonResponse({'status': 'ERROR', 'message': 'SiteConf crawling is disabled'})

    if site_conf.is_locked:
        return JsonResponse({'status': 'ERROR', 'message': 'Crawling In-progress'})

    ib = InvokeBackend(site_conf, wait_time=wait_time)

    flag = request.GET.get("redirect_to_job")

    if flag and flag.lower() == 'yes':
        return redirect(f'/job/{ib.job.id}')

    return JsonResponse({"status": "OK", "message": f"Crawling Started, job_id: {ib.job.id}"})