import datetime
import sys

from django.core import management
from django.core.management.commands import loaddata
from django.http import HttpResponse, JsonResponse

import os
import subprocess
import time

from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import SiteConf, Job, Category


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
    paginate_by = 50  # Pagination

    def get_queryset(self):
        sc = self.request.GET.get("sc")
        cat = self.request.GET.get("cat")
        dt = self.request.GET.get("dt")
        status = self.request.GET.get("status")

        qry = Job.objects

        if sc:
            qry = qry.filter(site_conf__slug=sc)

        if cat:
            qry = qry.filter(category__slug=cat)

        if dt:
            if dt.count("-") == 2:
                dd, mm, yyyy = dt.split("-")
                qry = qry.filter(created_at__year=int(yyyy), created_at__month=int(mm), created_at__day=int(dd))

        if status:
            qry = qry.filter(status=status.upper())

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sc_slug = self.request.GET.get("sc")
        cat_slug = self.request.GET.get("cat")
        dt = self.request.GET.get("dt")
        status = self.request.GET.get("status")

        context['header'] = ''

        if sc_slug:
            context["header"] = get_object_or_404(SiteConf, slug=sc_slug)
        if cat_slug:
            cat = get_object_or_404(Category, slug=cat_slug)
            if context["header"]:
                context["header"] = f"{context['header']} | {cat}"
            else:
                context["header"] = cat
        if dt:
            if context["header"]:
                context["header"] = f"{context['header']} | {dt}"
            else:
                context["header"] = dt

        if status:
            if context["header"]:
                context["header"] = f"{context['header']} | {status}"
            else:
                context["header"] = status
        context["count"] = self.get_queryset().count()
        return context


class JobDetailView(DetailView):
    model = Job
    template_name = "crawler/job/detail.html"
    context_object_name = "job"
