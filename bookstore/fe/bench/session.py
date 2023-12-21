from fe.bench.workload import Workload
from fe.bench.workload import ShipOrder,ReceiveOrder
from fe.bench.workload import Payment
import time
import threading


class Session(threading.Thread):
    def __init__(self, wl: Workload):
        threading.Thread.__init__(self)
        self.workload = wl
        self.new_order_request = []
        self.payment_request = []
        self.shipment_request = []
        self.receive_request = []

        self.new_order_i = 0
        self.payment_i = 0
        self.shipment_i = 0
        self.receive_i = 0

        self.new_order_ok = 0
        self.payment_ok = 0
        self.shipment_ok = 0
        self.receive_ok = 0

        self.time_new_order = 0
        self.time_payment = 0
        self.time_shipment = 0
        self.time_receive = 0
        self.thread = None
        self.gen_procedure()

    # 获取order对象
    def gen_procedure(self):
        for i in range(0, self.workload.procedure_per_session):
            new_order = self.workload.get_new_order()
            self.new_order_request.append(new_order)

    def run(self):
        self.run_gut()

    def run_gut(self):
        for new_order in self.new_order_request:
            before = time.time()
            # 运行下单操作，发送请求
            ok, order_id = new_order.run()
            after = time.time()
            self.time_new_order = self.time_new_order + after - before
            self.new_order_i = self.new_order_i + 1
            if ok:
                self.new_order_ok = self.new_order_ok + 1
                # 如果下单完成，创建付款对象
                payment = Payment(new_order.buyer, order_id)
                self.payment_request.append(payment)
            # 如果订单累计到一定的数量
            if self.new_order_i % 100 or self.new_order_i == len(self.new_order_request):
                self.workload.update_stat(
                    self.new_order_i,
                    self.payment_i,
                    self.shipment_i,
                    self.receive_i,
                    self.new_order_ok,
                    self.payment_ok,
                    self.shipment_ok,
                    self.receive_ok,
                    self.time_new_order,
                    self.time_payment,
                    self.time_shipment,
                    self.time_receive
                )

                # 批量发送付款请求
                for payment in self.payment_request:
                    before = time.time()
                    ok = payment.run()
                    after = time.time()
                    self.time_payment = self.time_payment + after - before
                    self.payment_i = self.payment_i + 1
                    if ok:
                        self.payment_ok = self.payment_ok + 1
                        shipment = ShipOrder(new_order.store_id, order_id)
                        self.shipment_request.append(shipment)


                for shipment in self.shipment_request:
                    before = time.time()
                    ok = shipment.run()
                    after = time.time()
                    self.time_shipment = self.time_shipment + after - before
                    self.shipment_i = self.shipment_i + 1
                    if ok:
                        self.shipment_ok = self.shipment_ok + 1
                        receive = ReceiveOrder(new_order.buyer, order_id)
                        self.receive_request.append(receive)

                for receive in self.receive_request:
                    before = time.time()
                    ok = receive.run()
                    after = time.time()
                    self.time_receive = self.time_receive + after - before
                    self.receive_i = self.receive_i + 1
                    if ok:
                        self.receive_ok = self.receive_ok + 1

                self.payment_request = []
                self.shipment_request = []
                self.receive_request = []
