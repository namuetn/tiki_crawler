import json
import requests
import time
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import RequestException
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
import multiprocessing
from multiprocessing import freeze_support

url = 'https://tiki.vn/api/v2/products/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,fa;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Referer': 'https://tiki.vn/do-choi-me-be/c2549',
    'x-guest-token': 'LoFf91qsdKhymIYliWuc7Ha6VTXeDk2n',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

def create_file_csv(data, file_path):
    df = pd.DataFrame(data)

    # Tên tệp tin CSV
    csv_file = "product_v1.csv"

    # Lưu DataFrame thành tệp tin CSV
    df.to_csv(file_path, index=False)

    print("Tạo tệp tin CSV thành công!")

def parser_product(json_string):
    data = {}

    data['id'] = json_string.get('id')

    if 'categories' in json_string and json_string['categories'] is not None:
        data['category_id'] = json_string['categories']['id']

    data['name'] = json_string.get('name')
    data['short_description'] = json_string.get('short_description')
    data['description'] = json_string.get('description')
    data['short_url'] = json_string.get('short_url')
    data['rating'] = json_string.get('rating_average')
    data['original_price'] = json_string.get('original_price')
    data['price'] = json_string.get('price')

    base_urls = []
    images = json_string.get('images')
    if images is not None:
        for item in images:
            base_urls.append(item.get('base_url'))

    data['base_url'] = base_urls

    return data

def process_product(product_id):
    