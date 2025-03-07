import logging
import uuid

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.utils import timezone
from django.urls import reverse_lazy

from .models import FisherMan, Net, Fish, FishType
from .forms import FishAddForm, FishFilterForm
from .other_libs import show_dangerous_fish


class FishCreateView(View):
    template_name = 'fleet/fish/create.html'

    def get(self, request, *args, **kwargs):
        form = FishAddForm()
        context = {'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = FishAddForm(request.POST)
        context = {'form': form}

        if form.is_valid():
            fisherman_name = "Tormund" if form.cleaned_data['is_dangerous'] else "Jon"
            fish_type, _ = FishType.objects.get_or_create(name="default")

            is_dangerous = form.cleaned_data['is_dangerous']
            fisherman, _ = FisherMan.objects.get_or_create(
                name=fisherman_name,
                fish_type=fish_type,
                is_dangerous=is_dangerous,
                active=False
            )

            Fish.objects.create(
                tagged=True,
                name=form.cleaned_data['name'],
                link=form.cleaned_data['link'],
                additional_info=form.cleaned_data['additional_info'],
                fisherman=fisherman,
                tracking_id=str(uuid.uuid4())
            )
            fisherman.last_successful_catch = timezone.now()
            self.save()
            context["errors"] = form.errors
            return redirect(reverse_lazy('crawler:fisherman-detail', kwargs=dict(slug=fisherman.slug)))

        else:
            logging.error(form.errors)
            context["errors"] = form.errors
            return render(request, self.template_name, context=context)


class FishListView(ListView):
    model = Fish
    template_name = "fleet/fish/list.html"
    context_object_name = "fishes"
    paginate_by = 50  # Pagination

    def get_queryset(self):
        qry = Fish.objects
        self.filters = []

        form = FishFilterForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["fish_type"]:
                qry = qry.filter(fish_type__slug=form.cleaned_data["fish_type"])
                self.filters.append(form.cleaned_data["fish_type"])

            if form.cleaned_data["fisherman"]:
                qry = qry.filter(fisherman__slug=form.cleaned_data["fisherman"])
                self.filters.append(form.cleaned_data["fisherman"])

            if form.cleaned_data["caught_at"]:
                dt = form.cleaned_data["caught_at"]
                qry = qry.filter(caught_at__year=dt.year, caught_at__month=dt.month, caught_at__day=dt.day)
                self.filters.append(form.cleaned_data["caught_at"])

            if form.cleaned_data["tagged"]:
                qry = qry.filter(tagged=form.cleaned_data["tagged"])
                self.filters.append(f'tagged')

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

        context["filters"] = self.filters
        context["count"] = self.get_queryset().count()

        show_dangerous = self.request.GET.get("dangerous", "")
        form = FishFilterForm(self.request.GET, show_dangerous=show_dangerous)
        context['form'] = form
        return context







# @login_required(login_url='/login/')
def toggle_tag(request, pk):
    fish = get_object_or_404(Fish, pk=pk)
    fish.tagged = not fish.tagged
    fish.save()
    action = "tagged" if fish.tagged else "untagged"
    return JsonResponse({"status": "ok", "action": action})
