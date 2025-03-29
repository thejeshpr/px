from django.urls import path
from . import views
from . import v_fisherman
from . import v_fish_type
from . import v_fish
from . import v_net
from . import v_ship_config
from . import v_ship
from . import v_others

app_name = 'fleet'

urlpatterns = [
    path('', v_ship.ShipListView.as_view(), name='home'),

    path('fisherman/', v_fisherman.FishermanListView.as_view(), name='fisherman-list'),
    path('fisherman/add/', v_fisherman.FishermanCreateView.as_view(), name='fisherman-add'),
    path('fisherman/add/json/', v_fisherman.CreateFishermanByJSONView.as_view(), name='fisherman-add-json'),
    path('fisherman/get-name/', v_fisherman.fisherman_name_json, name='fisherman-get-name'),
    path('fisherman/<slug:slug>/', v_fisherman.FishermanDetailView.as_view(), name='fisherman-detail'),
    path('fisherman/<slug:slug>/edit/', v_fisherman.FishermanUpdateView.as_view(), name='fisherman-edit'),
    path('fisherman/<slug:slug>/delete/', v_fisherman.FishermanDeleteView.as_view(), name='fisherman-delete'),
    path('fisherman/<slug:slug>/clone/', v_fisherman.CloneFisherman.as_view(), name='fisherman-clone'),

    path('fisherman/<slug:slug>/add-to-ship/', v_ship.ShipCreateView.as_view(), name='fisherman-add-to-ship'),

    path('ship/', v_ship.ShipListView.as_view(), name='ship-list'),
    path('ship/sail/', v_ship.StartShipsView.as_view(), name='ship-sail'),
    path('ship/<int:pk>/', v_ship.ShipDetailView.as_view(), name='ship-detail'),

    path('net/', v_net.NetListView.as_view(), name='net-list'),
    path('net/<int:pk>/', v_net.NetDetailView.as_view(), name='net-detail'),
    path('net/<int:pk>/raw-data/', v_net.NetRawDataView.as_view(), name='net-raw-data'),
    path('net/bulk-create', v_net.AddBulkNetsToShipView.as_view(), name='net-add-bulk-to-ship'),

    path('fish-type/', v_fish_type.FishTypeListView.as_view(), name='fish-type-list'),
    path('fish-type/add/', v_fish_type.FishTypeCreateView.as_view(), name='fish-type-add'),
    path('fish-type/<slug:slug>/', v_fish_type.FishTypeDetailView.as_view(), name='fish-type-detail'),
    path('fish-type/<slug:slug>/edit/', v_fish_type.FishTypeUpdateView.as_view(), name='fish-type-edit'),
    path('fish-type/<slug:slug>/delete/', v_fish_type.FishTypeDeleteView.as_view(), name='fish-type-delete'),

    path('ship-config/', v_ship_config.ShipConfigListView.as_view(), name='ship-config-list'),
    path('ship-config/add/', v_ship_config.ShipConfigCreateView.as_view(), name='ship-config-add'),
    path('ship-config/<slug:slug>/', v_ship_config.ShipConfigDetailView.as_view(), name='ship-config-detail'),
    path('ship-config/<slug:slug>/edit/', v_ship_config.ShipConfigUpdateView.as_view(), name='ship-config-edit'),
    path('ship-config/<slug:slug>/delete/', v_ship_config.ShipConfigDeleteView.as_view(), name='ship-config-delete'),

    path('fish/', v_fish.FishListView.as_view(), name='fish-list'),
    path('fish/add/', v_fish.FishCreateView.as_view(), name='fish-add'),
    path('fish/<int:pk>/toggle-tagged', v_fish.toggle_tag, name='fish-tag'),

    path('data/bulk/dump', v_others.DataDump.as_view(), name='data-bulk-dump'),
    path('data/bulk/create', v_others.DataBulkCreate.as_view(), name='data-bulk-create'),

    # path('showd/<int:year>/<int:month>/<int:day>/', other_views.ShowDateView.as_view(), name='show_date_view'),
    # path('show/<int:number>/', other_views.ShowView.as_view(), name='show_view'),
    # path('test/<str:data>/', other_views.TestView.as_view(), name='test-view'),

]