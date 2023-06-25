import re
import requests

url = 'https://api.tiki.vn/raiden/v2/menu-config'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,fa;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://tiki.vn/',
    'x-guest-token': 'LoFf91qsdKhymIYliWuc7Ha6VTXeDk2n',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

params = {
    'platform': 'desktop'
}

response = requests.get(url=url, headers=headers, params=params)

def parser_parent_categories(json, id):
    data = dict()
    data['id'] = id
    data['text'] = json.get('text')
    data['link'] = json.get('link')
    
    return data

def parent_categories_crawler():
    parent_categories_result = {
        'parent_categories': []
    }
    print('Processing: Tiến hành lấy thông tin danh mục cha...')
    if response.status_code == 200:
        parent_categories_list = response.json().get('menu_block').get('items')
        for category in parent_categories_list:
            id = re.findall(r'\d+', category.get('link'))[-1]
            parent_categories_result['parent_categories'].append(parser_parent_categories(category, id))
        
        print('- Số lượng danh mục cha: ', len(parent_categories_result['parent_categories']))
        print('Success: Crawl thông tin danh mục cha thành công')

        return parent_categories_result
    else:
        print('Error: Yêu cầu GET không thành công. Mã trạng thái:', response.status_code)

        return None
