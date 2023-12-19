import sqlite3
import psycopg2

# 连接到 SQLite 数据库文件
sqlite_connection = sqlite3.connect("book.db")
# sqlite_connection = sqlite3.connect("book_lx.db")
sqlite_cursor = sqlite_connection.cursor()

# 连接到 PostgreSQL 数据库
db_params = {
    'host': '127.0.0.1',
    'database': 'bookstore',
    'user': 'postgres',
    'password': '123456',
    'port': '5432'
}
postgres_connection = psycopg2.connect(**db_params)
postgres_cursor = postgres_connection.cursor()

# 从 SQLite 数据库中读取数据
sqlite_cursor.execute("SELECT * FROM book")
sqlite_data = sqlite_cursor.fetchall()

# 将数据插入到 MongoDB 集合中
for index,row in enumerate(sqlite_data):

    book_doc = {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "publisher": row[3],
        "original_title": row[4],
        "translator": row[5],
        "pub_year": row[6],
        "pages": row[7],
        "price": row[8],
        "currency_unit": row[9],
        "binding": row[10],
        "isbn": row[11],
        "author_intro": row[12],
        "book_intro": row[13],
        "content": row[14],
        "tags": row[15],
        "picture": row[16]
        # 如果有图书封面图片字段，需要根据实际情况添加
    }
    try:
        # 插入数据到 PostgreSQL 表中
        postgres_cursor.execute("""
            INSERT INTO book (
                id, title, author, publisher, original_title, translator, pub_year, 
                pages, price, currency_unit, binding, isbn, author_intro, book_intro, 
                content, tags, picture
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(book_doc.values()))
        # 提交更改
    except Exception as e:
        print(e)

# 提交更改
postgres_connection.commit()

# 关闭连接
postgres_cursor.close()
postgres_connection.close()