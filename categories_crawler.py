import requests
import pandas as pd
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

def categories_crawler(parent_categories_result, categories_list_id):
    print('Processing: Tiến hành lấy danh mục...')

    count_categories_result = 0
    count_sub_categories_result = 0
    count_sub_sub_categories_result = 0
    count_sub_sub_sub_categories_result = 0

    remove_once_1 = False
    remove_once_2 = False
    remove_once_3 = False
    remove_once_4 = False

    for parent_category_result in tqdm(parent_categories_result['parent_categories'], total=len(parent_categories_result['parent_categories']), desc='Danh mục'):
        parent_category_result['categories'] = []
        params['category'] = parent_category_result.get('id')
        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            categories_list = response.json().get('filters')[0].get('values')
            paging = response.json().get('paging')
            count_categories_result = count_categories_result + len(categories_list)

            for category in categories_list:
                if category.get('url_path') and paging.get('total') == 2000:
                    result = parser_categories(category)
                    parent_category_result['categories'].append(result)
                    if not remove_once_1:
                        categories_list_id.remove(parent_category_result.get('id'))
                        remove_once_1 = True
                    categories_list_id.append(result.get('id'))
        else:
            print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

            return None

        for category_result in tqdm(parent_category_result['categories'], total=len(parent_category_result['categories']), desc='Danh mục con'):
            category_result['sub_categories'] = []
            params['category'] = category_result.get('id')
            response = requests.get(url=url, headers=headers, params=params)

            if response.status_code == 200:
                categories_list = response.json().get('filters')[0].get('values')
                paging = response.json().get('paging')
                count_sub_categories_result = count_sub_categories_result + len(categories_list)

                for category in categories_list:
                    if category.get('url_path') and paging.get('total') == 2000:
                        result = parser_categories(category)
                        category_result['sub_categories'].append(result)
                        if not remove_once_2:
                            categories_list_id.remove(category_result.get('id'))
                            remove_once_2 = True
                        categories_list_id.append(result.get('id'))
            else:
                print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

                return None

            for sub_category_result in tqdm(category_result['sub_categories'], total=len(category_result['sub_categories']), desc='Danh mục con 2'):
                sub_category_result['sub_sub_categories'] = []
                params['category'] = sub_category_result.get('id')
                response = requests.get(url=url, headers=headers, params=params)

                if response.status_code == 200:
                    categories_list = response.json().get('filters')[0].get('values')
                    paging = response.json().get('paging')
                    count_sub_sub_categories_result = count_sub_sub_categories_result + len(categories_list)

                    for category in categories_list:
                        if category.get('url_path') and paging.get('total') == 2000:
                            result = parser_categories(category)
                            sub_category_result['sub_sub_categories'].append(result)
                            if not remove_once_3:
                                categories_list_id.remove(sub_category_result.get('id'))
                                remove_once_3 = True
                            categories_list_id.append(result.get('id'))
                else:
                    print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

                    return None
                
                for sub_sub_category_result in tqdm(sub_category_result['sub_sub_categories'], total=len(sub_category_result['sub_sub_categories']), desc='Danh mục con 3'):
                    sub_sub_category_result['sub_sub_sub_categories'] = []
                    params['category'] = sub_sub_category_result.get('id')
                    response = requests.get(url=url, headers=headers, params=params)

                    if response.status_code == 200:
                        categories_list = response.json().get('filters')[0].get('values')
                        paging = response.json().get('paging')
                        count_sub_sub_sub_categories_result = count_sub_sub_sub_categories_result + len(categories_list)

                        for category in categories_list:
                            if category.get('url_path') and paging.get('total') == 2000:
                                result = parser_categories(category)
                                sub_sub_category_result['sub_sub_sub_categories'].append(result)
                                if not remove_once_4:
                                    categories_list_id.remove(sub_sub_category_result.get('id'))
                                    remove_once_4 = True
                                categories_list_id.append(result.get('id'))
                    else:
                        print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

                        return None
    
    # return categories_list_id
            
    print('- Số lượng danh mục: ', count_categories_result)
    print('- Số lượng danh mục phụ: ', count_sub_categories_result)
    print('- Số lượng danh mục phụ 2: ', count_sub_sub_categories_result)
    print('- Số lượng danh mục phụ 3: ', count_sub_sub_sub_categories_result)

    return [parent_categories_result, categories_list_id]

def crawler():
    result = parent_categories_crawler()
    parent_categories_result = result[0]
    parent_categories_list_id = result[1]

    categories_result = categories_crawler(parent_categories_result, parent_categories_list_id)
    print('Success: Crawl thông tin danh mục con thành công')
    connect_database(categories_result[0])

    df = pd.DataFrame(categories_result[1], columns=['Category ID'])
    df.to_csv('categories_id.csv')
    print(f"File created successfully.")
    return categories_result

crawler()
