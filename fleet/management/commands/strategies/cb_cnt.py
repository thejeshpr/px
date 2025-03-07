import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    for a in soup.find_all('a', {'class': "c-storiesNeonLatest_story md:u-col-2 sm:u-col-2 u-flexbox-column lg:u-col-2"}):
        handler.verify_and_create_item(
            unique_key=a.get('href'),
            name=a.text.strip(),
            url=Handler.url_join(base_url, a.get('href')),
            # data=data
        )




