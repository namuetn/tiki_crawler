from pymongo import MongoClient
from bs4 import BeautifulSoup
import mysql.connector
from tqdm import tqdm
import re

def get_collection():
    client = MongoClient("mongodb://localhost:27017")
    db = client["tiki"]
    collection = db["products"]

    return collection

def import_to_mysql(data):
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456789',
        # connect_timeout=600
        # database='tiki_database'
    )

    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS tiki_ingredients")
    cursor.execute("USE tiki_ingredients")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            product_id INT,
            ingredients TEXT
        )
    """)
    
    cursor.execute('SET GLOBAL interactive_timeout=28800')
    cursor.execute('SET GLOBAL wait_timeout=28800')
    cursor.execute('SET GLOBAL binlog_format = "ROW"')
    cursor.execute('SET GLOBAL binlog_error_action=ABORT_SERVER')
    cursor.execute('SET GLOBAL max_allowed_packet=67108864')

    sql = "INSERT INTO products (product_id, ingredients) VALUES (%s, %s)"
    print('Bắt đàu import')
    values = [(item.get('id', ''), item.get('ingredients', '')) for item in tqdm(data)]
    print('Chuẩn bị lưu vào mysql')

    chunk_size = 3000  # Số lượng dòng dữ liệu chèn mỗi lần
    chunks = [values[i:i+chunk_size] for i in range(0, len(values), chunk_size)]

    for chunk in chunks:
        cursor.executemany(sql, chunk)
        print('Lưu vào db thành công 3000 sp')
        db.commit()

    db.close()

def main():
    projection = {
        '_id': 0,
        'id': 1,
        'short_url': 1,
        'description': 1,
        'specifications': 1,
    }

    # pattern = re.compile(r'thành phần', re.IGNORECASE)
    data = get_collection().find({}, projection)
    # data = data[0:100]
    results = []

    for item in tqdm(data):
        # print(item.get('id'), ' ', item.get('short_url'))
        if 'specifications' in item and len(item['specifications']) > 0:
            specifications = item['specifications'][0]['attributes']
            for attributes in specifications:
                if attributes['code'] == 'ingredients':
                    results.append({'id': item['id'], 'ingredients': attributes['value']})
                    # print({'id': item['id'], 'ingredients': attributes['value']})
        # elif 'description' in item:
        #     description = item['description']
        #     soup = BeautifulSoup(description, 'html.parser')
        #     # elements = soup.find('strong', text='Thành phần')
        #     elements = soup.find_all(string=pattern)
        #     if elements:
        #         print(item.get('short_url'))
        #         print(elements)
            #     # Lấy tất cả văn bản bên dưới thẻ strong '2. Thành phần'
            #     text_below_strong = elements.find_next_siblings(text=True)
                
            #     # Gộp các đoạn văn bản thành một chuỗi
            #     result = ''.join(text_below_strong)
                
            #     # Loại bỏ khoảng trắng thừa và ký tự xuống dòng
            #     result = result.strip()
                
            #     # In kết quả
            #     print(result)
            # # print(elements)
            # for element in elements:
            #     text = element.get_text()
            #     results.append(text)
    import_to_mysql(results)


main()
