import datetime
import time
import traceback

from django.core.management.base import BaseCommand
from crawler.models import Job, JobQueue

from crawler.management.commands.custom_libs.handler import Handler

class Command(BaseCommand):
    help = "Process crawl queue request"

    # def add_arguments(self, parser):
    #     parser.add_argument("job_id", type=int)
    #     parser.add_argument("wait_time", type=int, default=0)

    def handle(self, *arg, **options):
        job_queues = JobQueue.objects.filter(status="WAITING").order_by("-id").all()
        if not job_queues:
            print("No Queues to process")

        for q in job_queues:
            try:
                q.status = "PROCESSING"
                q.processed_at = datetime.datetime.now()
                q.save()

                print(f"processing q: {q}")
                for job in q.jobs.all():
                    handler_obj = Handler(job, 0)
                    handler_obj.start()
                    time.sleep(5)

                q.status = "COMPLETED"

            except Exception as e:
                q.status = "ERROR"
                q.error = str(traceback.format_exc())

            finally:
                q.save()

