import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    res = WebClient.get(base_url)

    if res.status_code == 200:
        jdata = res.json()
        handler.update_catching_info(jdata)

        for item in jdata["data"]["posts"]:
            data = (f"desc: {item['excerpt']}"
                    f"data: {item['date']}")
            handler.verify_and_add_fish(
                tracking_id=item["ID"],
                name=f'[{item["topic"]}] - {item["title"]}',
                link=Handler.url_join(
                    additional_data["article_base_url"], item["slug"]
                ),
                data=data
            )
    else:
        handler.update_catching_info(res.content.strip())
        logging.error(f"Error while fetching andrauth data: {res}")
        raise Exception(f"Error while fetching andrauth data: {res}")

