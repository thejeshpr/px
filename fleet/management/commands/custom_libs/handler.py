import datetime
import json
import logging
import time
import urllib.parse

from bs4 import BeautifulSoup
from django.utils import timezone

from fleet.models import FisherMan, Net, Fish, ShipConfig
from fleet.management.commands.custom_libs import strategy_finder

logger = logging.getLogger('fleet')


class Handler:
    def __init__(self, net: Net, wait_time: int):
        self.net = net
        self.wait_time = wait_time
        self.fs: FisherMan = net.fisherman
        self.fishes_to_create = []

        self.net_deployed_time = time.time()
        self.wait()

    def wait(self):
        logger.debug(f"checking for the wait time: {self.wait_time}")
        if self.wait_time > 0:
            time.sleep(self.wait_time)

    def update_fisherman_status(self, fishing_status):
        logging.debug(f"updating fisherman: {self.fs.name} to fishing")
        self.fs.is_fishing = fishing_status
        self.fs.save()

    def undock_fisherman(self):
        logging.debug(f"undocking fisherman: {self.fs.name}")
        self.fs.is_docked = False
        self.fs.save()

    def update_net_status(self, status):
        """"""
        logging.debug(f"Update net {self.net.id} Status: {status}")
        if status == "FISHED":
            fish_count = Fish.objects.filter(net=self.net).count()
            status = "FISHED" if fish_count > 0 else "EMPTY"
        self.net.status = status
        self.net.save()

    def update_fishing_time(self):
        elapsed_time = time.time() - self.net_deployed_time
        logging.debug(f"updating fishing time: {elapsed_time} for net: {self.net}")
        self.net.elapsed_time = elapsed_time if elapsed_time >= 1 else 1
        self.net.save()

    def start(self):
        try:
            strategy = strategy_finder.get_strategy(self.fs.strategy)
            self.update_fisherman_status(fishing_status=True)
            self.update_net_status('IN-USE')

            additional_data = self.get_fisherman_additional_data()
            strategy(self, additional_data=additional_data)
            self.create_fishes()
            self.update_net_status('FISHED')

        except Exception as e:
            self.update_net_status('DAMAGED')
            self.net.problem = str(e)
            self.net.save()
            logging.error(str(e))

        finally:
            self.update_fishing_time()
            self.undock_fisherman()

            if self.net.status == "FISHED":
                self.fs.last_successful_catch = timezone.now()
                self.fs.save()

            self.update_fisherman_status(fishing_status=False)

    def get_fisherman_additional_data(self):
        return json.loads(self.fs.additional_data)

    def build_fish_tracking_id(self, tracking_id):
        logging.debug(f"building fish tracking id: {tracking_id}")
        return f"{self.fs.name}::{tracking_id}"

    @staticmethod
    def is_fish_exist(tracking_id):
        logging.debug(f"checking fish existence: {tracking_id}")
        count = Fish.objects.filter(tracking_id=tracking_id).count()
        return True if count else False

    def verify_and_add_fish(self, tracking_id, *args, **kwargs):
        """
        check and create the fish if not exist
        """
        tracking_id = self.build_fish_tracking_id(tracking_id)
        if not Handler.is_fish_exist(tracking_id):
            logging.debug(f"creating unique_key : {tracking_id}")
            self.fishes_to_create.append(
                Fish(
                    tracking_id=tracking_id,
                    name=kwargs.get("name"),
                    link=kwargs.get("link"),
                    additional_info=kwargs.get("data"),
                    net=self.net,
                    fisherman=self.fs,
                    fish_type=self.fs.fish_type,
                    ship=self.net.ship,
                    is_dangerous=self.fs.is_dangerous
                )
            )

    @staticmethod
    def get_config_val(key):
        logging.debug(f'Fetching ship config for key:{key}')
        conf: ShipConfig = ShipConfig.objects.filter(key=key).first()

        if not conf:
            raise Exception(f"Invalid Ship Config Key: {key}")

        return conf.val

    def create_fishes(self):
        if self.fishes_to_create:
            logging.info(f"Adding {len(self.fishes_to_create)} to {self.fs.name}, Net: {self.net.id}")
            Fish.objects.bulk_create(self.fishes_to_create)
        else:
            logging.info(f"No fishes caught for {self.fs.name}, Net: {self.net.id}")

    def update_catching_info(self, raw_data, byte_data=False):
        logger.debug(f"storing raw data of net: {self.net.id} of FS: {self.fs.name}")

        if self.fs.store_catching_info:
            if byte_data:
                raw_data = BeautifulSoup(raw_data.decode("utf-8")).prettify()

            self.net.raw_data = raw_data

    @staticmethod
    def url_join(base_url, sub_url):
        return urllib.parse.urljoin(base_url, sub_url)

