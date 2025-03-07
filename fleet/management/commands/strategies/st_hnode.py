import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    # soup = WebClient.get_bs(base_url)
    res = WebClient.get(base_url)

    data = res.json()
    handler.update_catching_info(json.dumps(data, indent=4))

    for post in res.json().get('posts'):
        name = post.get('title')
        if post['publication'].get('domainStatus'):
            if post['publication']['domainStatus'].get('ready'):
                url = f"https://{post['publication']['domain']}/{post['slug']}"
            else:
                url = f"https://{post['publication']['username']}.hashnode.dev/{post['slug']}"
        else:
            url = f"https://{post['author']['username']}.hashnode.dev/{post['slug']}"

        handler.verify_and_add_fish(
            tracking_id=post["_id"],
            name=name,
            link=url,
            data=post.get("brief", "")
        )


