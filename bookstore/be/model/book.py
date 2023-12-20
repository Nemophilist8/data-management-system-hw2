import psycopg2
from model import db_conn
import base64

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
            for key, value in qs_dict.items():
                if len(value) != 0:
                    qs_dict[key] = ''
                qs_dict[key] = '%'+value+'%'
            cursor.execute(
                "SELECT * FROM book WHERE id IN %s, title LIKE %s, author LIKE %s, publisher LIKE %s, isbn LIKE %s, content LIKE %s, tags LIKE %s, book_intro LIKE %s LIMIT %s OFFSET %s",
                (tuple(book_ids),qs_dict['title'],qs_dict['author'],qs_dict['publisher'],qs_dict['isbn'],qs_dict['content'],qs_dict['tags'],qs_dict['book_intro'],per_page,(page - 1) * per_page),
            )
            result = cursor.fetchall()
            conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, result

    def search_all(self,title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
        conn = self.conn
        cursor = None
        try:
            qs_dict = {
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }

            for key, value in qs_dict.items():
                if len(value) != 0:
                    qs_dict[key] = ''
                qs_dict[key] = '%'+value+'%'

            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM book WHERE title LIKE %s AND author LIKE %s AND publisher LIKE %s AND isbn LIKE %s AND content LIKE %s AND tags LIKE %s AND book_intro LIKE %s LIMIT %s OFFSET %s",
                (qs_dict['title'],qs_dict['author'],qs_dict['publisher'],qs_dict['isbn'],qs_dict['content'],qs_dict['tags'],qs_dict['book_intro'],per_page,(page - 1) * per_page),
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    'id':row[0],
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
                })
            conn.commit()
        except psycopg2.Error as e:
            print(e)
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))
        finally:
            if cursor:
                cursor.close()
        return 200, results