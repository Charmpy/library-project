import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMessageBox
from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QTableWidgetItem, QHeaderView, QTabWidget


class Data:
    def __init__(self):
        self.con = sqlite3.connect('library_db.db')
        self.cur = self.con.cursor()

    def get_books(self, str, **kwargs):
        rez = self.cur.execute('''
        SELECT * FROM books
        WHERE id > 0
        ''').fetchall()
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
        self.cur.execute('''
                            INSERT INTO books(id, title, author, genre, year) VALUES(?, ?, ?, ?, ?) 
                            ''', (ide, title, author, genre, year, ))


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
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('book_widget.ui', self)
        self.back.clicked.connect(lambda x: self.root.widget.setCurrentIndex(0))

        self.book_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.author_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.genre_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.refresh_tables()

        self.add_book_btn.clicked.connect(self.add_book_dialog)
        self.add_author_btn.clicked.connect(self.add_author_dialog)
        self.add_genre_btn.clicked.connect(self.add_genre_dialog)

        self.change_book_btn.clicked.connect(self.change_book_dialog)
        self.change_author_btn.clicked.connect(self.change_author_dialog)
        self.change_genre_btn.clicked.connect(self.change_genre_dialog)

    def refresh_tables(self):
        book_head = ['id', 'Название', 'Автор', 'Жанр', 'Год']
        book_list = self.root.data.get_books('123')
        self.change_book_list(book_list)
        show_tbl(self.book_tbl, book_list, book_head)

        author_head = ['id', 'ФИО']
        author_list = self.root.data.get_authors()
        show_tbl(self.author_tbl, author_list, author_head)

        genre_head = ['id', 'ФИО']
        genre_list = self.root.data.get_genres()
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
            a = self.d.author_combo.currentIndex() + 1
            g = self.d.genre_combo.currentIndex() + 1
            y = self.d.year_in.text()
            msg = QMessageBox(self.d)
            if bool(t) and bool(y) and bool(a) and bool(g):
                try:
                    y = int(y)
                except ValueError:
                    msg.question(self, '', 'Неверный год', msg.Ok)

                else:
                    if 0 < y <= 2020:
                        self.root.data.add_book(t, a, g, y)
                        self.refresh_tables()
                        self.d.close()
                    else:
                        msg.question(self, '', 'Неверный год', msg.Ok)
            else:
                msg.question(self, '', 'Не все поля заполнены', msg.Ok)

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
            self.d.close()

        self.d = QDialog()
        uic.loadUi('book_add_author_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def add_genre_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('book_add_genre_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_book_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('book_change_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_author_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('book_change_author_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_genre_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('book_change_genre_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)


class GiveWidget(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('give_widget.ui', self)
        self.back.clicked.connect(lambda x: self.root.widget.setCurrentIndex(0))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        head = ['id', 'ФИО', 'Книга']
        info = self.root.data.get_readers(True)
        self.change_info(info)
        show_tbl(self.table, info, head)
        self.give_btn.clicked.connect(self.give_dialog)
        self.get_btn.clicked.connect(self.back_dialog)

    def change_info(self, info):
        for i in info:
            i[-1] = self.root.data.get_bookinfo(i[-1])

    def give_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('give_give_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def back_dialog(self):
        def close():
            self.d.close()

        def check():
            self.d.close()

        self.d = QDialog()
        uic.loadUi('give_back_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)


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
