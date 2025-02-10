import json
import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)

    handler.update_raw_data(str(soup.prettify()))

    for card in soup.find_all("div", {"class": "view-card__top"}):
        a = card.find("a")
        if a:
            div = card.find("div", {"class": "view-card__excerpt"})
            if div:
                data = div.text.strip()
            else:
                data = ""

            handler.verify_and_create_item(
                unique_key=a.attrs.get('href'),
                name=a.text.strip(),
                url=a.attrs.get('href'),
                data=data
            )
