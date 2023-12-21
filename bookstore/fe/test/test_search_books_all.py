import pytest
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import random


class TestSearchBooksAll:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self, str_len=2):

        # 测试的时候要用已有的数据，已有的数据存在book里，不应该改动
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, book_db.get_book_count())
        self.json = {
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
            if getattr(selected_book, i) is not None:
                text_length = len(getattr(selected_book, i))
                if random.random() > 0.6 and text_length >= str_len:
                    start_index = random.randint(0, text_length - str_len)
                    self.json[i] = getattr(selected_book, i)[start_index:start_index + str_len]
        yield

    def test_ok(self):
        def check_ok():
            processed_json = {}
            for key, value in self.json.items():
                if len(value) != 0:
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
        print('json_list',json_list)
        code, res = book.search_all(json_list[0], json_list[1], json_list[2], json_list[3], json_list[4],
                                    json_list[5], json_list[6], 1, 100000000)
        assert code == 200
        res = [i['id'] for i in res['data']]
        print('搜索结果', len(res), res)
        right_answer = check_ok()
        print('真实结果', len(right_answer), right_answer)
        assert len(right_answer) == len(res)
        for i in res:
            if i not in right_answer:
                assert False  # 搜索结果不正确


if __name__ == "__main__":
    t = TestSearchBooksAll()
    t.pre_run_initialization()
    t.test_ok()
