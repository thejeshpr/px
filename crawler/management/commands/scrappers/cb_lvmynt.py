import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    for h2 in soup.find_all('h2', {'class': 'headline'}):
        a = h2.find('a')
        if a:
            url = Handler.url_join(extras.get("article_base_url"), a.get('href'))
            handler.verify_and_create_item(
                unique_key=url,
                name=a.text.strip(),
                url=Handler.url_join(base_url, url)
            )
