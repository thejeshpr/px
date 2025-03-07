import base64
from datetime import timedelta, datetime

from django.views import View
from django.shortcuts import render
from datetime import date
from django.utils import timezone

from .models import ConfigValues


class ShowDateView(View):
    template = "crawler/others/show_date.html"
    def get(self, request, year, month, day, *args, **kwargs):
        try:
            selected_date = date(year, month, day)
        except ValueError:
            return render(request, self.template, {"error": "Invalid date!"})

        is_today = selected_date == date.today()

        # Context for template
        context = {
            "selected_date": selected_date.strftime("%Y-%m-%d"),
            "is_today": is_today,
        }
        return render(request, self.template, context)


class ShowView(View):
    template = "crawler/others/show.html"
    def get(self, request, number, *args, **kwargs):
        try:
            # selected_date = date(year, month, day)

            tdy = timezone.now()
            number = number/2
            number = number - tdy.year
            number = number - (tdy.month * tdy.day)
            context = {}
            if number == 0:
                context['data'] = base64.b64encode(f"{tdy.year}/{tdy.month}/{tdy.day}".encode("utf-8")).decode("utf-8")
            else:
                context['data'] = number

        except ValueError as e:
            return render(request, self.template, {"error": e})

        return render(request, self.template, context)



class TestView(View):
    template = "crawler/others/show.html"
    def get(self, request, data, *args, **kwargs):
        try:

            data = base64.b64decode(data.encode("utf")).decode("utf-8")
            print("data", data)

            y, m, d = data.split("/")
            tdy = timezone.now()
            print("tdy", tdy)

            context = {}
            if int(y) == tdy.year and int(m) == tdy.month and int(d) == tdy.day:

                delta = tdy + timedelta(minutes=1)
                val = base64.b64encode(delta.strftime("%Y:%m:%d-%H:%M:%S%Z%z").encode("utf-8")).decode("utf8")

                cfg, _ = ConfigValues.objects.get_or_create(key="range")
                cfg.val = val
                cfg.save()



                # if not cfg:
                #     ConfigValues.objects.create(
                #         key="range",
                #         val=val
                #     )
                # print("delta", delta)
                # context['data'] = delta.strftime("%Y:%m:%d-%H:%M:%S%Z%z")
                # range_data = datetime.strptime(context["data"], "%Y:%m:%d-%H:%M:%S%Z%z")
                # print(tdy < range_data)
                # print(range_data - tdy)

                # print("tdy", tdy.utcnow().timestamp())
                # print("range date", range_data.utcnow().timestamp())
            else:
                context['data'] = "nothing"

        except ValueError as e:
            print(e)
            return render(request, self.template, {"error": e})

        return render(request, self.template, context)