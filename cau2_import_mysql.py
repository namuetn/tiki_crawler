from pymongo import MongoClient
import mysql.connector
from tqdm import tqdm


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
    cursor.execute("CREATE DATABASE IF NOT EXISTS tiki_database")
    cursor.execute("USE tiki_database")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY AUTO INCREMENT
            product_id INT,
            name VARCHAR(1000),
            short_description TEXT,
            description MEDIUMTEXT,
            short_url VARCHAR(1000),
            price DECIMAL(20, 5)
        )
    """)
    
    cursor.execute('SET GLOBAL interactive_timeout=28800')
    cursor.execute('SET GLOBAL wait_timeout=28800')
    cursor.execute('SET GLOBAL binlog_format = "ROW"')
    cursor.execute('SET GLOBAL binlog_error_action=ABORT_SERVER')
    cursor.execute('SET GLOBAL max_allowed_packet=67108864')

    sql = "INSERT INTO products (id, name, short_description, description, short_url, price) VALUES (%s, %s, %s, %s, %s, %s)"
    print('Bắt đàu import')
    values = [(item.get('id', ''), item.get('name', ''), item.get('short_description', ''), item.get('description', ''), item.get('short_url', ''), item.get('price', None)) for item in tqdm(data)]
    print('Chuẩn bị lưu vào mysql')

    chunk_size = 3000  # Số lượng dòng dữ liệu chèn mỗi lần
    chunks = [values[i:i+chunk_size] for i in range(0, len(values), chunk_size)]

    for chunk in chunks:
        cursor.executemany(sql, chunk)
        print('Lưu vào db thành công 3000 sp')
        db.commit()

    # cursor.executemany(sql, values)

    # db.commit()
    db.close()

def main():
    projection = {
        '_id': 0,
        'id': 1,
        'name': 1,
        'short_description': 1,
        'description': 1, 
        'name': 1,
        'short_url': 1,
        'price': 1,
    }

    data = get_collection().find({}, projection)
    import_to_mysql(data)


if __name__ == '__main__':
    main()
