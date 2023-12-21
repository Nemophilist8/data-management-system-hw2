import time

import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.seller import get_seller_order
from fe.access.buyer import Buyer
import uuid


class TestGetOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_ids=[]
        self.store_ids=[]
        self.buyer_ids=[]
        self.passwords=[]
        self.buyers=[]
        self.gen_books=[]

        for i in range(3):
            self.seller_ids.append("test_new_order_seller_id_{}".format(str(uuid.uuid1())))
            self.store_ids.append("test_new_order_store_id_{}".format(str(uuid.uuid1())))
            self.buyer_ids.append("test_new_order_buyer_id_{}".format(str(uuid.uuid1())))
            self.passwords.append(self.seller_ids[i])
            self.buyers.append(register_new_buyer(self.buyer_ids[i], self.passwords[i]))
            self.gen_books.append(GenBook(self.seller_ids[i], self.store_ids[i]))
        yield

    def test_ok(self):
        buy_book_id_lists=[]
        for i in range(3):
            ok, buy_book_id_list = self.gen_books[i].gen(
                non_exist_book_id=False, low_stock_level=False
            )
            assert ok
            buy_book_id_list = [(i[0],1) for i in buy_book_id_list]
            buy_book_id_lists.append(buy_book_id_list)

        code, _ = self.buyers[0].new_order(self.store_ids[0], buy_book_id_lists[0])
        assert code == 200
        code, _ = self.buyers[0].new_order(self.store_ids[1], buy_book_id_lists[1])
        assert code == 200
        code, _ = self.buyers[0].new_order(self.store_ids[2], buy_book_id_lists[2])
        assert code == 200
        code, _ = self.buyers[1].new_order(self.store_ids[0], buy_book_id_lists[0])
        assert code == 200
        code, _ = self.buyers[1].new_order(self.store_ids[1], buy_book_id_lists[1])
        assert code == 200
        code, _ = self.buyers[1].new_order(self.store_ids[2], buy_book_id_lists[2])
        assert code == 200

        code, result = get_seller_order(self.seller_ids[0])
        assert code == 200
        code, result = get_seller_order(self.seller_ids[1])
        assert code == 200
        code, result = get_seller_order(self.seller_ids[2])
        assert code == 200

        code, result = self.buyers[0].get_seller_order()
        assert code == 200
        code, result = self.buyers[1].get_seller_order()
        assert code == 200











