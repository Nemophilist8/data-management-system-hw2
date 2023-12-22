import logging
import os
import psycopg2
import pymongo

class Store:
    database: str

    def __init__(self, host, port):
        # PostgreSQL 数据库连接参数
        self.db_params = {
            'host': '127.0.0.1',
            'database': 'bookstore',
            'user': 'postgres',
            'password': '123456',
            'port': '5432'
        }
        # 初始化 PostgreSQL 数据库表格
        self.init_tables()
        # 连接 MongoDB 数据库
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client["bookstore"]

    def init_tables(self):
        try:
            # 获取 PostgreSQL 数据库连接和游标
            conn = self.get_db_conn()
            cursor = conn.cursor()

            # 定义创建表格的 SQL 命令
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS book
                (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    publisher TEXT,
                    original_title TEXT,
                    translator TEXT,
                    pub_year TEXT,
                    pages INTEGER,
                    price INTEGER,
                    currency_unit TEXT,
                    binding TEXT,
                    isbn TEXT,
                    author_intro TEXT,
                    book_intro TEXT,
                    content TEXT,
                    tags TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "user"
                (
                    user_id TEXT PRIMARY KEY,
                    password TEXT,
                    balance INTEGER,
                    token TEXT,
                    terminal TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS user_store
                (
                    store_id TEXT PRIMARY KEY ,
                    user_id TEXT REFERENCES "user" (user_id)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS store
                (
                    store_id TEXT,
                    user_id TEXT REFERENCES "user" (user_id),
                    book_id TEXT REFERENCES book (id),
                    price INTEGER,
                    stock_level INTEGER,
                    PRIMARY KEY (store_id, book_id)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "order"
                (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT PRIMARY "user" (user_id),
                    store_id TEXT REFERENCES user_store (store_id),
                    status TEXT,
                    created_at TIMESTAMP,
                    shipped_at TIMESTAMP,
                    received_at TIMESTAMP,
                    paid_at TIMESTAMP,
                    cancelled_at TIMESTAMP,
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS order_detail
                (
                    order_id TEXT REFERENCES "order" (order_id),
                    book_id TEXT REFERENCES book (id),
                    count INTEGER,
                    price INTEGER 
                );
                """
            ]

            # 执行创建表格的 SQL 命令
            for command in sql_commands:
                cursor.execute(command)
            # 提交更改
            conn.commit()

        except psycopg2.Error as e:
            # 如果发生错误，记录错误信息并回滚更改
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):
        # 返回 PostgreSQL 数据库连接
        return psycopg2.connect(**self.db_params)

# 全局数据库实例
database_instance: Store = None

# 初始化数据库实例
def init_database(host, port):
    global database_instance
    database_instance = Store(host, port)

# 获取数据库连接
def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()

# 获取数据库实例
def get_db_conn1():
    global database_instance
    return database_instance
