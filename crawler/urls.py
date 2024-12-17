from django.urls import path
from . import views

urlpatterns = [
    path('sc/', views.SiteConfListView.as_view(), name='siteconf-list'),
    path('sc/add/', views.SiteConfCreateView.as_view(), name='siteconf-add'),
    path('sc/<slug:slug>/', views.SiteConfDetailView.as_view(), name='siteconf-detail'),
    path('sc/<slug:slug>/edit/', views.SiteConfUpdateView.as_view(), name='siteconf-edit'),
    path('sc/<slug:slug>/delete/', views.SiteConfDeleteView.as_view(), name='siteconf-delete'),
]