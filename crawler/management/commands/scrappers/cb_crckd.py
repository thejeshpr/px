import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    articles = soup.find_all("article")
    for article in articles:
        a = article.find("a")
        if a:
            handler.verify_and_create_item(
                unique_key=a.get('href'),
                name=a.attrs.get("title"),
                url=a.get('href'),
                # data=data
            )




