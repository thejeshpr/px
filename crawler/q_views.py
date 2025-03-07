import os
import subprocess
import sys
import time
import traceback
from typing import List
import logging

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse

from .models import JobQueue, SiteConf, Job
from .forms import QueueFilterForm
from .other_libs import check_if_ns_enabled

logger = logging.getLogger(__name__)


def get_waiting_q(ns=False):
    q = JobQueue.objects.filter(status="WAITING", ns_flag=ns)
    if not q:
        q = JobQueue.objects.create(ns_flag=ns)
    else:
        q = q.first()

    return q


def add_to_q(request, site_confs: List[SiteConf]):
    """
    this function adds the given site_confs to waiting Q
    :param request:
    :param site_confs:
    :return:
    """
    logger.debug("adding site_confs to Q")

    q = None
    nsq = None
    jobs_to_create = list()

    for sc in site_confs:
        if not sc.enabled or sc.name in ['default', 'default-ns']:
            continue

        job = Job(site_conf=sc, category=sc.category)
        if sc.ns_flag:
            nsq = nsq or get_waiting_q(ns=True)
            job.queue = nsq

        else:
            q = q or get_waiting_q()
            job.queue = q

        jobs_to_create.append(job)

    if not jobs_to_create:
        logger.debug("no valid site conf found to add to Q")
        messages.add_message(request, messages.WARNING, "No SiteConfs Added to Q")
        return False

    created_jobs = Job.objects.bulk_create(jobs_to_create)
    logger.debug(f"added {len(jobs_to_create)} jobs")
    messages.add_message(request, messages.INFO, f"added {len(jobs_to_create)} jobs")
    return True


class QueueCreateView(View):
    template_name = 'crawler/queue/list.html'

    def get(self, request, *args, **kwargs):
        sc = get_object_or_404(SiteConf, slug=kwargs['slug'])
        if not sc.enabled or sc.name in ['default', 'default-ns']:
            return JsonResponse(dict(
                is_success=False,
                error_message=f"{sc.name} is either locked or not enabled"
            ))

        add_to_q(request, [sc])

        if request.GET.get("force_sync", None) == "yes":
            process_queue()

        return redirect(reverse_lazy('crawler:q-list'))


class QueueListView(ListView):
    model = JobQueue
    template_name = "crawler/queue/list.html"
    context_object_name = "queues"
    paginate_by = 50  # Pagination

    def get_queryset(self):
        qry = JobQueue.objects
        self.filters = []
        form = QueueFilterForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["created_at"]:
                dt = form.cleaned_data["created_at"]
                qry = qry.filter(created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day)
                self.filters.append(form.cleaned_data["created_at"])

            if form.cleaned_data["status"]:
                qry = qry.filter(status=form.cleaned_data["status"])
                self.filters.append(form.cleaned_data["status"])

            if form.cleaned_data["ns"]:
                if check_if_ns_enabled(self.request):
                    qry = qry.filter(ns_flag=True)
                    self.filters.append('ns')
            else:
                qry = qry.filter(ns_flag=False)

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if JobQueue.objects.filter(status="WAITING").count():
            context["q_in_waiting"] = True

        context['filters'] = self.filters
        context["count"] = self.get_queryset().count()
        context['form'] = QueueFilterForm(self.request.GET)
        return context


class JobQueueDetailView(DetailView):
    model = JobQueue
    template_name = "crawler/queue/detail.html"
    context_object_name = "queue"


def process_queue():
    parent_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.dirname(parent_path)

    script_path = os.path.join(base_path, 'manage.py')
    cmd = f'{sys.executable} "{script_path}" process_queues'

    try:
        logger.debug(f"invoking backend cmd: {cmd}")
        envs = os.environ.copy()
        o = subprocess.Popen(cmd, shell=True, env=envs)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"ERROR while invoking backend: {err}")
        raise Exception(e)


class ProcessQueues(View):
    def get(self, request, *args, **kwargs):
        job_queues = JobQueue.objects.filter(status="WAITING").order_by("-id").all()
        if not job_queues:
            return JsonResponse(dict(
                status="ok",
                message="No Queues to process"
            ))
        else:
            msg = f"{len(job_queues)} will be processed"
            try:
                process_queue()
            except Exception as e:
                err = traceback.format_exc()
                logger.exception(e)
                messages.add_message(request, messages.ERROR, message=str(err))

            else:
                messages.add_message(request, messages.INFO, message="Queue(s) pushed for processing")
                if request.GET.get("get_q_list", "no").lower() == "yes":
                    time.sleep(3)
                    return redirect(reverse_lazy("crawler:q-list"))

                return JsonResponse(dict(
                    status="ok",
                    message=msg
                ))
