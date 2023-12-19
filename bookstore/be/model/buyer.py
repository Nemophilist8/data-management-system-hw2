from datetime import datetime

import psycopg2
import uuid
import json
import logging
from model import db_conn
from model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        cursor = None
        prices=[]
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            for book_id, count in id_and_count:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT book_id, stock_level, price FROM store "
                    "WHERE store_id = %s AND book_id = %s;",
                    (store_id, book_id),
                )
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                price = row[2]
                prices.append(price)

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor.execute(
                    "UPDATE store set stock_level = stock_level - %s "
                    "WHERE store_id = %s and book_id = %s and stock_level >= %s; ",
                    (count, store_id, book_id, count),
                )
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
            cursor.execute(
                "INSERT INTO \"order\"(order_id, store_id, user_id, status, created_at) "
                "VALUES(%s, %s, %s, %s, %s);",
                (uid, store_id, user_id, 'unpaid', datetime.now().isoformat()),
            )
            for index,(book_id, count) in enumerate(id_and_count):

                cursor.execute(
                    "INSERT INTO order_detail(order_id, book_id, count, price) "
                    "VALUES(%s, %s, %s, %s);",
                    (uid, book_id, count, prices[index]),
                )

            self.conn.commit()
            order_id = uid
        except psycopg2.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        finally:
            if cursor:
                cursor.close()
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id, user_id, store_id, status FROM \"order\" WHERE order_id = %s",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            status = row[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if status == 'paid' or status == 'shipped':
                return error.error_status_fail(order_id)

            cursor.execute(
                "SELECT balance, password FROM \"user\" WHERE user_id = %s;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "SELECT book_id, count, price FROM order_detail WHERE order_id = %s;",
                (order_id,),
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE \"user\" set balance = balance - %s WHERE user_id = %s AND balance >= %s",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            # cursor.execute(
            #     "UPDATE \"user\" set balance = balance + %s WHERE user_id = %s",
            #     (total_price, buyer_id),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_non_exist_user_id(buyer_id)

            cursor.execute(
                "UPDATE \"order\" SET status = %s, paid_at = %s WHERE order_id = %s",
                ('paid', datetime.now().isoformat(), order_id),
            )

            conn.commit()

        except psycopg2.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_id, status from \"order\" where order_id=%s", (order_id,)
            )

            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            if row[0] != user_id:
                return error.error_authorization_fail()

            status = row[1]
            if status == 'received':
                return 200, "Order is already received"
            if status != "shipped":
                return error.error_status_fail(order_id)

            cursor.execute(
                "UPDATE \"order\" SET status = %s, received_at = %s WHERE order_id = %s",
                ('received', datetime.now().isoformat(), order_id),
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

    def add_funds(self, user_id, password, add_value) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password from \"user\" where user_id=%s", (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor.execute(
                "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                (add_value, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_id, status from \"order\" where order_id=%s", (order_id,)
            )

            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            if row[0] != user_id:
                return error.error_authorization_fail()

            status = row[1]
            if status == "shipped" or status == "received":
                return error.error_status_fail(order_id)

            elif status == "cancelled":
                return 200, "Order is already cancelled."

            elif status == "paid":
                # 获取订单详细信息
                cursor.execute(
                    "SELECT count, price from order_detail where order_id=%s", (order_id,)
                )
                rows = cursor.fetchall()
                total_price = 0
                for row in rows:
                    total_price += int(row[0])*int(row[1])

                # 更新用户余额，将付款退还给用户
                cursor.execute(
                    "SELECT balance from \"user\" where user_id=%s", (user_id,)
                )
                row = cursor.fetchone()
                refund_amount = total_price
                current_balance = int(row[0])
                new_balance = current_balance + refund_amount

                cursor.execute(
                    "UPDATE \"user\" SET balance = %s WHERE user_id = %s",
                    (new_balance, user_id),
                )

                # 取消订单，更新状态为 "cancelled"
                cursor.execute(
                    "UPDATE \"order\" SET status = %s, cancelled_at = %s WHERE order_id = %s",
                    ('cancelled', datetime.now().isoformat(), order_id),
                )

                self.conn.commit()
        except psycopg2.Error as e:
            print(e)
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def get_buyer_orders(self, user_id: str) -> (int, str, list):
        cursor = None
        buyer_orders = []
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT store_id, order_id, status from \"order\" where user_id=%s", (user_id,)
            )
            rows = cursor.fetchall()
            if len(rows) == 0:
                return error.error_authorization_fail()

            for row in rows:
                buyer_orders.append(
                    {'store_id': row[0],
                     'order_id': row[1],
                     'status': row[2]}
                )
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, "ok", buyer_orders