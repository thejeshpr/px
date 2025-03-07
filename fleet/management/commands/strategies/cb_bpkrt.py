import json
import logging

import requests

from crawler.management.commands.custom_libs.web_client import WebClient
from crawler.management.commands.custom_libs.handler import Handler


def scrape(handler: Handler, extras, *args, **kwargs):
    base_url = handler.sc.base_url

    headers = {
        'authority': 'api.beepkart.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'appname': 'Website',
        'cache-control': 'no-cache',
        'changesorigin': 'product-listingpage',
        'content-type': 'application/json; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://beepkart.com',
        'originid': '0',
        'pageindex': '2',
        'pragma': 'no-cache',
        'referer': 'https://beepkart.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76'
    }

    res = requests.get(base_url, headers=headers)

    handler.update_raw_data(json.dumps(res.json(), indent=4))

    for item in res.json().get('inventories'):
        name = f"{item.get('vehicle_name')} - {item.get('sale_price')}"

        data = f"year of manufacturing: {item.get('year of manufacturing')}\n" \
               f"kms_ridden: {item.get('kms_ridden')}\n" \
               f"discount_price: {item.get('discount_price')}\n" \
               f"is_reserved: {item.get('is_reserved')}\n" \
               f"Owner: {item.get('owner')}\n" \
               f"odometer_replaced: {item.get('odometer_replaced')}\n"

        handler.verify_and_create_item(
            unique_key=item.get("id"),
            name=name,
            url=f"https://beepkart.com/usedvehicle/index/buyer2/id/{item.get('id')}",
            data=data
        )


