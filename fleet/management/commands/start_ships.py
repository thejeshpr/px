import datetime
import time
import traceback
import logging

from django.core.management.base import BaseCommand
from fleet.models import Ship
from django.utils import timezone

from fleet.management.commands.custom_libs.handler import Handler
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Start the docked ships"

    def handle(self, *arg, **options):
        ships = Ship.objects.filter(status="WAITING").order_by("id").all()
        if not ships:
            logger.debug("No Ships docked to start")

        errors = []

        for ship in ships:
            start_time = time.time()
            try:
                ship.status = "SAILING"
                ship.departure_time = timezone.now()
                ship.save()

                logger.info(f"sailing ship: {ship}")
                for net in ship.nets.all():
                    logger.info(f"throwing nets by : {net.fisherman.name}")
                    handler_obj = Handler(net, 0)
                    handler_obj.start()
                    time.sleep(3)

            except Exception as e:
                ship.status = "DAMAGED"
                errors.append(str(traceback.format_exc()))
                logger.error(traceback.format_exc())
                continue

            finally:
                if ship.nets.filter(status="DAMAGED").exists():
                    ship.status = "DAMAGED"
                    errs = "\n\n".join(errors)
                    ship.problem = f"One or More nets damaged in this Ship:\n {errs}"
                    logger.error("updating ship status to damaged")
                else:
                    ship.status = "RETURNED"
                    logger.info("updating ship status to returned")

                ship.time_spent = time.time() - start_time
                ship.save()

