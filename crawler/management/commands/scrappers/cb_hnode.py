import json
import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    # soup = WebClient.get_bs(base_url)
    res = WebClient.get(base_url)

    data = res.json()
    handler.update_raw_data(json.dumps(data, indent=4))

    for post in res.json().get('posts'):
        name = post.get('title')
        if post['publication'].get('domainStatus'):
            if post['publication']['domainStatus'].get('ready'):
                url = f"https://{post['publication']['domain']}/{post['slug']}"
            else:
                url = f"https://{post['publication']['username']}.hashnode.dev/{post['slug']}"
        else:
            url = f"https://{post['author']['username']}.hashnode.dev/{post['slug']}"

        handler.verify_and_create_item(
            unique_key=post["_id"],
            name=name,
            url=url,
            data=post.get("brief", "")
        )


