import json
import requests
import time
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import RequestException
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

def create_file_csv(data, file_path):
    df = pd.DataFrame(data)

    # Lưu DataFrame thành tệp tin CSV
    df.to_csv(file_path, index=False)

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
                max_retries = 3
                retries = 0
                success = False
                while retries < max_retries and not success:
                    try:
                        response = requests.get(url=url, headers=headers, params=params)
                        if response.status_code == 200:
                            products = response.json().get('data')
                            for product in products:
                                product_result.append(parser_product(product))
                            success = True
                        else:
                            print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)
                            retries += 1
                            print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
                            time.sleep(4)
                    except ChunkedEncodingError:
                        print('Error: Lỗi mã hóa')
                        retries += 1
                        print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
                        time.sleep(4)
                    except RequestException as e:
                        print('Error: Lỗi kết nối:', str(e))
                        retries += 1
                        print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
                        time.sleep(4)

        unique_products = []
        id_set = set()

        print('Tiến hành loại bỏ product trùng lặp...')
        for product in product_result:
            product_id = product['id']
            if product_id not in id_set:
                unique_products.append(product)
                id_set.add(product_id)

        print('Tiến hành tạo file csv...')
        create_file_csv(unique_products, "product_v1_1.csv")
        print('Tiến hành lưu vào database...')
        connect_database(unique_products)
        create_file_csv(id_set, "id_set_v1.csv")

        print('Crawl thông tin sản phẩm thành công')
    except Exception as e:
        print('Tiến hành tạo file csv')
        create_file_csv(product_result, "product_v1_1.csv")
        print(f'Có lỗi xảy ra: {e}')
        
products_crawler()

