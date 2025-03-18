import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_catching_info(soup.prettify())

    divs = soup.find_all("div", {"class": "media-body"})

    for div in divs:
        a = div.find('a')
        if a:
            url = a.attrs.get("href").strip()
            p_list = div.find_all("p")
            data = ""
            if len(p_list) >= 2:
                data = p_list[1].text.strip()

            handler.verify_and_add_fish(
                tracking_id=url,
                name=a.text.strip(),
                link=Handler.url_join(base_url, url),
                data=data
            )
