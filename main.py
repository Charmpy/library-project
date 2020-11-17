import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMessageBox
from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QTableWidgetItem, QHeaderView, QTabWidget


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

    def delete_book(self, index):
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


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.data = Data()
        self.initUI()

    def initUI(self):
        self.widget = QStackedWidget(self)
        main = uic.loadUi('main_widget.ui')
        book = BookWidget(self)
        give = GiveWidget(self)
        users = UsersWidget(self)

        self.widget.addWidget(main)
        self.widget.addWidget(book)
        self.widget.addWidget(give)
        self.widget.addWidget(users)

        main.find_books.clicked.connect(lambda x: self.widget.setCurrentIndex(1))
        main.give_books.clicked.connect(lambda x: self.widget.setCurrentIndex(2))
        main.work.clicked.connect(lambda x: self.widget.setCurrentIndex(3))

        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)


class BookWidget(QWidget):
    def __init__(self, root):
        self.selected_book_info = None
        self.selected_author_info = None
        self.selected_genre_info = None
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('book_widget.ui', self)
        self.back.clicked.connect(lambda x: self.root.widget.setCurrentIndex(0))

        self.book_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.author_tbl.horizontalHeader().setStretchLastSection(True)
        self.genre_tbl.horizontalHeader().setStretchLastSection(True)
        self.refresh_tables()

        self.find_param = ['не указан', 'Название', 'Автор', 'Жанр', 'Год']
        self.find_combo.addItems(self.find_param)
        self.find_combo.currentIndexChanged.connect(self.refresh_tables)
        self.find_in.textChanged.connect(self.refresh_tables)
        self.find_author_in.textChanged.connect(self.refresh_tables)

        self.add_book_btn.clicked.connect(self.add_book_dialog)
        self.add_author_btn.clicked.connect(self.add_author_dialog)
        self.add_genre_btn.clicked.connect(self.add_genre_dialog)

        self.book_tbl.cellDoubleClicked.connect(self.change_book_coords)
        self.author_tbl.cellDoubleClicked.connect(self.change_author_coords)
        self.genre_tbl.cellDoubleClicked.connect(self.change_genre_coords)

    def change_book_coords(self, row, col):
        selected_book_info = [self.book_tbl.item(row, i).text() for i in range(5)]
        self.change_book_dialog(selected_book_info)

    def change_author_coords(self, row, col):
        selected_author_info = [self.author_tbl.item(row, i).text() for i in range(2)]
        self.change_author_dialog(selected_author_info)

    def change_genre_coords(self, row, col):
        selected_genre_info = [self.genre_tbl.item(row, i).text() for i in range(2)]
        self.change_genre_dialog(selected_genre_info)

    def refresh_tables(self):
        book_list = self.root.data.get_books(self.find_combo.currentIndex(), self.find_in.text())

        book_head = ['id', 'Название', 'Автор', 'Жанр', 'Год']
        self.change_book_list(book_list)
        show_tbl(self.book_tbl, book_list, book_head)

        author_head = ['id', 'ФИО']
        author_list = self.root.data.find_authors(self.find_author_in.text())
        author_list = list(filter(lambda x: x[0] != 0, author_list))
        show_tbl(self.author_tbl, author_list, author_head)

        genre_head = ['id', 'ФИО']
        genre_list = self.root.data.get_genres()
        genre_list = list(filter(lambda x: x[0] != 0, genre_list))
        show_tbl(self.genre_tbl, genre_list, genre_head)

    def change_book_list(self, info):
        for i in info:
            i[2] = self.root.data.get_authorname(i[2])
            i[3] = self.root.data.get_genrename(i[3])

    def add_book_dialog(self):
        def close():
            self.d.close()

        def check():
            t = self.d.title_in.text()
            a = self.d.author_combo.currentText()
            g = self.d.genre_combo.currentText()
            y = self.d.year_in.text()
            if bool(t) and bool(y) and bool(a) and bool(g):
                try:
                    y = int(y)
                except ValueError:
                    self.d.error.setText('Неверный год')
                else:
                    if 0 < y <= 2020:
                        self.root.data.add_book(t, a, g, y)
                        self.refresh_tables()
                        self.d.close()
                    else:
                        self.d.error.setText('Неверный год')
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('book_add_dialog.ui', self.d)
        authors = [i[1] for i in self.root.data.get_authors()]
        genres = [i[1] for i in self.root.data.get_genres()]
        self.d.author_combo.addItems(authors)
        self.d.genre_combo.addItems(genres)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def add_author_dialog(self):
        def close():
            self.d.close()

        def check():
            n = self.d.name_in.text()
            if bool(n):
                if bool(self.root.data.find_authors(n)):
                    self.d.error.setText('Такой автор уже существует')
                else:
                    self.root.data.add_author(n)
                    self.refresh_tables()
                    self.d.close()
            else:
                self.d.error.setText('Заполните поле')

        def update_tbl(line):
            info = self.root.data.find_authors(line)
            show_tbl(self.d.author_tbl, info, ['id', 'Автор'])

        self.d = QDialog()
        uic.loadUi('book_add_author_dialog.ui', self.d)
        self.d.show()
        self.d.author_tbl.horizontalHeader().setStretchLastSection(True)
        update_tbl('')
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.name_in.textChanged.connect(update_tbl)

    def add_genre_dialog(self):
        def close():
            self.d.close()

        def check():
            g = self.d.genre_in.text()
            if bool(g):
                if bool(self.root.data.find_genres(g)):
                    self.d.error.setText('Такой жанр уже существует')
                else:
                    self.root.data.add_genre(g)
                    self.refresh_tables()
                    self.d.close()
            else:
                self.d.error.setText('Заполните поле')

        def update_tbl(line):
            info = self.root.data.find_genres(line)
            show_tbl(self.d.genre_tbl, info, ['id', 'Жанр'])

        self.d = QDialog()
        uic.loadUi('book_add_genre_dialog.ui', self.d)
        self.d.show()
        self.d.genre_tbl.horizontalHeader().setStretchLastSection(True)
        update_tbl('')
        self.d.genre_in.textChanged.connect(update_tbl)
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_book_dialog(self, info):
        def close():
            self.d.close()

        def delete():
            dialog = QMessageBox(self.d)
            ret = dialog.question(self, '', "Удалить книгу из базы данных?", dialog.Yes | dialog.No)
            if ret == dialog.Yes:
                self.root.data.delete_book(info[0])
                self.refresh_tables()
                self.d.close()

        def check():
            index = info[0]
            t = self.d.title_in.text()
            a = self.d.author_combo.currentText()
            g = self.d.genre_combo.currentText()
            y = self.d.year_in.text()
            if bool(t) and bool(y) and bool(a) and bool(g):
                try:
                    y = int(y)
                except ValueError:
                    self.d.error.setText('Неверный год')
                else:
                    if 0 < y <= 2020:
                        self.root.data.change_book(index, t, a, g, y)
                        self.refresh_tables()
                        self.d.close()
                    else:
                        self.d.error.setText('Неверный год')
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('book_change_dialog.ui', self.d)

        authors = [i[1] for i in self.root.data.get_authors()]
        genres = [i[1] for i in self.root.data.get_genres()]
        self.d.author_combo.addItems(authors)
        self.d.genre_combo.addItems(genres)

        self.d.title_in.setText(info[1])
        self.d.author_combo.setCurrentText(authors[authors.index(info[2])])
        self.d.genre_combo.setCurrentText(genres[genres.index(info[3])])
        self.d.year_in.setText(info[4])

        self.d.show()
        self.d.delete_btn.clicked.connect(delete)
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_author_dialog(self, info):
        def close():
            self.d.close()

        def delete():
            dialog = QMessageBox(self.d)
            ret = dialog.question(self, '', "Удалить автора из базы данных?", dialog.Yes | dialog.No)
            if ret == dialog.Yes:
                self.root.data.delete_author(info[0])
                self.refresh_tables()
                self.d.close()

        def check():
            index = info[0]
            n = self.d.name_in.text()
            if bool(n):
                    self.root.data.change_author(index, n)
                    self.refresh_tables()
                    self.d.close()
            else:
                self.d.error.setText('Заполните поле')

        self.d = QDialog()
        uic.loadUi('book_change_author_dialog.ui', self.d)
        self.d.show()
        self.d.name_in.setText(info[1])
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.delete_btn.clicked.connect(delete)

    def change_genre_dialog(self, info):
        def close():
            self.d.close()

        def delete():
            dialog = QMessageBox(self.d)
            ret = dialog.question(self, '', "Удалить жанр из базы данных?", dialog.Yes | dialog.No)
            if ret == dialog.Yes:
                self.root.data.delete_genre(info[0])
                self.refresh_tables()
                self.d.close()

        def check():
            index = info[0]
            g = self.d.genre_in.text()
            if bool(g):
                self.root.data.change_genre(index, g)
                self.refresh_tables()
                self.d.close()
            else:
                self.d.error.setText('Заполните поле')

        self.d = QDialog()
        uic.loadUi('book_change_genre_dialog.ui', self.d)
        self.d.show()
        self.d.genre_in.setText(info[1])
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.delete_btn.clicked.connect(delete)


