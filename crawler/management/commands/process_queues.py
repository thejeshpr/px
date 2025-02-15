import datetime
import time
import traceback
import  logging

from django.core.management.base import BaseCommand
from crawler.models import Job, JobQueue
from django.utils import timezone

from crawler.management.commands.custom_libs.handler import Handler

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Process crawl queue request"

    # def add_arguments(self, parser):
    #     parser.add_argument("job_id", type=int)
    #     parser.add_argument("wait_time", type=int, default=0)

    def handle(self, *arg, **options):
        job_queues = JobQueue.objects.filter(status="WAITING").order_by("-id").all()
        if not job_queues:
            print("No Queues to process")

        errors = []

        for q in job_queues:
            try:
                q.status = "PROCESSING"
                q.processed_at = timezone.now()
                q.save()

                print(f"processing q: {q}")
                for job in q.jobs.all():
                    logger.info(f"processing job: {job}")
                    handler_obj = Handler(job, 0)
                    handler_obj.start()
                    time.sleep(5)

                # q.status = "COMPLETED"

            except Exception as e:
                q.status = "ERROR"
                # q.error = str(traceback.format_exc())
                errors.append(str(traceback.format_exc()))
                continue

            finally:
                if q.jobs.filter(status="ERROR").exists():
                    q.status = "ERROR"
                    errs = "\n\n".join(errors)
                    q.error = f"One or More job failed in this Queue:\n {errs}"
                else:
                    q.status = "COMPLETED"

                q.save()

