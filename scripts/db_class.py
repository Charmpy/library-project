import sqlite3


class Data:
    def __init__(self):
        self.con = sqlite3.connect('library_db.db')
        self.cur = self.con.cursor()

    def find_authors(self, line):
        rez = self.cur.execute(
            '''
            SELECT * FROM authors
            WHERE name LIKE ?
            ''', (f'%{line}%',)).fetchall()
        return [list(i) for i in rez]

    def find_genres(self, line):
        rez = self.cur.execute(
            '''
            SELECT * FROM genres
            WHERE genre LIKE ?
            ''', (f'%{line}%',)).fetchall()
        return [list(i) for i in rez]

    def get_books(self, head='', line=''):
        if head == -1:
            head = 0
        head = ['id', 'title', 'author', 'genre', 'year'][int(head)]
        rez = self.cur.execute(
            '''
            SELECT * FROM books
            WHERE id > 0
            ''').fetchall()
        if head == 'author':
            rez = self.cur.execute(
                '''SELECT * FROM books
                    WHERE id > 0 AND author IN (SELECT id from authors WHERE name LIKE ?)
                ''', (f'%{line}%', )).fetchall()
        elif head == 'genre':
            rez = self.cur.execute(
                '''SELECT * FROM books
                    WHERE id > 0 AND genre IN (SELECT id from genres WHERE genre LIKE ?)
                ''', (f'%{line}%',)).fetchall()
        elif head == 'title':
            rez = self.cur.execute(
                '''SELECT * FROM books
                    WHERE id > 0 AND title LIKE ?
                ''', (f'%{line}%',)).fetchall()
        elif head == 'year':
            rez = self.cur.execute(
                '''SELECT * FROM books
                    WHERE id > 0 AND year LIKE ?
                ''', (f'{line}',)).fetchall()
        return [list(i) for i in rez]

    def get_authors(self):
        rez = self.cur.execute('''
            SELECT * FROM authors
        ''',).fetchall()
        return [list(i) for i in rez]

    def get_genres(self):
        rez = self.cur.execute('''
            SELECT * FROM genres
        ''',).fetchall()
        return [list(i) for i in rez]

    def get_bookinfo(self, index):
        title = self.cur.execute('''
                SELECT title FROM books
                WHERE id = ?
        ''', (index, )).fetchone()
        author = self.cur.execute('''
                SELECT name FROM authors
                WHERE id = (SELECT author FROM books WHERE id = ?)
        ''', (index, )).fetchone()
        if not bool(title) or not bool(author):
            return 0
        return f'{title[0]} ({author[0]})'

    def get_authorname(self, index):
        author = self.cur.execute('''
            SELECT name FROM authors
            WHERE id = ?
        ''', (index,)).fetchone()
        return author[0]

    def get_genrename(self, index):
        genre = self.cur.execute('''
            SELECT genre FROM genres
            WHERE id = ?
        ''', (index,)).fetchone()
        return genre[0]

    def get_readers(self, fl):
        if fl:
            rez = self.cur.execute('''
                SELECT * FROM users
                WHERE books > 0
            ''').fetchall()
        else:
            rez = self.cur.execute('''
                SELECT * FROM users
            ''').fetchall()
        return [list(i) for i in rez]

    def add_book(self, title, author, genre, year):
        ide = self.cur.execute("select max(id) from books").fetchall()[0][0] + 1
        self.cur.execute(
            '''
                INSERT INTO books(id, title, author, genre, year) VALUES(
                ?, ?, 
                (SELECT id FROM authors WHERE name LIKE ?), 
                (SELECT id FROM genres WHERE genre LIKE ?), 
                ?
                ) 
            ''', (ide, title, author, genre, year, ))

    def add_author(self, name):
        ide = self.cur.execute("select max(id) from authors").fetchall()[0][0] + 1
        self.cur.execute(
            '''
                INSERT INTO authors(id, name) VALUES(?, ?) 
            ''', (ide, name,))

    def add_genre(self, genre):
        ide = self.cur.execute("select max(id) from genres").fetchall()[0][0] + 1
        self.cur.execute(
            '''
                INSERT INTO genres(id, genre) VALUES(?, ?) 
            ''', (ide, genre,))

    def add_user(self, name):
        ide = self.cur.execute("select max(id) from users").fetchall()[0][0] + 1
        self.cur.execute(
            '''
                INSERT INTO users(id, name, books) VALUES(?, ?, ?) 
            ''', (ide, name, 0, ))

    def change_book(self, index, title, author, genre, year):
        self.cur.execute('''
                UPDATE books
                SET title = ?, 
                author = (SELECT id FROM authors WHERE name LIKE ?),
                genre = (SELECT id FROM genres WHERE genre LIKE ?), 
                year = ?
                WHERE id = ?
            ''', (title, author, genre, year, index,))

    def change_author(self, index, name):
        self.cur.execute(
            '''
                UPDATE authors
                SET name = ?
                WHERE id = ?
            ''', (name, index,))

    def change_genre(self, index, genre):
        self.cur.execute(
            '''
                UPDATE genres
                SET genre = ?
                WHERE id = ?
            ''', (genre, index,))

    def change_user(self, index, name):
        self.cur.execute('''
            UPDATE users
            SET name = ?
            WHERE id = ?
        ''', (name, index, ))

    def delete_user(self, index):
        self.cur.execute('''
        DELETE FROM users
        WHERE id = ?''', (index,))

    def delete_book(self, index):
        self.cur.execute('''
            UPDATE users
            SET books = 0
            WHERE books = ?''', (index,))
        self.cur.execute('''
        DELETE FROM books
        WHERE id = ?''', (index, ))

    def delete_author(self, index):
        self.cur.execute(
            '''
            UPDATE books
            SET author = 0
            WHERE author = ?
            ''', (index,))
        self.cur.execute('''
        DELETE FROM authors
        WHERE id = ?''', (index, ))

    def delete_genre(self, index):
        self.cur.execute(
            '''
            UPDATE books
            SET genre = 0
            WHERE genre = ?
            ''', (index,))
        self.cur.execute('''
        DELETE FROM genres
        WHERE id = ?''', (index, ))

    def find_users(self, line, flag=''):
        if flag == 1:
            rez = self.cur.execute(
                '''
                SELECT * FROM users
                WHERE name LIKE ? AND books = 0
                ''', (f'%{line}%',)).fetchall()

        elif flag == 2:
            rez = self.cur.execute(
                '''
                SELECT * FROM users
                WHERE name LIKE ? AND books > 0
                ''', (f'%{line}%',)).fetchall()
        else:
            rez = self.cur.execute(
                '''
                SELECT * FROM users
                WHERE name LIKE ?
                ''', (f'%{line}%',)).fetchall()
        return [list(i) for i in rez]

    def check_book(self, book_author, book_title):
        rez = self.cur.execute(
            '''
            SELECT id FROM users
            WHERE books = (
                SELECT id FROM books WHERE title LIKE ? AND author = (SELECT id FROM authors WHERE name LIKE ?)
            )
            ''', (book_title, book_author,)).fetchall()
        if rez:
            return True
        return False

    def give_book(self, user_name, book_author, book_title):
        self.cur.execute(
            '''
            UPDATE users
            SET books = (
                SELECT id FROM books 
                WHERE title LIKE ? AND author = (SELECT id FROM authors WHERE name LIKE ?)
                )
            WHERE name = ?
            ''', (book_title, book_author, user_name, ))

    def back_book(self, user_name):
        self.cur.execute(
            '''
            UPDATE users
            SET books = 0
            WHERE name LIKE ?
            ''', (user_name, ))

