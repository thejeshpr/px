import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    divs = soup.find_all('div', {'class': 'widget-listing-content-section'})

    for div in divs:
        a = div.find('a')
        if a:
            a = div.find('a')
            if a:
                p = div.find('p')
                data = p.text.strip() if p else ""

                handler.verify_and_create_item(
                    unique_key=a.get('href'),
                    name=a.text.strip(),
                    url=a.get('href'),
                    data=data
                )
