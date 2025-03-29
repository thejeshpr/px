import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    cat = additional_data.get("category", "")
    typ = additional_data.get("type", "")
    url = handler.fs.base_url.format(category=cat, type=typ)

    soup = WebClient.get_bs(url)
    handler.update_catching_info(soup.prettify())

    section = soup.find("section")

    if section:
        for a in section.find_all("a", {"class": "title post-link"}):
            link = a.attrs.get("href").split("?")[0]
            name = a.text.strip()
            handler.verify_and_add_fish(
                tracking_id=link,
                name=name,
                link=link,
                data=""
            )
