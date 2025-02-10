import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from .models import SiteConf, Job, Item, Category
from .forms import ItemCreateForm


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
                ns_flag=ns_flag
            )

            Item.objects.create(
                is_bookmarked=form.cleaned_data['bookmark'],
                name=form.cleaned_data['name'],
                url=form.cleaned_data['url'],
                data=form.cleaned_data['data'],
                site_conf=sc,
                unique_key=str(uuid.uuid4())
            )
            context["errors"] = form.errors
            return redirect(reverse_lazy('crawler:siteconf-detail', kwargs=dict(slug=sc.slug)))

        else:
            print(form.errors)
            context["errors"] = form.errors
            return render(request, self.template_name, context=context)


class ItemListView(ListView):
    model = Item
    template_name = "crawler/item/list.html"
    context_object_name = "items"
    paginate_by = 50  # Pagination
    # queryset = Item.objects.order_by('-id')

    def get_queryset(self):
        sc = self.request.GET.get("sc")
        if sc:
            return Item.objects.filter(site_conf__slug=sc).order_by('-id')
        return Item.objects.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sc_slug = self.request.GET.get("sc")
        context["sc"] = get_object_or_404(SiteConf, slug=sc_slug) if sc_slug else None
        return context
