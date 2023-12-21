import pytest

from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
import random
from fe import conf


class TestSearchBooksInStore:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self, str_len=2):

        # do before test
        self.seller_id = "test_search_in_store_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_in_store_books_store_id_{}".format(str(uuid.uuid1()))

        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200

        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, random.randint(1, 20))
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        self.json = {
            "store_id": self.store_id,
            "title": "",
            "author": "",
            "publisher": "",
            "isbn": "",
            "content": "",
            "tags": "",
            "book_intro": ""
        }
        selected_book = random.choice(self.books)

        for i in ['title', 'author', 'publisher', 'isbn', 'content', 'tags', 'book_intro']:
            text_length = len(getattr(selected_book, i))
            if random.random() > 0.8 and text_length >= str_len:
                start_index = random.randint(0, text_length - 2)
                self.json[i] = getattr(selected_book, i)[start_index:start_index + 2]

        yield

    def test_ok(self):
        def check_ok():
            processed_json = {}
            for key, value in self.json.items():
                if len(value) != 0 and key != 'store_id':
                    processed_json[key] = value
            print('pro', processed_json)
            if len(processed_json.keys()) == 0:
                return [book.id for book in self.books]

            res = []
            for d in self.books:
                flag = 0
                for key, substring in processed_json.items():
                    attr_value = getattr(d, key)
                    if attr_value is not None:
                        if isinstance(attr_value, str):
                            if attr_value.find(substring) == -1:
                                flag = 1
                        elif isinstance(attr_value, list):
                            for sub in substring:
                                if sub not in attr_value:
                                    flag = 1
                                    break
                        else:
                            flag = 1
                    else:
                        flag = 1

                if flag == 0:
                    res.append(d.id)

            return res

        json_list = list(self.json.values())
        code, res = book.search_in_store(json_list[0], json_list[1], json_list[2], json_list[3], json_list[4],
                                         json_list[5], json_list[6], json_list[7], 1, 10000000)
        assert code == 200

        res = [i['id'] for i in res['data']]
        print('搜索结果', res)

        right_answer = check_ok()
        print('真实结果', right_answer)
        assert len(right_answer) == len(res)
        # check_ok()
        for i in res:
            if i not in right_answer:
                assert False  # 搜索结果不正确


if __name__ == "__main__":
    t = TestSearchBooksInStore()
    t.pre_run_initialization()
    t.test_ok()
