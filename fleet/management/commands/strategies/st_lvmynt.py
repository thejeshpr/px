import logging

from fleet.management.commands.custom_libs.web_client import WebClient
from fleet.management.commands.custom_libs.handler import Handler


def instructions(handler: Handler, additional_data, *args, **kwargs):
    base_url = handler.fs.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_catching_info(soup.prettify())

    for h2 in soup.find_all('h2', {'class': 'headline'}):
        a = h2.find('a')
        if a:
            url = Handler.url_join(additional_data.get("article_base_url"), a.get('href'))
            handler.verify_and_add_fish(
                tracking_id=url,
                name=a.text.strip(),
                link=Handler.url_join(base_url, url)
            )
