from django.urls import path
from . import views
from . import cat_views
from . import item_views
from . import job_views
from . import config_views
from . import q_views

from . import test_views


app_name = 'crawler'

urlpatterns = [
    path('', q_views.QueueListView.as_view(), name='home'),

    path('sc/', views.SiteConfListView.as_view(), name='siteconf-list'),
    path('sc/add/', views.SiteConfCreateView.as_view(), name='siteconf-add'),
    path('sc/add/json', views.SiteConfByJSONView.as_view(), name='siteconf-add-json'),
    path('sc/<slug:slug>/', views.SiteConfDetailView.as_view(), name='siteconf-detail'),
    path('sc/<slug:slug>/edit/', views.SiteConfUpdateView.as_view(), name='siteconf-edit'),
    path('sc/<slug:slug>/delete/', views.SiteConfDeleteView.as_view(), name='siteconf-delete'),
    path('sc/<slug:slug>/crawl/', views.crawl, name='siteconf-crawl'),
    path('sc/<slug:slug>/duplicate/', views.DuplicateSiteConfListView.as_view(), name='siteconf-duplicate'),
    path('sc/<slug:slug>/add-to-q/', q_views.QueueCreateView.as_view(), name='siteconf-create-q'),

    path('queue/', q_views.QueueListView.as_view(), name='q-list'),
    path('queue/process/', q_views.ProcessQueues.as_view(), name='q-process'),
    path('queue/<int:pk>/', q_views.JobQueueDetailView.as_view(), name='q-detail'),

    path('job/', job_views.JobListView.as_view(), name='job-list'),
    path('job/<int:pk>', job_views.JobDetailView.as_view(), name='job-detail'),
    path('job/<int:pk>/raw-data', job_views.JobRawDataView.as_view(), name='job-raw-data'),
    path('job/bulk-create', job_views.BulkJobCreation.as_view(), name='job-create-bulk'),

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

    path('item/', item_views.ItemListView.as_view(), name='item-list'),
    path('item/add/', item_views.ItemCreateView.as_view(), name='item-add'),
    path('item/<int:pk>/toggle-bookmark', item_views.toggle_bookmark, name='item-bookmark'),
    # path('item/bookmarks', item_views.BookmarkItemListView.as_view(), name='item-bookmark-list'),

    path('item-ns/', item_views.ns_item_list_view_wrapper, name='item-list-ns'),

    path('data/bulk/dump', views.DataDump.as_view(), name='data-bulk-dump'),
    path('data/bulk/create', views.DataBulkCreate.as_view(), name='data-bulk-create'),

]