class GiveWidget(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('give_widget.ui', self)
        self.back.clicked.connect(lambda x: self.root.widget.setCurrentIndex(0))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.refresh_table()
        self.give_btn.clicked.connect(self.give_dialog)
        self.get_btn.clicked.connect(self.back_dialog)

    def change_info(self, info):
        for i in info:
            i[-1] = self.root.data.get_bookinfo(i[-1])

    def give_dialog(self):
        def refresh(line):
            info = self.root.data.find_users(line, '1')
            show_tbl(self.d.name_tbl, info, head)

        def chose_user(x, y):
            info = [self.d.name_tbl.item(x, 0).text(), self.d.name_tbl.item(x, 1).text()]
            self.d.name_tbl.setDisabled(True)
            self.d.user_name.setText(info[1])

        def change(line):
            self.d.title_combo.clear()
            self.d.title_combo.setDisabled(False)
            titles = [i[1] for i in self.root.data.get_books(2, line)]
            self.d.title_combo.addItems(titles)

        def close():
            self.d.close()

        def check():
            n = self.d.user_name.text()
            a = self.d.author_combo.currentText()
            t = self.d.title_combo.currentText()
            if bool(n) and bool(a) and bool(t):
                flag = self.root.data.check_book(a, t)
                if flag:
                    self.d.error.setText('Данная книга уже выдана')
                else:
                    self.root.data.give_book(n, a, t)
                    self.d.close()
                    self.refresh_table()
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('give_give_dialog.ui', self.d)
        self.d.name_tbl.horizontalHeader().setStretchLastSection(True)
        head = ['id', 'ФИО']
        info = self.root.data.find_users('', 1)
        show_tbl(self.d.name_tbl, info, head)
        authors = [i[1] for i in self.root.data.get_authors()]
        self.d.author_combo.addItems(authors)

        self.d.author_combo.currentTextChanged.connect(change)
        self.d.title_combo.setDisabled(True)

        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.name_tbl.cellClicked.connect(chose_user)
        self.d.name_in.textChanged.connect(refresh)

    def refresh_table(self):
        head = ['id', 'ФИО', 'Книга']
        info = self.root.data.get_readers(True)
        self.change_info(info)
        show_tbl(self.table, info, head)

    def back_dialog(self):
        def close():
            self.d.close()

        def chose_user(x, y):
            self.out_info = [self.d.name_tbl.item(x, i).text() for i in range(3)]
            self.d.user_name.setText(self.out_info[1])
            self.d.book_title.setText(self.out_info[2])

        def check():
            n = self.d.user_name.text()
            if bool(n):
                self.root.data.back_book(n)
                self.refresh_table()
                self.d.close()
            else:
                self.d.error.setText('Выберите пользователя')

        self.d = QDialog()
        uic.loadUi('give_back_dialog.ui', self.d)
        head = ['id', 'ФИО', 'книга']
        info = self.root.data.get_readers(True)
        self.change_info(info)
        self.d.name_tbl.horizontalHeader().setStretchLastSection(True)
        show_tbl(self.d.name_tbl, info, head)

        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.name_tbl.cellClicked.connect(chose_user)


class UsersWidget(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('users_widget.ui', self)
        self.back.clicked.connect(lambda x: self.root.widget.setCurrentIndex(0))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        head = ['id', 'ФИО', 'Книга']
        info = self.root.data.get_readers(False)
        self.change_info(info)
        show_tbl(self.table, info, head)
        self.add_b.clicked.connect(self.add_dialog)
        self.change_b.clicked.connect(self.change_dialog)

    def change_info(self, info):
        for i in info:
            if int(i[-1]) > 0:
                i[-1] = self.root.data.get_bookinfo(i[-1])
            else:
                i[-1] = 'Нет'

    def add_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('users_add_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('users_change_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)


def show_tbl(table, info, head):
    table.setRowCount(len(info))
    table.setColumnCount(len(head))
    table.setHorizontalHeaderLabels(head)
    if len(info) > 0:
        table.setRowCount(len(info))
        for i in range(len(info)):
            for j in range(len(head)):
                table.setItem(i, j, QTableWidgetItem(str(info[i][j])))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
