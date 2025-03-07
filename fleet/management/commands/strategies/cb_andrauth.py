import json
import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    res = WebClient.get(base_url)

    if res.status_code == 200:
        jdata = res.json()
        handler.update_raw_data(json.dumps(jdata, indent=4))

        for item in jdata["data"]["posts"]:
            data = (f"desc: {item['excerpt']}"
                    f"data: {item['date']}")
            handler.verify_and_create_item(
                unique_key=item["ID"],
                name=f'[{item["topic"]}] - {item["title"]}',
                url=Handler.url_join(
                    extras["article_base_url"], item["slug"]
                ),
                data=data
            )
    else:
        handler.update_raw_data(res.content.strip())
        logging.error(f"Error while fetching andrauth data: {res}")

