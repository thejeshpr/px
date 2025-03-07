import datetime
import sys

from django.contrib import messages
from django.core import management
from django.core.management.commands import loaddata
from django.http import HttpResponse, JsonResponse

import os
import subprocess
import time

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView

from .models import FisherMan, Net, ShipConfig
from .other_libs import show_dangerous_fish
from .v_ship import get_docked_ship, add_to_ship
from .forms import NetFilterForm


class NetListView(ListView):
    model = Net
    template_name = "fleet/net/list.html"
    context_object_name = "nets"
    paginate_by = 25  # Pagination

    def get_queryset(self):

        qry = Net.objects
        self.filters = []
        form = NetFilterForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["fish_type"]:
                qry = qry.filter(fish_type__slug=form.cleaned_data["fish_type"])
                self.filters.append(form.cleaned_data["fish_type"])

            if form.cleaned_data["fisherman"]:
                qry = qry.filter(fisherman__slug=form.cleaned_data["fisherman"])
                self.filters.append(form.cleaned_data["fisherman"])

            if form.cleaned_data["deployed_at"]:
                dt = form.cleaned_data["deployed_at"]
                qry = qry.filter(deployed_at__year=dt.year, deployed_at__month=dt.month, deployed_at__day=dt.day)
                self.filters.append(form.cleaned_data["deployed_at"])

            if form.cleaned_data["status"]:
                qry = qry.filter(status=form.cleaned_data["status"])
                self.filters.append(form.cleaned_data["status"])

            if form.cleaned_data["dangerous"]:
                if show_dangerous_fish(self.request):
                    qry = qry.filter(is_dangerous=True)
                    self.filters.append('dangerous')
            else:
                qry = qry.filter(is_dangerous=False)

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sc_slug = self.request.GET.get("sc")
        # cat_slug = self.request.GET.get("cat")
        # dt = self.request.GET.get("dt")
        # status = self.request.GET.get("status")

        # context['header'] = ''
        #
        # if sc_slug:
        #     context["header"] = get_object_or_404(SiteConf, slug=sc_slug)
        # if cat_slug:
        #     cat = get_object_or_404(Category, slug=cat_slug)
        #     if context["header"]:
        #         context["header"] = f"{context['header']} | {cat}"
        #     else:
        #         context["header"] = cat
        # if dt:
        #     if context["header"]:
        #         context["header"] = f"{context['header']} | {dt}"
        #     else:
        #         context["header"] = dt
        #
        # if status:
        #     if context["header"]:
        #         context["header"] = f"{context['header']} | {status}"
        #     else:
        #         context["header"] = status

        context['filters'] = self.filters
        context["count"] = self.get_queryset().count()

        # ns = self.request.GET.get("ns", "").strip()
        # if ns:
        #     site_confs = SiteConf.objects.filter(ns_flag=True).values_list('slug', 'slug').distinct()
        #     site_conf_choices = [('', 'All Site Configs')] + list(site_confs)
        #
        #     form = JobFilterForm(self.request.GET, site_conf=site_conf_choices)
        # else:
        #     form = JobFilterForm(self.request.GET)

        show_dangerous = self.request.GET.get("dangerous", "")
        context["form"] = NetFilterForm(self.request.GET, show_dangerous=show_dangerous)
        return context


class NetDetailView(DetailView):
    model = Net
    template_name = "fleet/net/detail.html"
    context_object_name = "net"


class NetRawDataView(DetailView):
    model = Net
    template_name = "fleet/net/raw_data.html"
    context_object_name = "net"


class AddBulkNetsToShipView(View):
    template = "fleet/net/bulk_create.html"

    def get(self, request):
        context = dict()
        slug_exclude_list = ["jon", "tormund"]

        # check if sc is given
        fishers = request.GET.get("fishers")
        dangerous = request.GET.get("dangerous", "")
        dangerous_flag = True if dangerous and dangerous.lower() in ["yes", "on", "true"] else False

        if fishers:
            fishers_list = fishers.split(",")
            fishers_objs = FisherMan.objects.filter(slug__in=fishers_list).exclude(is_dangerous=not dangerous_flag).all()
            status = add_to_ship(self.request, fishers=fishers_objs)

            if status:
                messages.add_message(request, messages.INFO, "Ship Docked")

            return redirect(reverse_lazy('fleet:ship-list'))

        qry = FisherMan.objects.filter(active=True).exclude(slug__in=slug_exclude_list)
        qry = qry.exclude(is_dangerous=not dangerous_flag)

        context["fishers"] = qry.order_by("-id")
        context["dangerous"] = "on" if dangerous_flag else ""
        return render(request, self.template, context=context)


