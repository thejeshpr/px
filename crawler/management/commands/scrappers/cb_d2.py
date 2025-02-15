import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    tag = extras["tag"] if "tag" in extras.keys() else ""
    if tag:
        base_url = Handler.url_join(base_url, tag)

    res = WebClient.get(base_url)
    handler.update_raw_data(res.content, byte_data=True)

    h2_list = res.html.find(".crayons-story__title")

    for h2 in h2_list:
        a = h2.find("a", first=True)
        if a:
            url = a.attrs.get('href')
            handler.verify_and_create_item(
                unique_key=a.attrs.get("id").strip(),
                name=a.text.strip(),
                url=Handler.url_join(base_url, url),
            )
