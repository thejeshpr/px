import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    for div in soup.find_all('div', {'class': "dw-single-update dw-tax-name col-9"}):
        a = div.find('a')
        if a:
            handler.verify_and_create_item(
                unique_key=a.get('href'),
                name=a.text.strip(),
                url=a.get('href'),
            )




