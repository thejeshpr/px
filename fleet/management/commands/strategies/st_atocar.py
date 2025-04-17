import json
import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_catching_info(soup.prettify())

    for div in soup.find_all('div', {'class': 'ns-con-height'}):
        a = div.find('a')
        a.get('href')
        p = div.find('p', {"class": "new-pare-p"})
        data = p.text.strip() if p else ""

        handler.verify_and_add_fish(
            tracking_id=a.get('href'),
            name=div.find('h2').text.strip(),
            link=handler.url_join(additional_data.get('item_base_url'), a.get('href')),
            data=data
        )


