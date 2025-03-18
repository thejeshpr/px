import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_catching_info(soup.prettify())

    divs = soup.find_all('div', {'class': "w-display-card-content"})

    for div in divs:
        a = div.find('a')
        if a:
            p = div.find('p')
            data = p.text.strip() if p else ""
            url = a.get('href')
            handler.verify_and_add_fish(
                tracking_id=url,
                name=a.text.strip(),
                link=Handler.url_join(base_url, url),
                data=data
            )
