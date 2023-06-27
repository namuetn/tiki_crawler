import json
import requests
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
# from parent_categories_crawler import parent_categories_crawler

url = 'https://tiki.vn/api/personalish/v1/blocks/listings'

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

params = {
    'limit': 40,
    'include': 'advertisement',
    'aggregations': 2,
    'trackity_id': '6d8dc609-cca9-32c5-29cc-b1cbfecfc236',
    # 'category': 2549,
    # 'page': 1,
}

def connect_database(data):
    client = MongoClient("mongodb://localhost:27017")
    db = client["tiki_database"]
    collection = db["categories"]
    result = collection.insert_one(data)

    print("Inserted document ID:", result.inserted_id)

def parser_categories(json):
    data = {}

    data['id'] = json.get('query_value')
    data['text'] = json.get('display_value')
    data['link'] = json.get('url_path')

    return data

def products_crawler():
    pass
