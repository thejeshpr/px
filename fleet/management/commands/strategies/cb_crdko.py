import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    # soup = WebClient.get_bs(base_url)
    res = WebClient.get(base_url)
    handler.update_raw_data(res.content, byte_data=True)

    links = res.html.xpath("/html/body/div[2]/div/div[1]/div/main/div[3]/div[1]/div[1]/div/div[*]/div[2]/h2/a")

    for link in links:
        url = link.attrs.get('href')
        handler.verify_and_create_item(
            unique_key=url,
            name=link.text.strip(),
            url=Handler.url_join(base_url, url),
            # data=data
        )
