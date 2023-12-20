import psycopg2
import pymongo
from model import db_conn
import base64
import copy

class Book(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        conn = self.conn
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT book_id FROM store WHERE order_id = %s",
                (store_id,),
            )
            book_ids = cursor.fetchall()

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

            qs_dict2={}
            for key,value in qs_dict.items():
                if len(value)!=0:
                    qs_dict2[key]=value
            qs_list2=[{key:{"$regex": value}} for key,value in qs_dict2.items()]
            if len(qs_list2)==0:
                query={}
            else:
                query = {
                    "$and": qs_list2
                }

            cursor.execute(
                "SELECT * FROM book WHERE id IN %s AND title LIKE %s AND author LIKE %s AND publisher LIKE %s AND isbn LIKE %s AND content LIKE %s AND tags LIKE %s AND book_intro LIKE %s LIMIT %s OFFSET %s",
                (tuple(book_ids),qs_dict1['title'],qs_dict1['author'],qs_dict1['publisher'],qs_dict1['isbn'],qs_dict1['content'],qs_dict1['tags'],qs_dict1['book_intro'],per_page,(page - 1) * per_page),
            )
            bookpic_collection = self.db["pic"]
            pics = bookpic_collection.find(query, {'_id': 0}).skip((page - 1) * per_page).limit(per_page)

            rows = cursor.fetchall()
            results = []
            for rowi in range(len(rows)):
                row = rows[rowi]
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
                    'picture': base64.b64encode(pics[rowi]['pic']).decode("utf-8")
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

            qs_dict2 = {}
            for key, value in qs_dict.items():
                if len(value) != 0:
                    qs_dict2[key] = value
            qs_list2 = [{key: {"$regex": value}} for key, value in qs_dict2.items()]
            if len(qs_list2) == 0:
                query = {}
            else:
                query = {
                    "$and": qs_list2
                }

            cursor.execute(
                "SELECT * FROM book WHERE title LIKE %s AND author LIKE %s AND publisher LIKE %s AND isbn LIKE %s AND content LIKE %s AND tags LIKE %s AND book_intro LIKE %s LIMIT %s OFFSET %s",
                (qs_dict1['title'], qs_dict1['author'], qs_dict1['publisher'], qs_dict1['isbn'],
                 qs_dict1['content'], qs_dict1['tags'], qs_dict1['book_intro'], per_page, (page - 1) * per_page),
            )
            bookpic_collection = self.db["pic"]
            pics = bookpic_collection.find(query, {'_id': 0}).skip((page - 1) * per_page).limit(per_page)
            rows = cursor.fetchall()
            results = []
            for rowi in range(len(rows)):
                row = rows[rowi]
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
                    'picture': base64.b64encode(pics[rowi]['pic']).decode("utf-8")
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