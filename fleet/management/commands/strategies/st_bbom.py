import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_catching_info(soup.prettify())

    for card in soup.find_all("div", {"class": "view-card__top"}):
        a = card.find("a")
        if a:
            div = card.find("div", {"class": "view-card__excerpt"})
            if div:
                data = div.text.strip()
            else:
                data = ""

            handler.verify_and_add_fish(
                tracking_id=a.get('href'),
                name=a.text.strip(),
                link=a.get('href'),
                data=data
            )


