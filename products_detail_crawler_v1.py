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

# params = {
#     'limit': 40,
#     'include': 'advertisement',
#     'aggregations': 2,
#     'trackity_id': '6d8dc609-cca9-32c5-29cc-b1cbfecfc236',
#     # 'category': 2549,
#     # 'page': 1,
# }

def connect_database(data):
    client = MongoClient("mongodb://localhost:27017")
    db = client["tiki_database"]
    collection = db["products_detail"]
    if collection.count_documents({}) > 0:
         # Xóa tất cả các tài liệu trong bộ sưu tập
        collection.delete_many({})
        print(f"tài liệu đã được xóa.")

    collection.insert_many(data)

    client.close()

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
    max_retries = 3
    retries = 0
    success = False
    while retries < max_retries and not success:
        try:
            response = requests.get(url=url + str(product_id), headers=headers)
            if response.status_code == 200:
                product = response.json()
                parser_result = parser_product(product)
                success = True
                if retries != 0:
                    print('Crawl lại thành công.')
                else:
                    print(f'Thành công: {url + str(product_id)}')
            
                return product_id if parser_result else None
            else:
                print(f'Error: {url + str(product_id)}. Mã trạng thái: {response.status_code}')
                retries += 1
                print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
                time.sleep(4)
        except ChunkedEncodingError:
            print(f'Error: Lỗi mã hóa của {url + str(product_id)}')
            retries += 1
            print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
            time.sleep(4)
        except RequestException as e:
            print(f'Error: Lỗi kết nối của {url + str(product_id)}:{str(e)}')
            retries += 1
            print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
            time.sleep(4)

def products_detail_crawler():
    products_id = pd.read_csv('./products-200001-400000-test.csv')
    product_detail_result = []
    try:
        pool = multiprocessing.Pool(processes=3)
        results = []
        with tqdm(total=len(products_id.get('id')), desc='Chi tiết sản phẩm', unit=' requests') as pbar:
            for product_id in products_id.get('id'):
                result = pool.apply_async(process_product, args=(product_id,))
                results.append(result)
                print(result.get())

            # Chờ tất cả các tiến trình con hoàn thành
            pool.close()
            pool.join()

            # Lấy kết quả từ các tiến trình con
            for result in results:
                product_id = result.get()
                if product_id is not None:
                    product_detail_result.append(product_id)
                    pbar.update(1)

        print('Tiến hành tạo file csv...')
        create_file_csv(product_detail_result, "product_detail_v1_1.csv")
        print('Tiến hành lưu vào database...')
        connect_database(product_detail_result)

        print('Crawl thông tin sản phẩm thành công')
    except Exception as e:
        print('Tiến hành tạo file csv')
        create_file_csv(product_detail_result, "product_detail_v1_1.csv")
        print(f'Có lỗi xảy ra: {e}')

if __name__ == '__main__':
    freeze_support()
    products_detail_crawler()
