import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    a_list = soup.find_all('a', {'class': 'article-title link-hover-underline-blue'})

    for a in a_list:
        handler.verify_and_create_item(
            unique_key=a.get('href'),
            name=a.text.strip(),
            url=handler.url_join(extras['article_base_url'], a.get('href'))
        )





