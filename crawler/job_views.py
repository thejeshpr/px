import datetime
import sys

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

from .models import SiteConf, Job, Category
from .q_views import get_waiting_q
from .forms import JobFilterForm


class InvokeBackend:
    """"""
    def __init__(self, site_conf, auto_start=True, wait_time=0):
        self.site_conf = site_conf
        self.job = None
        self.wait_time = wait_time

        if auto_start:
            self.execute()

    def execute(self):
        self.create_job()
        self.invoke_backend_crawler()

    def create_job(self):
        self.job = Job(site_conf=self.site_conf, category=self.site_conf.category)
        self.job.save()

    def invoke_backend_crawler(self):
        parent_path = os.path.dirname(os.path.realpath(__file__))
        base_path = os.path.dirname(parent_path)
        #base_path = "/home/ubuntu/pyenvs/projectx_dev/src/projectx"

        # script_path = os.path.join(base_path, 'crawler', 'management', 'commands', 'test_cmd.py')
        script_path = os.path.join(base_path, 'manage.py')

        # create config object to place python interpreter
        # cmd = f'/home/ubuntu/pyenvs/projectx_dev/bin/python "{script_path}" {self.job.id}'
        # cmd = f'python "{script_path}" {self.job.id} --wait-time {self.wait_time}'

        # cmd = f'python "{script_path}" test_cmd {self.job.id}'
        cmd = f'{sys.executable} "{script_path}" crawl {self.job.id} {self.wait_time}'
        print(f"cmd: {cmd}")
        print("starting process")
        o = subprocess.Popen(cmd, shell=True)
        print(f"command o/p: {o.stdout}")








def invoke_job(request):
    # management.call_command("flush", verbosity=0, interactive=False)
    op = management.call_command("test_cmd", "123")
    # management.call_command(loaddata.Command(), "test_data", verbosity=0)
    return HttpResponse(op)


class JobListView(ListView):
    model = Job
    template_name = "crawler/job/list.html"
    context_object_name = "jobs"
    paginate_by = 10  # Pagination

    def get_queryset(self):
        # sc = self.request.GET.get("sc")
        # cat = self.request.GET.get("cat")
        # dt = self.request.GET.get("dt")
        # status = self.request.GET.get("status")

        qry = Job.objects
        self.filters = []
        form = JobFilterForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["category"]:
                qry = qry.filter(category__slug=form.cleaned_data["category"])
                self.filters.append(form.cleaned_data["category"])

            if form.cleaned_data["site_conf"]:
                qry = qry.filter(site_conf__slug=form.cleaned_data["site_conf"])
                self.filters.append(form.cleaned_data["site_conf"])

            if form.cleaned_data["created_at"]:
                print(form.cleaned_data["created_at"])
                dt = form.cleaned_data["created_at"]
                qry = qry.filter(created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day)
                self.filters.append(form.cleaned_data["created_at"])

            if form.cleaned_data["status"]:
                qry = qry.filter(status=form.cleaned_data["status"])
                self.filters.append(form.cleaned_data["status"])

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
        context["form"] = JobFilterForm(self.request.GET)
        return context


class JobDetailView(DetailView):
    model = Job
    template_name = "crawler/job/detail.html"
    context_object_name = "job"


class JobRawDataView(DetailView):
    model = Job
    template_name = "crawler/job/raw_data.html"
    context_object_name = "job"


class BulkJobCreation(View):
    template = "crawler/job/bulk_create.html"
    def get(self, request):
        context = dict()

        # check if sc is given
        sc = request.GET.get("sc")
        ns = True if request.GET.get("ns", "no").lower() == "yes" else False

        sc_slug_exclude_list = ["default", "default-ns"]
        if sc:
            sc_list = sc.split(",")
            site_confs = SiteConf.objects.filter(slug__in=sc_list, enabled=True).exclude(slug__in=sc_slug_exclude_list).all()
            q = get_waiting_q()
            jobs_list = [Job(site_conf=sc, category=sc.category, queue=q) for sc in site_confs]
            res = Job.objects.bulk_create(jobs_list)
            return redirect(reverse_lazy('crawler:q-list'))

        qry = SiteConf.objects.filter(enabled=True).exclude(slug__in=sc_slug_exclude_list)

        if ns:
            qry = qry.exclude(ns_flag=False)
        else:
            qry = qry.exclude(ns_flag=True)

        context["site_confs"] = qry.order_by("-id")
        return render(request, self.template, context=context)



