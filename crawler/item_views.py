import logging
import uuid

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.utils import timezone
from django.urls import reverse_lazy

from .models import SiteConf, Job, Item, Category
from .forms import ItemCreateForm, ItemSearchForm
from .other_libs import check_if_ns_enabled


class ItemCreateView(View):
    template_name = 'crawler/item/create.html'

    def get(self, request, *args, **kwargs):
        form = ItemCreateForm()
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = ItemCreateForm(request.POST)
        context = {'form': form}

        if form.is_valid():
            sc_name = "default-ns" if form.cleaned_data['ns'] else "default"
            category, _ = Category.objects.get_or_create(name="default")
            ns_flag = form.cleaned_data['ns']
            sc, _ = SiteConf.objects.get_or_create(
                name=sc_name,
                category=category,
                ns_flag=ns_flag,
                enabled=False
            )

            Item.objects.create(
                is_bookmarked=True,
                name=form.cleaned_data['name'],
                url=form.cleaned_data['url'],
                data=form.cleaned_data['data'],
                site_conf=sc,
                unique_key=str(uuid.uuid4())
            )
            sc.last_successful_sync = timezone.now()
            self.save()
            context["errors"] = form.errors
            return redirect(reverse_lazy('crawler:siteconf-detail', kwargs=dict(slug=sc.slug)))

        else:
            logging.error(form.errors)
            context["errors"] = form.errors
            return render(request, self.template_name, context=context)


class ItemListView(ListView):
    model = Item
    template_name = "crawler/item/list.html"
    context_object_name = "items"
    paginate_by = 50  # Pagination
    # queryset = Item.objects.order_by('-id')

    def get_queryset(self):
        qry = Item.objects
        self.filters = []

        form = ItemSearchForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["category"]:
                qry = qry.filter(category__slug=form.cleaned_data["category"])
                self.filters.append(form.cleaned_data["category"])

            if form.cleaned_data["site_conf"]:
                qry = qry.filter(site_conf__slug=form.cleaned_data["site_conf"])
                self.filters.append(form.cleaned_data["site_conf"])

            if form.cleaned_data["created_at"]:
                dt = form.cleaned_data["created_at"]
                qry = qry.filter(created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day)
                self.filters.append(form.cleaned_data["created_at"])

            if form.cleaned_data["is_bookmarked"]:
                qry = qry.filter(is_bookmarked=form.cleaned_data["is_bookmarked"])
                self.filters.append(f'bookmarked')

            if form.cleaned_data["ns"]:
                if check_if_ns_enabled(self.request):
                    qry = qry.filter(site_conf__ns_flag=True)
                    self.filters.append('ns')
            else:
                qry = qry.filter(site_conf__ns_flag=False)

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["filters"] = self.filters
        context["count"] = self.get_queryset().count()

        ns = self.request.GET.get("ns", "").strip()
        if ns:
            site_confs = SiteConf.objects.filter(ns_flag=True).values_list('slug', 'slug').distinct()
            site_conf_choices = [('', 'All Site Configs')] + list(site_confs)

            form = ItemSearchForm(self.request.GET, site_conf=site_conf_choices)
        else:
            form = ItemSearchForm(self.request.GET)

        context['form'] = form
        return context


# @login_required(login_url='/login/')
def toggle_bookmark(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.is_bookmarked = not item.is_bookmarked
    item.save()
    action = "marked" if item.is_bookmarked else "unmarked"
    return JsonResponse({"status": "ok", "action": action})
