from django.core.management.base import BaseCommand
from crawler.models import Job

from fleet.management.commands.custom_libs.handler import Handler

class Command(BaseCommand):
    help = "Crawl the given Site Conf"

    def add_arguments(self, parser):
        parser.add_argument("job_id", type=int)
        parser.add_argument("wait_time", type=int, default=0)

    def handle(self, *arg, **options):
        job = Job.objects.get(id=options["job_id"])
        wait_time = options["wait_time"]
        handler_obj = Handler(job, wait_time)
        handler_obj.start()

        # self.style.SUCCESS('Successfully closed poll "%s"' % job_id)
        # print('Successfully closed poll "%s"' % job_id)
        # print(SiteConf.objects.count())
        # time.sleep(30)
        # # test = TestModel(name=job_id)
        # # test.save()
        # # self.stdout.write(
        # #     self.style.SUCCESS('Successfully closed poll "%s"' % job_id)
        # # )
        #
        # # print('Successfully closed poll "%s"' % options['job_id'])
        # # for poll_id in options["poll_ids"]:
        # #     try:
        # #         poll = Poll.objects.get(pk=poll_id)
        # #     except Poll.DoesNotExist:
        # #         raise CommandError('Poll "%s" does not exist' % poll_id)
        # #
        # #     poll.opened = False
        # #     poll.save()
        # #
        # #     self.stdout.write(
        # #         self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
        # #     )
        #
