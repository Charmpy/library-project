from PyQt5 import uic
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox


class BookWidget(QWidget):
    def __init__(self, root):
        self.selected_book_info = None
        self.selected_author_info = None
        self.selected_genre_info = None
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/book_widget.ui', self)
        self.back.clicked.connect(
            lambda: (
                self.root.widget.setCurrentIndex(0), self.root.refresh_tables()
            )
        )

        self.book_tbl.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
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
        selected_book_info = [
            self.book_tbl.item(row, i).text() for i in range(5)
        ]
        self.change_book_dialog(selected_book_info)

    def change_author_coords(self, row, col):
        selected_author_info = [
            self.author_tbl.item(row, i).text() for i in range(2)
        ]
        self.change_author_dialog(selected_author_info)

    def change_genre_coords(self, row, col):
        selected_genre_info = [
            self.genre_tbl.item(row, i).text() for i in range(2)
        ]
        self.change_genre_dialog(selected_genre_info)

    def refresh_tables(self):
        book_list = self.root.data.get_books(
            self.find_combo.currentIndex(), self.find_in.text()
        )

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
        uic.loadUi('UI/book_add_dialog.ui', self.d)
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
        uic.loadUi('UI/book_add_author_dialog.ui', self.d)
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
        uic.loadUi('UI/book_add_genre_dialog.ui', self.d)
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
            ret = dialog.question(
                self, '', "Удалить книгу из базы данных?",
                dialog.Yes | dialog.No
            )
            if ret == dialog.Yes:
                self.root.data.delete_book(info[0])
                self.root.refresh_tables()
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
                        self.root.refresh_tables()
                        self.d.close()
                    else:
                        self.d.error.setText('Неверный год')
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('UI/book_change_dialog.ui', self.d)

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
            ret = dialog.question(
                self, '', "Удалить автора из базы данных?",
                dialog.Yes | dialog.No)
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
        uic.loadUi('UI/book_change_author_dialog.ui', self.d)
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
            ret = dialog.question(
                self, '', "Удалить жанр из базы данных?",
                dialog.Yes | dialog.No)
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
        uic.loadUi('UI/book_change_genre_dialog.ui', self.d)
        self.d.show()
        self.d.genre_in.setText(info[1])
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.delete_btn.clicked.connect(delete)


def show_tbl(table, info, head):
    table.setRowCount(len(info))
    table.setColumnCount(len(head))
    table.setHorizontalHeaderLabels(head)
    if len(info) > 0:
        table.setRowCount(len(info))
        for i in range(len(info)):
            for j in range(len(head)):
                table.setItem(i, j, QTableWidgetItem(str(info[i][j])))
