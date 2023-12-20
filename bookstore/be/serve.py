import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request
from view import auth
from view import seller
from view import buyer
from view import book
from model.store import init_database
from model.order_auto_cancel import OrderAutoCancel
from apscheduler.schedulers.background import BackgroundScheduler  # 导入背景调度器

bp_shutdown = Blueprint("shutdown", __name__)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."

# 创建一个函数来初始化和启动定时任务
def start_order_auto_cancel():
    scheduler = BackgroundScheduler()
    scheduler.add_job(OrderAutoCancel().cancel_unpaid_orders, 'interval', minutes=1)  # 每隔15分钟触发一次
    scheduler.start()

def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    init_database()

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # 初始化和启动定时任务
    start_order_auto_cancel()

    app = Flask(__name__)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(book.bp_book)
    app.run()
