from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QDialog, QTableWidgetItem


class GiveWidget(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('UI/give_widget.ui', self)
        self.back.clicked.connect(
            lambda: (
                self.root.widget.setCurrentIndex(0), self.root.refresh_tables()
            )
        )
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
            info = [
                self.d.name_tbl.item(x, 0).text(),
                self.d.name_tbl.item(x, 1).text()
            ]
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
        uic.loadUi('UI/give_give_dialog.ui', self.d)
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
            self.out_info = [
                self.d.name_tbl.item(x, i).text() for i in range(3)
            ]
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
        uic.loadUi('UI/give_back_dialog.ui', self.d)
        head = ['id', 'ФИО', 'книга']
        info = self.root.data.get_readers(True)
        self.change_info(info)
        self.d.name_tbl.horizontalHeader().setStretchLastSection(True)
        show_tbl(self.d.name_tbl, info, head)

        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)
        self.d.name_tbl.cellClicked.connect(chose_user)


def show_tbl(table, info, head):
    table.setRowCount(len(info))
    table.setColumnCount(len(head))
    table.setHorizontalHeaderLabels(head)
    if len(info) > 0:
        table.setRowCount(len(info))
        for i in range(len(info)):
            for j in range(len(head)):
                table.setItem(i, j, QTableWidgetItem(str(info[i][j])))
