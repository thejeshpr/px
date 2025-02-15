import os
import subprocess
import sys
import time
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from .models import JobQueue, SiteConf, Job
from django.http import HttpResponse, JsonResponse

def get_waiting_q():
    q = JobQueue.objects.filter(status="WAITING")
    if not q:
        q = JobQueue.objects.create()
    else:
        q = q.first()

    return q


class QueueCreateView(View):
    template_name = 'crawler/queue/list.html'

    def get(self, request, *args, **kwargs):
        sc = get_object_or_404(SiteConf, slug=kwargs['slug'])
        if not sc.enabled:
            return JsonResponse(dict(
                is_success=False,
                error_message=f"{sc.name} is either locked or not enabled"
            ))

        q = get_waiting_q()

        Job.objects.create(site_conf=sc, category=sc.category, queue=q)

        if request.GET.get("force_sync", None) == "yes":
            process_queue()

        return redirect(reverse_lazy('crawler:q-list'))


class QueueListView(ListView):
    model = JobQueue
    template_name = "crawler/queue/list.html"
    context_object_name = "queues"
    paginate_by = 50  # Pagination
    # queryset = JobQueue.objects.order_by('-id')

    def get_queryset(self):
        status = self.request.GET.get("status")

        qry = JobQueue.objects
        if status:
            status = status.upper()
            qry = qry.filter(status=status)

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if JobQueue.objects.filter(status="WAITING").count():
            context["q_in_waiting"] = True

        context["header"] = ""

        status = self.request.GET.get("status")
        if status:
            context["header"] = status.lower()

        context["count"] = self.get_queryset().count()
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

    print(f"cmd: {cmd}")
    print("starting process")
    # o = subprocess.Popen(cmd, shell=True)
    envs = os.environ.copy()
    o = subprocess.Popen(cmd, shell=True, env=envs)
    print(o)


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
            process_queue()

            if request.GET.get("get_q_list", "no").lower() == "yes":
                time.sleep(3)
                return redirect(reverse_lazy("crawler:q-list"))

            return JsonResponse(dict(
                status="ok",
                message=msg
            ))
