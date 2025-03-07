import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    res = WebClient.get(base_url)

    if res.status_cod == 200:
        json_data = res.json()
        handler.update_raw_data(json_data)

        for item in res.json()['data']:
            handler.verify_and_create_item(
                unique_key=item.get('url'),
                name=item.get('title'),
                url=item.get('url'),
                data=f'{item.get("description")} - {item.get("published")}'
            )
