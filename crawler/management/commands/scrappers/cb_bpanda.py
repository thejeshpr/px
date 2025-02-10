import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    cat = extras.get("category", "")
    typ = extras.get("type", "")
    url = handler.sc.base_url.format(category=cat, type=typ)

    soup = WebClient.get_bs(url)
    handler.update_raw_data(soup.prettify())

    section = soup.find("section")
    if section:
        for a in section.find_all("a", {"class": "title post-link"}):
            link = a.attrs.get("href").split("?")[0]
            name = a.text.strip()
            handler.verify_and_create_item(
                unique_key=link,
                name=name,
                url=link,
                data=""
            )
