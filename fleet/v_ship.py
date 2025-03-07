import os
import subprocess
import sys
import time
import traceback
import random
from typing import List
import logging

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse

from .models import Ship, FisherMan, Net
from .forms import ShipFilterForm
from .other_libs import show_dangerous_fish

logger = logging.getLogger(__name__)


def get_ship_name(dangerous=False):
    adjectives = [
        "Stormy", "Salty", "Brave", "Fearless", "Jolly", "Rusty", "Blazing",
        "Mysterious", "Daring", "Seaworthy", "Barnacled", "Swift", "Golden",
        "Howling", "Tattered", "Shadowy", "Bold", "Clever", "Wandering",
        "Silver", "Mighty", "Loyal", "Thunderous", "Fearsome", "Ironclad"
    ]

    nouns = [
        "Seagull", "Dolphin", "Galleon", "Mariner", "Voyager", "Windrunner",
        "Explorer", "Captain", "Navigator", "Compass", "Wave", "Breeze",
        "Anchor", "Sailor", "Harpoon", "Sea Rover", "Gust", "Current",
        "Adventure", "Buoy", "Star", "Harbor", "Ocean", "Lagoon", "Beacon"
    ]

    d_adjectives = [
        "Stormy", "Salty", "Brave", "Jolly", "Rusty", "Blazing", "Howling", "Rowdy",
        "Drunken", "Raging", "Wicked", "Cursed", "Sneaky", "Plundering", "Greedy",
        "Grimy", "Sly", "Shady", "Lusty", "Reckless", "Thirsty", "Foul", "Wild"
    ]

    d_nouns = [
        "Seagull", "Dolphin", "Galleon", "Mariner", "Voyager", "Compass", "Anchor",
        "Rum Barrel", "Deckhand", "Plunderer", "Rogue", "Scoundrel", "Deck Beast",
        "Cannon", "Bounty", "Swindler", "Siren", "Kraken", "Wench", "Rogue Sail",
        "Cutlass", "Pillager", "Wreck", "Parrot", "Grog Chugger", "Scallywag",
        "Barnacle", "Bilge Rat", "Scurvy Dog"
    ]
    if dangerous:
        return f"{random.choice(d_adjectives)}-{random.choice(d_nouns)}"
    return f"{random.choice(adjectives)}-{random.choice(nouns)}"


def get_docked_ship(dangerous=False):
    ship = Ship.objects.filter(status="WAITING", is_dangerous=dangerous)
    if not ship:
        ship_name = get_ship_name(dangerous=dangerous)
        ship = Ship.objects.create(name=ship_name, is_dangerous=dangerous)
    else:
        ship = ship.first()
    return ship


def check_fisher_is_eligible_for_ship(request, ship, fisherman):
    """
    :param request:
    :param ship:
    :param fisherman:
    :return:
    """
    if ship.nets.filter(fisherman__name=fisherman.name).exists():
        messages.add_message(request, messages.WARNING, f"Fisher:{fisherman.name} is already assigned to Ship: {ship.name}")
        return False
    else:
        return True
    # return [fisher for fisher in ship.nets.values_list('fisherman__name', flat=True)]


def add_to_ship(request, fishers: List[FisherMan]):
    """
    """
    logger.debug("assigning fisherman to Ship")

    ship = None
    d_ship = None
    nets = list()

    for fisherman in fishers:
        if not fisherman.active or fisherman.name in ['default', 'd-default']:
            continue

        ship = get_docked_ship(dangerous=fisherman.is_dangerous)

        net = Net(fisherman=fisherman, fish_type=fisherman.fish_type, is_dangerous=fisherman.is_dangerous)

        if check_fisher_is_eligible_for_ship(request, ship, fisherman):
            net.ship = ship
            nets.append(net)
        else:
            logger.debug("fisher is already assigned to ship")

        # if fisherman.is_dangerous:
        #     if check_fisher_is_eligible_for_ship(request, d_ship, fisherman):
        #         d_ship = d_ship or get_docked_ship(dangerous=True)
        #         net.ship = d_ship
        #     else:
        #         logger.debug("fisher is already assigned to ship")
        #
        # else:
        #     # if fisherman.name not in ship.net.fisherman
        #     if check_fisher_is_eligible_for_ship(request, ship, fisherman):
        #         ship = ship or get_docked_ship()
        #         net.ship = ship
        #     else:
        #         logger.debug("fisher is already assigned")



    if not nets:
        msg = "No valid fishers found to assign to ship"
        logger.debug(msg)
        messages.add_message(request, messages.WARNING, msg)
        return False

    assigned_nets = Net.objects.bulk_create(nets)
    logger.debug(f"added {len(nets)} nets")
    messages.add_message(request, messages.INFO, f"Assigned {len(nets)} Fishers")
    return True


