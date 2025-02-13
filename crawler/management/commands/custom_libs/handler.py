import datetime
import json
import logging
import time
import urllib.parse

from bs4 import BeautifulSoup
from django.utils import timezone

from crawler.models import SiteConf, Job, Item, ConfigValues
from crawler.management.commands.custom_libs import scrapper_module_finder

logger = logging.getLogger('crawler')


class Handler:
    def __init__(self, job: Job, wait_time: int):
        self.job = job
        self.wait_time = wait_time
        self.sc: SiteConf = job.site_conf
        self.items_to_create = []

        self.job_start_time = time.time()
        self.wait()

    def wait(self):
        logger.debug(f"checking for the wait time: {self.wait_time}")
        if self.wait_time > 0:
            time.sleep(self.wait_time)

    def lock_site_conf(self):
        logging.debug(f"Locking SiteConf: {self.sc.name}")
        self.sc.is_locked = True
        self.sc.save()

    def unlock_site_conf(self):
        logging.debug(f"unlocking SiteConf: {self.sc.name}")
        self.sc.is_locked = False
        self.sc.save()

    def update_job_status(self, status):
        """"""
        logging.debug(f"Update Job {self.job.id} Status: {status}")
        if status == "SUCCESS":
            task_count = Item.objects.filter(job__pk=self.job.pk).count()
            status = "SUCCESS" if task_count > 0 else "NO-ITEM"
        self.job.status = status
        self.job.save()

    def update_elapsed_time(self):
        elapsed_time = time.time() - self.job_start_time
        logging.debug(f"updating elapsed time: {elapsed_time} for job: {self.job}")
        elapsed_time = elapsed_time if elapsed_time >= 1 else 1
        self.job.elapsed_time = elapsed_time
        self.job.save()

    def start(self):
        scrapper = scrapper_module_finder.get_scrapper(self.sc.scraper_name)
        self.lock_site_conf()
        self.update_job_status('RUNNING')
        try:
            extras = self.get_sc_extra_data()
            scrapper(self, extras=extras)
            self.create_job_items()
            self.update_job_status('SUCCESS')

        except Exception as e:
            self.update_job_status('ERROR')
            self.job.error = str(e)
            self.job.save()
            logging.error(str(e))

        finally:
            self.update_elapsed_time()

            if self.job.status == "SUCCESS":
                self.sc.last_successful_sync = timezone.now()
                self.sc.save()

            self.unlock_site_conf()

    def get_sc_extra_data(self):
        return json.loads(self.sc.extra_data_json)

    def build_item_unique_key(self, unique_key):
        logging.debug(f"building unique_key: {unique_key}")
        return f"{self.sc.name}::{unique_key}"

    @staticmethod
    def is_item_exist(unique_key):
        logging.debug(f"checking item existence: {unique_key}")
        count = Item.objects.filter(unique_key=unique_key).count()
        return True if count else False

    def verify_and_create_item(self, unique_key, *args, **kwargs):
        """
        check and create the item if not exist
        """
        unique_key = self.build_item_unique_key(unique_key)
        if not Handler.is_item_exist(unique_key):
            logging.debug(f"creating unique_key : {unique_key}")
            self.items_to_create.append(
                Item(
                    unique_key=unique_key,
                    name=kwargs.get("name"),
                    url=kwargs.get("url"),
                    data=kwargs.get("data"),
                    job=self.job,
                    site_conf=self.sc,
                    category=self.sc.category
                )
            )

    @staticmethod
    def get_config_val(key):
        logging.debug(f'Fetching config values for key:{key}')
        conf: ConfigValues = ConfigValues.objects.filter(key=key).first()
        logging.debug(f"Conf: {conf}")
        if not conf:
            raise Exception("Invalid Configuration Key")
        logging.debug(f'config value for key is {conf.val}')
        return conf.val

    def create_job_items(self):
        if self.items_to_create:
            logging.info(f"creating {len(self.items_to_create)} for {self.sc.name}, job: {self.job.id}")
            Item.objects.bulk_create(self.items_to_create)
        else:
            logging.info(
                f"data is up to date, no new tasks will be created for {self.sc.name}, job: {self.job.id}")

    def update_raw_data(self, raw_data, byte_data=False):
        logger.debug(f"storing raw data of job: {self.job.id} of SC: {self.sc.name}")
        if self.sc.store_raw_data:

            if byte_data:
                raw_data = BeautifulSoup(raw_data.decode("utf-8")).prettify()

            self.job.raw_data = raw_data

    @staticmethod
    def url_join(base_url, sub_utl):
        return urllib.parse.urljoin(base_url, sub_utl)

