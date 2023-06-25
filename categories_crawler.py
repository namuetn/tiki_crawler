import requests
from tqdm import tqdm
from pymongo import MongoClient
from parent_categories_crawler import parent_categories_crawler

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
    'page': 1,
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

def categories_crawler(parent_categories_result):
    print('Processing: Tiến hành lấy danh mục...')

    count_categories_result = 0
    count_sub_categories_result = 0

    for parent_category_result in tqdm(parent_categories_result['parent_categories'], total=len(parent_categories_result['parent_categories'])):
        parent_category_result['categories'] = []
        params['category'] = parent_category_result.get('id')
        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            categories_list = response.json().get('filters')[0].get('values')
            count_categories_result = count_categories_result + len(categories_list)

            for category in categories_list:
                if category.get('url_path'):
                    parent_category_result['categories'].append(parser_categories(category))
        else:
            print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.data)

            return None

        for category_result in tqdm(parent_category_result['categories'], total=len(parent_category_result['categories'])):
            category_result['sub_categories'] = []
            params['category'] = category_result.get('id')
            response = requests.get(url=url, headers=headers, params=params)

            if response.status_code == 200:
                categories_list = response.json().get('filters')[0].get('values')
                count_sub_categories_result = count_sub_categories_result + len(categories_list)

                for category in categories_list:
                    if category.get('url_path'):
                        category_result['sub_categories'].append(parser_categories(category))
            else:
                print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.data)

                return None
            
    print('- Số lượng danh mục: ', count_categories_result)
    print('- Số lượng danh mục phụ: ', count_sub_categories_result)

    return parent_categories_result

def crawler():
    categories_result = parent_categories_crawler()

    categories_result = categories_crawler(categories_result)
    print('Success: Crawl thông tin danh mục con thành công')
    connect_database(categories_result)

    return categories_result

crawler()
