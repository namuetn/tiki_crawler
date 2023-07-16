import requests
import time
import concurrent.futures
import pandas as pd
from tqdm import tqdm
import threading
from requests.exceptions import ChunkedEncodingError, RequestException
from pymongo import MongoClient

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

def crawl_product_detail(product_id):
    # print(products_id,11111111111)
    """Hàm con để thực hiện crawl thông tin chi tiết của sản phẩm"""
    # for product_id in tqdm(products_id, total=len(products_id), desc='Chi tiết sản phẩm'):
    max_retries = 3
    retries = 0
    success = False
    while retries < max_retries and not success:
        try:
            response = requests.get(url=url + str(product_id), headers=headers)
            if response.status_code == 200:
                product = response.json()
                # print(f'Worker {concurrent.futures.thread.get_ident()}: Crawl xong sản phẩm {product_id}')
                print(f'Worker {threading.current_thread().ident}: Crawl xong sản phẩm {product_id}')
                success = True

                if retries != 0:
                    print(f'Crawl {str(product_id)} lại thành công')
                else:
                    print(f'Crawl {str(product_id)} thành công')
                return parser_product(product)
            else:
                print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)
                print(url + str(product_id))
                retries += 1
                print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
                time.sleep(4)
                print(4234234)
        except ChunkedEncodingError:
            print('Error: Lỗi mã hóa')
            print(url + str(product_id))
            retries += 1
            print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
            time.sleep(4)
        except RequestException as e:
            print('Error: Lỗi kết nối:', str(e))
            print(url + str(product_id))
            retries += 1
            print(f'+ Thử lại yêu cầu ({retries}/{max_retries})')
            time.sleep(4)

def products_detail_crawler():
    products_id = pd.read_csv('./id_set_v1.csv')
    product_detail_result = []

    # try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Tách danh sách product_id thành 3 phần bằng nhau cho 3 luồng
        chunk_size = len(products_id.get('0')) // 3
        chunks = [products_id.get('0')[i:i+chunk_size] for i in range(0, len(products_id), chunk_size)]
        for chunk in chunks:
            # Thực hiện crawl thông tin sản phẩm cho từng chunk sử dụng ThreadPoolExecutor
            results = list(executor.map(crawl_product_detail, chunk))
            product_detail_result.extend(results)

    print('Tiến hành tạo file csv...')
    create_file_csv(product_detail_result, "product_detail_v1_1.csv")
    print('Tiến hành lưu vào database...')
    connect_database(product_detail_result)

    print('Crawl thông tin sản phẩm thành công')
    # except Exception as e:
    #     print('Tiến hành tạo file csv')
    #     create_file_csv(product_detail_result, "product_detail_v1_1.csv")
    #     print(f'Có lỗi xảy ra: {e}')

products_detail_crawler()