class ShipCreateView(View):
    template_name = 'fleet/ship/list.html'

    def get(self, request, *args, **kwargs):
        fisherman = get_object_or_404(FisherMan, slug=kwargs['slug'])
        if not fisherman.active or fisherman.name in ['Jon', 'Tormund']:
            return JsonResponse(dict(
                is_success=False,
                error_message=f"{fisherman.name} cannot be assigned to ship"
            ))

        add_to_ship(request, [fisherman])

        # if request.GET.get("force_sync", None) == "yes":
        #     process_queue()

        return redirect(reverse_lazy('fleet:ship-list'))


class ShipListView(ListView):
    model = Ship
    template_name = "fleet/ship/list.html"
    context_object_name = "ships"
    paginate_by = 50  # Pagination

    def get_queryset(self):
        qry = Ship.objects
        self.filters = []
        form = ShipFilterForm(self.request.GET)

        if form.is_valid():

            if form.cleaned_data["departure_time"]:
                dt = form.cleaned_data["departure_time"]
                qry = qry.filter(departure_time__year=dt.year, departure_time__month=dt.month, departure_time__day=dt.day)
                self.filters.append(form.cleaned_data["departure_time"])

            if form.cleaned_data["status"]:
                qry = qry.filter(status=form.cleaned_data["status"])
                self.filters.append(form.cleaned_data["status"])

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
        if Ship.objects.filter(status="WAITING").count():
            context["ships_waiting"] = True

        context['filters'] = self.filters
        context["count"] = self.get_queryset().count()
        context['form'] = ShipFilterForm(self.request.GET)
        return context


class ShipDetailView(DetailView):
    model = Ship
    template_name = "fleet/ship/detail.html"
    context_object_name = "ship"


def start_ships():
    parent_path = os.path.dirname(os.path.realpath(__file__))
    base_path = os.path.dirname(parent_path)

    script_path = os.path.join(base_path, 'manage.py')
    cmd = f'{sys.executable} "{script_path}" start_ships'

    try:
        logger.debug(f"issuing cmd: {cmd}")
        envs = os.environ.copy()
        o = subprocess.Popen(cmd, shell=True, env=envs)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"ERROR while invoking backend cmds: {err}")
        raise Exception(e)


class StartShipsView(View):
    def get(self, request, *args, **kwargs):
        ships = Ship.objects.filter(status="WAITING").order_by("-id").all()
        if not ships:
            return JsonResponse(dict(
                status="ok",
                message="No ships docked"
            ))
        else:
            msg = f"{len(ships)} will be started"
            try:
                start_ships()
            except Exception as e:
                err = traceback.format_exc()
                logger.exception(e)
                messages.add_message(request, messages.ERROR, message=f"Failed to start the ships: {err}")
                # messages.add_message(request, messages.ERROR, message=str(err))

            else:
                # messages.add_message(request, messages.INFO, message="Queue(s) pushed for processing")
                messages.add_message(request, messages.INFO, message=f"Issued command to start docked ships")

                if request.GET.get("redirect_to_ship_list", "no").lower() == "yes":
                    time.sleep(2)
                    return redirect(reverse_lazy("fleet:ship-list"))

                return JsonResponse(dict(
                    status="ok",
                    message=msg
                ))
