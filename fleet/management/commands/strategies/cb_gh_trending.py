from uuid import uuid4

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url
    soup = WebClient.get_bs(base_url)
    handler.update_raw_data(soup.prettify())

    for article in soup.find_all('article', {"class": "Box-row"}):
        a = article.find('a', {'class': "Link"})
        p = article.find('p')
        data = p.text.strip() if p else ""

        handler.verify_and_create_item(
            unique_key=str(uuid4()),
            name=a.text.strip(),
            url=f"{extras.get('article_base_url')}{a.get('href')}",
            data=data
        )

