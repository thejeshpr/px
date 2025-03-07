import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    for div in soup.find_all('div', {'class': 'ns-con-height'}):
        a = div.find('a')
        a.get('href')
        p = div.find('p', {"class": "new-pare-p"})
        data = p.text.strip() if p else ""

        handler.verify_and_create_item(
            unique_key=a.get('href'),
            name=div.find('h2').text.strip(),
            url=Handler.url_join(
                extras.get("item_base_url"), a.get('href')
            ),
            data=data
        )


