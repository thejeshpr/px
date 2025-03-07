import logging

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    divs = soup.find_all("div", {"class": "media-body"})

    for div in divs:
        a = div.find('a')
        if a:
            url = a.attrs.get("href").strip()
            p_list = div.find_all("p")
            data = ""
            if len(p_list) >= 2:
                data = p_list[1].text.strip()

            handler.verify_and_create_item(
                unique_key=url,
                name=a.text.strip(),
                url=Handler.url_join(base_url, url),
                data=data
            )


