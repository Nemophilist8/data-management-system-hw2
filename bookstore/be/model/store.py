import logging
import os
import psycopg2


class Store:
    database: str

    def __init__(self):
        self.db_params = {
            'host': '127.0.0.1',
            'database': 'bookstore',
            'user': 'postgres',
            'password': '123456',
            'port': '5432'
        }
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cursor =  conn.cursor()
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
                    tags TEXT,
                    picture BYTEA
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
                    store_id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES "user" (user_id)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS store
                (
                    store_id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES "user" (user_id),
                    book_id TEXT REFERENCES book (id),
                    price INTEGER,
                    stock_level INTEGER 
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS "order"
                (
                    order_id TEXT PRIMARY KEY,
                    book_id TEXT REFERENCES book (id),
                    store_id TEXT REFERENCES user_store (store_id)
                    status TEXT,
                    created_at TIMESTAMP,
                    shipped_at TIMESTAMP,
                    received_at TIMESTAMP
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
            for command in sql_commands:
                cursor.execute(command)
            conn.commit()

        except psycopg2.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self):
        return psycopg2.connect(**self.db_params)


database_instance = Store()


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
