import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    divs = soup.find_all('div', {'class': "w-display-card-content"})

    for div in divs:
        a = div.find('a')
        if a:
            p = div.find('p')
            data = p.text.strip() if p else ""
            url = a.get('href')
            handler.verify_and_create_item(
                unique_key=url,
                name=a.text.strip(),
                url=Handler.url_join(base_url, url),
                data=data
            )
