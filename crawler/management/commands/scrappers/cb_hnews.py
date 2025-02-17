import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    spans = soup.find_all('span', {'class': 'titleline'})
    for span in spans:
        a = span.find('a')
        if a:
            site_info = span.find('span', {'class': "sitebit comhead"})
            if site_info:
                title = f"{a.text.strip()} - {site_info.text.strip()}"
            else:
                title = a.text.strip()

            handler.verify_and_create_item(
                unique_key=a.get("href"),
                name=title,
                url=a.get("href")
                # data=data
            )