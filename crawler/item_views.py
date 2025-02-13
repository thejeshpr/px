import uuid

from django.http import JsonResponse
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
        cat = self.request.GET.get("cat")
        dt = self.request.GET.get("dt")

        qry = Item.objects
        if sc:
            qry = qry.filter(site_conf__slug=sc)
        if cat:
            qry = qry.filter(category__slug=cat)

        if dt:
            if dt.count("-") == 2:
                dd, mm, yyyy = dt.split("-")
                qry = qry.filter(created_at__year=int(yyyy), created_at__month=int(mm), created_at__day=int(dd))

        qry = qry.order_by('-id')
        return qry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sc_slug = self.request.GET.get("sc")
        cat_slug = self.request.GET.get("cat")
        dt = self.request.GET.get("dt")

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

        context["count"] = self.get_queryset().count()
        context['categories'] = Category.objects.all()
        return context


# @login_required(login_url='/login/')
def toggle_bookmark(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.is_bookmarked = not item.is_bookmarked
    item.save()
    action = "marked" if item.is_bookmarked else "unmarked"
    return JsonResponse({"status": "ok", "action": action})
