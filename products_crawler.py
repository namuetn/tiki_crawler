import json
import requests
import time
from requests.exceptions import ChunkedEncodingError
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
    collection = db["products"]
    if collection.count_documents({}) > 0:
         # Xóa tất cả các tài liệu trong bộ sưu tập
        collection.delete_many({})
        print(f"tài liệu đã được xóa.")

    collection.insert_many(data)

    client.close()

def create_file_csv(data):
    df = pd.DataFrame(data)

    # Tên tệp tin CSV
    csv_file = "product_v1.csv"

    # Lưu DataFrame thành tệp tin CSV
    df.to_csv(csv_file, index=False)

    print("Tạo tệp tin CSV thành công!")

def parser_product(json):
    data = {}

    data['id'] = json.get('id')
    data['name'] = json.get('name')
    data['short_description'] = json.get('short_description')
    data['url'] = json.get('url_path')
    data['rating'] = json.get('rating_average')
    data['price'] = json.get('price')
    data['category_id'] = json.get('primary_category_path')
    # data['quantity_sold'] = json.get('quantity_sold')

    return data

def products_crawler():
    categories = pd.read_csv('./categories_id_v1_1.csv')
    total_page = pd.read_csv('./total_page_v1_1.csv')
    zipper = zip(categories['Category ID'], total_page['Total Page'])

    product_result = []

    try:
        for category, pages in tqdm(zipper, total=len(categories['Category ID']), desc='Sản phẩm'):
            for page in range(1, pages + 1):
                params['category'] = category
                params['page'] = page
                try:
                    response = requests.get(url=url, headers=headers, params=params)
                    if response.status_code == 200:
                        products = response.json().get('data')
                        for product in products:
                            product_result.append(parser_product(product))
                    else:
                        print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)
                        print('# Đợi 1 giây và thử lại yêu cầu')
                        time.sleep(2)
                        print(params)
                        response = requests.get(url=url, headers=headers, params=params)
                        if response.status_code == 200:
                            print('trả kết quả sau khi load lại')
                            products = response.json().get('data')
                            for product in products:
                                product_result.append(parser_product(product))
                        else:
                            print('lỗi khi chạy lại')
                except ChunkedEncodingError:
                    print('request lại')
                    response = requests.get(url=url, headers=headers, params=params)
                except requests.exceptions.RequestException as e:
                    print('Lỗi kết nối:', str(e))

        print('Tiến hành tạo file csv')
        create_file_csv(product_result)
        print('Tiến hành lưu vào database')
        connect_database(product_result)

        print('Crawl thông tin sản phẩm thành công')
    except Exception as e:
        print('Tiến hành tạo file csv')
        create_file_csv(product_result)
        print(f'có lỗi xảy ra {e}')
        
products_crawler()

