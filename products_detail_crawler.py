import json
import os
import csv
import requests
import time
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
# from parent_categories_crawler import parent_categories_crawler

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

client = MongoClient("mongodb://localhost:27017")
db = client["tiki_database"]
collection = db["products_detail"]

if collection.count_documents({}) > 0:
    collection.delete_many({})
    print(f"tài liệu đã được xóa.")

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

def crawl_product_details(product_id):
    product_false = []
    try:
        response = requests.get(url + str(product_id), headers=headers)
        if response.status_code == 200:
            product = response.json()
            return parser_product(product)
        else:
            print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)
            print(product_id)
            product_false.append(product_id)
            time.sleep(4)
    except requests.exceptions.ChunkedEncodingError as e:
        print('Error: Lỗi mã hóa', str(e))
        print(product_id)
        product_false.append(product_id)
        time.sleep(4)
    except RequestException as e:
        print('Error: Lỗi kết nối:', str(e))
        print(product_id)
        product_false.append(product_id)
        time.sleep(4)

    return product_false

def products_detail_crawler():
    products_id = pd.read_csv('./products-200001-400000.csv')
    product_detail_result = []
    product_false = []

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for i, product_id in enumerate(tqdm(products_id.get('id'), total=len(products_id.get('id')), desc='Chi tiết sản phẩm')):
                future = executor.submit(crawl_product_details, product_id)
                product_result = future.result()
                if isinstance(product_result, list):
                    product_false += product_result
                else:
                    product_detail_result.append(product_result)
            
                if (i + 1) % 100 == 0:  # Chèn vào MongoDB sau mỗi 1000 sản phẩm
                    collection.insert_many(product_detail_result)
                    print("Lưu thành công", len(product_detail_result), "sản phẩm vào Tiki.")
                    product_detail_result = []  # Reset danh sách sản phẩm
                    
                    # Ghi danh sách product_false vào file CSV
                    if len(product_false) > 0:
                        file_exists = os.path.isfile('product_false.csv')
                        mode = 'a' if file_exists else 'w'

                        with open('product_false.csv', mode, newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            if not file_exists:  # Ghi header nếu file chưa tồn tại
                                writer.writerow(["ID"])

                            for item in product_false:
                                writer.writerow([item])
                        product_false = []  # Reset danh sách product_false
        
            # Lưu các sản phẩm còn lại (số lượng không đạt đến 1000)
            if len(product_detail_result) > 0:
                collection.insert_many(product_detail_result)
                print("Lưu thành công", len(product_detail_result), "sản phẩm vào Tiki.")
            
            # Ghi danh sách product_false vào file CSV (nếu còn)
            if len(product_false) > 0:
                file_exists = os.path.isfile('product_false.csv')
                mode = 'a' if file_exists else 'w'

                with open('product_false.csv', mode, newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    if not file_exists:  # Ghi header nếu file chưa tồn tại
                        writer.writerow(["ID"])

                    for item in product_false:
                        writer.writerow([item])

        print('Tiến hành tạo file csv...')
        create_file_csv(product_detail_result, "product_detail_v1_1.csv")

        print('Crawl thông tin sản phẩm thành công')
    except Exception as e:
        print('Tiến hành tạo file csv')
        create_file_csv(product_detail_result, "product_detail_v1_1.csv")
        print(f'Có lỗi xảy ra: {e}')

products_detail_crawler()

