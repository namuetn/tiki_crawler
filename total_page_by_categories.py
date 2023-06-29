import re
import requests
import pandas as pd
from tqdm import tqdm

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

def abc():
    print(len([28, 1, 6, 7, 11, 1, 16, 2, 22, 4, 3, 6, 14, 42, 7, 18, 4, 1, 5, 1, 7, 2, 3, 34, 15, 40, 22, 10, 10, 5, 14, 9, 3, 23, 5, 3, 10, 15, 3, 9, 31, 9, 25, 5, 4, 22, 9, 17, 4, 8, 29, 10, 1, 7, 6, 4, 50, 23, 50, 17, 50, 37, 8, 50, 13, 20, 15, 50, 1, 48, 50, 30, 10, 50, 50, 42, 50, 21, 3, 1, 50, 50, 50, 50, 50, 21, 3, 2, 14, 26, 21, 15, 21, 16, 5, 4, 4, 2, 50, 25, 10, 4, 3, 2, 11, 2, 15, 1, 5, 7, 4, 38, 26, 10, 50, 50, 10, 50, 13, 50, 15, 50, 5, 25, 13, 1, 20, 6, 50, 50, 1, 50, 43, 22, 18, 50, 1, 6, 50, 10, 50, 50, 29, 4, 35, 30, 17, 30, 19, 4, 1, 11, 1, 50, 34, 35, 30, 18, 9, 50, 28, 21, 3, 7, 1, 9, 30, 4, 28, 50, 50, 46, 4, 13, 50, 50, 1, 1, 50, 35, 37, 47, 44, 4, 22, 9, 6, 32, 8, 7, 10, 22, 18, 7, 9, 2, 2, 2, 7, 6, 5, 5, 5, 30, 35, 11, 6, 26, 9, 5, 18, 4, 17, 7, 17, 19, 1, 3, 18, 15, 12, 25, 7, 20, 3, 8, 5, 9, 17, 6, 31, 29, 3, 3, 14, 12, 9, 24, 2, 25, 22, 19, 7, 50, 50, 15, 23, 2, 5, 25, 27, 6, 17, 4, 20, 2, 16, 15, 3, 1, 8, 14, 15, 25, 8, 3, 9, 1, 43, 1, 50, 9, 12, 1, 31, 30, 32, 50, 9, 31, 50, 14, 35, 10, 1, 1, 1, 24, 17, 33, 1, 50, 16, 8, 21, 23, 13, 8, 18, 1, 18, 2, 17, 2, 9, 4, 17, 12, 1, 5, 4, 9, 4, 1, 31, 4, 4, 18, 4, 12, 11, 3, 17, 14, 8, 6, 1, 50, 
3, 1, 1, 50, 18, 6, 38, 9, 14, 2, 26, 7, 36, 15, 25, 34, 17, 50, 15, 13, 8, 50, 17, 6, 33, 26, 15, 7, 42, 17, 46, 10, 50, 1, 31, 29, 15, 1, 32, 29, 30, 50, 14, 6, 2, 25, 30, 21, 2, 3, 4, 38, 1, 36, 40, 13, 29, 20, 15, 4, 6, 4, 21, 8, 26, 15, 7, 12, 10, 38, 10, 17, 7, 37, 6, 25, 2, 8, 2, 1, 9, 5, 2, 5, 3, 9, 7, 2, 37, 17, 43, 14, 21, 8, 4, 9, 35, 1, 8, 1, 9, 8, 40, 13, 45, 26, 17, 21, 7, 
10, 25, 5, 22, 43, 7, 33, 20, 5, 5, 2, 21, 17, 4, 17, 10, 36, 4, 8, 2, 17, 20, 33, 16, 27, 16, 5, 15, 29, 8, 50, 5, 50, 50, 50, 50, 50, 50, 50, 50, 19, 50, 33, 2, 50, 50, 7, 7, 13, 6, 50, 50, 50, 50, 44, 50, 4, 50, 50, 50, 16, 50, 50, 50, 3, 47, 50, 50, 50, 32, 50, 3, 50, 10, 12, 12, 6, 9, 50, 50, 36, 3, 50, 45, 34, 50, 50, 50, 50, 50, 33, 50, 30, 36, 50, 36, 29, 8, 7, 13, 50, 50, 21, 34, 5, 50, 50, 20, 50, 9, 7, 50, 48, 34, 16, 6, 22, 1, 50, 23, 46, 50, 21, 50, 41, 33, 50, 5, 27, 42, 50, 16, 32, 34, 39, 50, 9, 42, 50, 8, 50, 14, 43, 3, 2, 8, 11, 40, 2, 30, 50, 35, 32, 14, 27, 19, 30, 46, 21, 50, 20, 50, 46, 50, 21, 50, 23, 11, 50, 9, 27, 50, 33, 11, 38, 50, 4, 19, 7, 31, 34, 50, 9, 50, 48, 47, 50, 39, 6, 50, 23, 20, 50, 17, 1, 21, 5, 1, 38, 8, 3, 50, 50, 50, 50, 50, 50, 50, 25, 11, 49, 50, 39, 50, 50, 49, 50, 50, 50, 28, 4, 14, 50, 16, 49, 1, 50, 49, 16, 40, 46, 4, 4, 4, 8, 9, 50, 8, 6, 50, 50, 26, 8, 43, 50, 17, 50, 13, 13, 7, 50, 50, 50, 50, 50, 20, 45, 11, 
27, 49, 5, 2, 37, 11, 13, 2, 19, 1, 5, 3, 28, 50, 20, 4, 7, 12, 41, 5, 1, 3, 1, 1, 10, 6, 12, 7, 6, 18, 7, 7, 13, 1, 1, 1, 3, 13, 50, 50, 50, 2, 16, 1, 1, 50, 50, 50, 50, 46, 50, 50, 21, 50, 25, 
50, 50, 15, 36, 50, 50, 50, 50, 40, 36, 40, 50, 50, 50, 49, 1, 50, 50, 31, 1, 50, 50, 50, 50, 50, 50, 50, 50, 7, 34, 19, 26, 50, 43, 50, 50, 50, 50, 29, 35, 50, 23, 38, 24, 50, 50, 50, 50, 50, 50, 5, 50, 47, 50, 50, 9, 50, 46, 3, 10, 50, 50, 8, 50, 50, 9, 25, 10, 6, 7, 50, 32, 47, 3, 50, 50, 40, 14, 50, 50, 50, 50, 50, 1, 50, 50, 50, 50, 50, 50, 50, 50, 25, 50, 33, 19, 34, 50, 1, 50, 50, 50, 11, 27, 50, 17, 50, 50, 6, 14, 17, 50, 27, 50, 38, 46, 50, 24, 5, 19, 50, 50, 50, 50, 50, 49, 50, 50, 32, 31, 50, 14, 50, 50, 50, 50, 15, 2, 42, 50, 38, 15, 13, 50, 5, 5, 12, 43, 43, 4, 3, 4, 18, 25, 8, 14, 26, 10, 50, 50, 50, 50, 50, 19, 1, 50, 1, 3, 1, 1, 2, 1, 12, 42, 1, 25, 50, 25, 50, 26, 2, 3, 14, 50, 21, 50, 18, 7, 11, 5, 4, 18, 9, 23, 19, 12, 50, 50, 11, 47, 2, 50, 1, 2, 1, 
1, 1, 50, 2, 22, 1, 50, 50, 27, 15, 1, 1, 1, 17, 16, 1, 1, 23, 50, 50, 10, 3, 50, 2, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 20, 50, 50, 2, 2, 50, 40, 50, 29, 2, 16, 50, 1, 1, 1, 4, 3, 17, 3, 1, 
9, 1, 3, 2, 2, 1, 6, 6, 30, 7, 3, 50, 50, 50, 50, 50, 50, 50, 50, 50, 28, 50, 50, 50, 1, 50, 36, 50, 50, 4, 50, 50, 50, 4, 50, 50, 50, 50, 11, 1, 50, 1, 42, 50, 50, 50, 23, 3, 50, 50, 50, 50, 50, 5, 22, 50, 50, 50, 50, 50, 50, 44, 20, 1, 22, 50, 16, 5, 50, 50, 50, 33, 29, 50, 50, 18, 29, 50, 50, 32, 8, 29, 31, 34, 18, 11, 9, 2, 1, 6, 14, 23, 50, 10, 27, 7, 5, 13, 50, 10, 5, 16, 34, 11, 44, 14, 3, 37, 10, 11, 8, 16, 42, 38, 22, 50, 50, 50, 16, 19, 24, 47, 24, 41, 21, 8, 6, 20, 21, 8, 22, 50, 50, 50, 41, 7, 50, 44, 40, 11, 9, 5, 6, 26, 34, 2, 42, 2, 5, 23, 5, 33, 7, 12, 50, 4, 27, 8, 25, 8, 46, 5, 9, 50, 6, 27, 9, 9, 7, 4, 2, 43, 7, 7, 20, 10, 1, 3, 17, 2, 41, 27, 1, 33, 20, 50, 1, 25, 7, 16, 32, 28, 13, 50, 1, 8, 9, 18, 5, 23, 50, 13, 17, 15, 27, 13, 27, 40, 14, 14, 12, 
22, 50, 3, 40, 10, 50, 30, 50, 32, 50, 50, 50, 50, 50, 50, 50, 50, 2, 50, 50, 50, 50, 46, 9, 5, 48, 18, 6, 1, 50, 50, 22, 5, 9, 14, 44, 21, 2, 9, 38, 33, 8, 4, 2, 1, 19, 12, 37, 9, 6, 15, 2, 21, 
16, 28, 5, 11, 27, 12, 3, 1, 6, 42, 30, 3, 21, 20, 29, 1, 1, 27, 34, 34, 49, 7, 3, 50, 16, 48, 17, 25, 21, 4, 50, 14, 16, 50, 3, 20, 15, 6, 5, 50, 2, 10, 13, 5, 7, 4, 45, 3, 50, 50, 40, 50, 40, 15, 7, 50, 6, 50, 50, 3, 50, 16, 20, 50, 42, 12, 8, 17, 25, 32, 8, 7, 18, 19, 3, 1, 1, 1, 6, 4, 6, 3, 3, 12, 39, 16, 19, 42, 21, 5, 8, 30, 1, 25, 50, 5, 15, 5, 4, 11, 11, 1, 4, 1, 4, 10, 1, 10, 2, 1, 1, 43, 1, 12, 20, 48, 35, 50, 50, 47, 4, 13, 50, 17, 31, 12, 8, 50, 20, 26, 50, 22, 50, 50, 17, 8, 5, 50, 15, 36, 3, 16, 50, 31, 50, 3, 2, 50, 27, 30, 42, 50, 50, 50, 11, 8, 47, 50, 50, 50, 25, 50, 50, 50, 50, 50, 50, 50, 6, 50, 50, 11, 13, 8, 6, 45, 50, 23, 23, 48, 26, 50, 50, 50, 26, 13, 32, 50, 42, 15, 33, 26, 31, 50, 42, 50, 39, 23, 3, 6, 28, 26, 50, 41, 30, 11, 37, 10, 18, 4, 17, 50, 38, 28, 23, 50, 44, 28, 27, 12, 1, 12, 3, 9, 11, 50, 31, 34, 50, 23, 6, 11, 19, 1, 4, 50, 13, 2, 1, 12, 6, 42, 43, 21, 11, 9, 1, 43, 10, 22, 22, 43, 18, 8, 8, 34, 7, 25, 8, 14, 50, 15, 50, 
13, 50, 31, 30, 50, 50, 24, 5, 50, 42, 50, 1, 4, 3, 50, 50, 9, 27, 49, 24, 4, 11, 25, 13, 32, 17, 2, 7, 34, 1, 28, 50, 32, 18, 3, 13, 28, 32, 6, 2, 12, 6, 3, 16, 28, 16, 2, 1, 9, 4, 1, 25, 16, 7, 9, 3, 3, 10, 38, 40, 7, 26, 6, 10, 2, 6, 17, 3, 18, 35, 26, 16, 8, 46, 20, 4, 7, 36, 21, 3, 50, 9, 2, 3, 2, 2, 3, 9, 50, 43, 50, 7, 5, 1, 1, 1, 4, 50, 50, 1, 10, 2, 1, 1, 1, 5, 3, 50, 32, 15, 7, 21, 2, 13, 47, 10, 50, 50, 50, 50, 50, 50, 13, 4, 2, 2, 9, 19, 40, 22, 12, 16, 50, 11, 1, 4, 2, 3, 26, 7, 42, 6, 5, 5, 3, 30, 16, 7, 17, 7, 3, 25, 16, 2, 36, 3, 7, 1, 1, 3, 4, 4, 2, 1, 5, 4, 25, 6, 1, 1, 3, 50, 14, 16, 9, 15]))

def total_page_crawler():
    total_page_list = []
    categories_id = pd.read_csv('./categories_id_v1_1.csv')

    print('Processing: Tiến hành lấy thông tin page cho tất cả danh mục...')
    for categories_id in tqdm(categories_id['Category ID'], total=len(categories_id['Category ID']), desc='Danh mục con 2'):
        params['category'] = categories_id
        response = requests.get(url=url, headers=headers, params=params)
        if response.status_code == 200:
            paging = response.json().get('paging').get('last_page')   
            total_page_list.append(paging)       
        else:
            print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

            return None
    print(total_page_list)
    df = pd.DataFrame(total_page_list, columns=['Total Page'])
    df.to_csv('total_page_v1_1.csv')
    print(f"File created successfully.")

total_page_crawler()
