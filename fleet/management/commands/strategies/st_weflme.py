import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    res = WebClient.get(base_url)

    data = res.json()
    handler.update_catching_info(json.dumps(data, indent=4))

    for item in res.json().get('posts'):
        name = item.get("post").get('name')
        tracking_id = item.get("post").get('id')
        link = item.get("post").get('ap_id')
        body = item.get('post').get('body')
        published = item.get('post').get('published')

        community = item.get('community').get('title')

        data = (f"pub: {published}\n"
                f"community: {community}\n"
                f"data: {body}")

        handler.verify_and_add_fish(
            tracking_id=tracking_id,
            name=name,
            link=link,
            data=data
        )


