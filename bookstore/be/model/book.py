import psycopg2
import pymongo
import os
import sys
sys.path[0] = os.path.dirname(os.getcwd())
from be.model import db_conn
import base64
import copy

class Book(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        conn = self.conn
        cursor = None
        results = []

        try:
            # 在store中搜索商店中拥有的图书列表
            cursor = conn.cursor()
            cursor.execute(
                "SELECT book_id FROM store WHERE store_id = %s",
                (store_id,),
            )
            book_ids = cursor.fetchall()
            if len(book_ids) != 0:
                qs_dict = {
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'isbn': isbn,
                    'content': content,
                    'tags': tags,
                    'book_intro': book_intro
                }
                qs_dict1 = copy.deepcopy(qs_dict)
                for key, value in qs_dict1.items():
                    if len(value) != 0:
                        qs_dict1[key] = ''
                    qs_dict1[key] = '%'+value+'%'

                # 按对应的要求与限制图书，返回结构化信息
                cursor.execute(
                    "SELECT * FROM book WHERE id IN %s AND title LIKE %s AND author LIKE %s AND publisher LIKE %s AND isbn LIKE %s AND content LIKE %s AND tags LIKE %s AND book_intro LIKE %s LIMIT %s OFFSET %s",
                    (tuple(book_ids),qs_dict1['title'],qs_dict1['author'],qs_dict1['publisher'],qs_dict1['isbn'],qs_dict1['content'],qs_dict1['tags'],qs_dict1['book_intro'],per_page,(page - 1) * per_page),
                )

                # 获取图片集合
                bookpic_collection = self.db["pic"]
                rows = cursor.fetchall()
                for rowi in range(len(rows)):
                    row = rows[rowi]
                    # 从MongoDB中找到对应的图片
                    pic = bookpic_collection.find_one({'id': row[0]}, {'_id': 0})
                    pic = pic['pic']
                    # 组装成完整的结果
                    results.append({
                        'id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'publisher': row[3],
                        'original_title': row[4],
                        'translator': row[5],
                        'pub_year': row[6],
                        'pages': row[7],
                        'price': row[8],
                        'currency_unit': row[9],
                        'binding': row[10],
                        'isbn': row[11],
                        'author_intro': row[12],
                        'book_intro': row[13],
                        'content': row[14],
                        'tags': row[15],
                        'picture': base64.b64encode(pic).decode("utf-8")
                    })
                conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, results

    def search_all(self,title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
        conn = self.conn
        cursor = None
        results = []

        try:
            cursor = conn.cursor()
            qs_dict = {
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }

            qs_dict1 = copy.deepcopy(qs_dict)
            for key, value in qs_dict1.items():
                if len(value) != 0:
                    qs_dict1[key] = ''
                qs_dict1[key] = '%' + value + '%'

            cursor.execute(
                "SELECT * FROM book WHERE title LIKE %s AND author LIKE %s AND publisher LIKE %s AND isbn LIKE %s AND content LIKE %s AND tags LIKE %s AND book_intro LIKE %s LIMIT %s OFFSET %s",
                (qs_dict1['title'], qs_dict1['author'], qs_dict1['publisher'], qs_dict1['isbn'],
                 qs_dict1['content'], qs_dict1['tags'], qs_dict1['book_intro'], per_page, (page - 1) * per_page),
            )
            bookpic_collection = self.db["pic"]
            rows = cursor.fetchall()

            for rowi in range(len(rows)):
                row = rows[rowi]
                pic = bookpic_collection.find_one({'id':row[0]}, {'_id': 0})
                pic = pic['pic']
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'publisher': row[3],
                    'original_title': row[4],
                    'translator': row[5],
                    'pub_year': row[6],
                    'pages': row[7],
                    'price': row[8],
                    'currency_unit': row[9],
                    'binding': row[10],
                    'isbn': row[11],
                    'author_intro': row[12],
                    'book_intro': row[13],
                    'content': row[14],
                    'tags': row[15],
                    'picture': base64.b64encode(pic).decode("utf-8")
                })
            conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, results