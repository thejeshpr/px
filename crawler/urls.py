from django.urls import path
from . import views
from . import cat_views
from . import item_views
from . import job_views
from . import config_views
from . import test_views

app_name = 'crawler'

urlpatterns = [
    path('sc/', views.SiteConfListView.as_view(), name='siteconf-list'),
    path('sc/add/', views.SiteConfCreateView.as_view(), name='siteconf-add'),
    path('sc/add/json', views.SiteConfByJSONView.as_view(), name='siteconf-add-json'),
    path('sc/<slug:slug>/', views.SiteConfDetailView.as_view(), name='siteconf-detail'),
    path('sc/<slug:slug>/edit/', views.SiteConfUpdateView.as_view(), name='siteconf-edit'),
    path('sc/<slug:slug>/delete/', views.SiteConfDeleteView.as_view(), name='siteconf-delete'),
    path('sc/<slug:slug>/crawl/', views.crawl, name='siteconf-crawl'),
    path('sc/<slug:slug>/duplicate/', views.DuplicateSiteConfListView.as_view(), name='siteconf-duplicate'),

    path('category/', cat_views.CategoryListView.as_view(), name='category-list'),
    path('category/add/', cat_views.CategoryCreateView.as_view(), name='category-add'),
    path('category/<slug:slug>/', cat_views.CategoryDetailView.as_view(), name='category-detail'),
    path('category/<slug:slug>/edit/', cat_views.CategoryUpdateView.as_view(), name='category-edit'),
    path('category/<slug:slug>/delete/', cat_views.CategoryDeleteView.as_view(), name='category-delete'),

    path('config_values/', config_views.ConfigValuesListView.as_view(), name='config-values-list'),
    path('config_values/add/', config_views.ConfigValuesCreateView.as_view(), name='config-values-add'),
    path('config_values/<slug:slug>/', config_views.ConfigValuesDetailView.as_view(), name='config-values-detail'),
    path('config_values/<slug:slug>/edit/', config_views.ConfigValuesUpdateView.as_view(), name='config-values-edit'),
    path('config_values/<slug:slug>/delete/', config_views.ConfigValuesDeleteView.as_view(), name='config-values-delete'),

    path('item/add/', item_views.ItemCreateView.as_view(), name='item-add'),


    path('network-graph/', test_views.network_graph, name='network_graph'),

    # path('job/run/', job_views, name='job-run'),

]