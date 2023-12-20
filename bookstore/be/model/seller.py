import psycopg2
from model import error
from model import db_conn
import json
from datetime import datetime

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        cursor = None
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            book_data = json.loads(book_json_str)
            price = book_data['price']
            cursor = self.conn.cursor()

            if not self.book_id_exist_in_all(book_data['id']):
                cursor.execute(
                    "INSERT INTO book (id, title, author, publisher, original_title, translator, pub_year,\
                                       pages, price, currency_unit, binding, isbn, author_intro, book_intro,\
                                       content, tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (book_data['id'], book_data['title'], book_data['author'], book_data['publisher'],book_data['original_title'], book_data['translator'], book_data['pub_year'],
                     book_data['pages'],book_data['price'], book_data['currency_unit'], book_data['binding'], book_data['isbn'],book_data['author_intro'], book_data['book_intro'],
                     book_data['content'], book_data['tags']),
                )
                self.conn.commit()

            cursor.execute(
                "INSERT INTO store (store_id, book_id, price, stock_level) VALUES (%s, %s, %s, %s)",
                (store_id, book_id, price, stock_level),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        cursor = None
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE store SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s",
                (add_stock_level, store_id, book_id),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        cursor = None
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT into user_store(store_id, user_id) VALUES (%s, %s)",
                (store_id, user_id),
            )
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT store_id, status from \"order\" where order_id=%s", (order_id,)
            )

            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            if row[0] != store_id:
                return error.error_authorization_fail()

            status = row[1]
            if status == 'shipped':
                return 200, "Order is already shipped."
            if status != "paid":
                return error.error_status_fail(order_id)

            cursor.execute(
                "UPDATE \"order\" SET status = %s, received_at = %s WHERE order_id = %s",
                ('shipped', datetime.now().isoformat(), order_id),
            )

            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def get_seller_orders(self, user_id: str) -> (int, str, list):
        cursor = None
        seller_orders = []
        try:

            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT store_id from user_store where user_id=%s", (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return error.error_authorization_fail()
            store_id = row[0]


            cursor.execute(
                "SELECT store_id, order_id, status from \"order\" where store_id=%s", (store_id,)
            )
            rows = cursor.fetchall()
            if len(rows) == 0:
                return error.error_authorization_fail()

            for row in rows:
                seller_orders.append(
                    {'store_id': row[0],
                     'order_id': row[1],
                     'status': row[2]}
                )

            self.conn.commit()

        except psycopg2.Error as e:
            return 528, "{}".format(str(e)), seller_orders
        except BaseException as e:
            return 530, "{}".format(str(e)), seller_orders
        finally:
            if cursor:
                cursor.close()
        return 200, "ok", seller_orders
