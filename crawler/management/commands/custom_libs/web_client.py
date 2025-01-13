import json
import logging
import os

import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from websockets.exceptions import InvalidStatusCode

# from crawler_backend import BaseParser
from crawler.management.commands.custom_libs.handler import Handler

logging.getLogger(__name__)


class WebClient:
    @staticmethod
    def check_status_code(res):
        if res.status_code not in [200]:
            logging.error(f"invalid status code: {res.status_code}\n{res.content}")
            raise Exception(f"Invalid status code: {res.status_code}\n{res.content}")

    @staticmethod
    def get(url):
        session = HTMLSession()
        logging.debug(f"connecting to {url}")
        res = session.get(url)
        WebClient.check_status_code(res)
        return res

    @staticmethod
    def post_phjs(
            url: str,
            output_as_json: str = "true",
            render_type: str = "plainText",
            return_json: bool = False,
    ):
        # use phantom js to access the content
        data = {
            "url": url,
            "renderType": render_type,
            "outputAsJson": output_as_json
        }

        key = Handler.get_config_val("phantom_js_key")
        url = Handler.get_config_val("phantom_js_url")

        url = url.format(key=key)

        res = requests.post(url, data=json.dumps(data))
        logging.debug(f"status_code: {res.status_code}")
        logging.debug(f"response: {res.content}")
        WebClient.check_status_code(res)
        return res.content if not return_json else res.json()

    @staticmethod
    def get_soup_phjs(url: str):
        content = WebClient.post_phjs(url=url, output_as_json="false", render_type="html")
        return BeautifulSoup(content, 'html.parser')

    @staticmethod
    def get_bs(url: str):
        res = WebClient.get(url)
        return BeautifulSoup(res.html.html, 'html.parser')

    @staticmethod
    def put(url, headers=dict(), payload=dict()):
        session = HTMLSession()
        logging.debug(f"connecting to {url}")
        res = session.post(url, headers=headers, data=payload)
        WebClient.check_status_code(res)
        return res




