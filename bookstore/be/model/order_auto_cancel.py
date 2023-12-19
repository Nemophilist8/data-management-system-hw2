import threading
from datetime import datetime, timedelta
from model import error, db_conn


class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)  # 定时器每分钟执行一次
        self.cancel_timer.start()

    def cancel_unpaid_orders(self):
        conn = self.conn
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id,created_at FROM \"order\" WHERE status = %s",
                ('unpaid',),
            )
            current_time = datetime.now()
            time_interval = current_time - timedelta(minutes=1)
            rows = cursor.fetchall()
            for row in rows:
                order_id = row[0]
                created_at = row[1]
                order_time = created_at
                if order_time < time_interval:
                    cursor.execute(
                        "UPDATE \"order\" set status = %s WHERE order_id = %s",
                        ('cancelled', order_id),
                    )
            conn.commit()
        except Exception as e:
            print(f"Error canceling unpaid orders: {str(e)}")
        finally:
            if cursor:
                cursor.close()

        # 重新启动定时器
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)
        self.cancel_timer.start()

