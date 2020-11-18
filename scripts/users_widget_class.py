from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox


class UsersWidget(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self):
        uic.loadUi('users_widget.ui', self)
        self.back.clicked.connect(lambda: (self.root.widget.setCurrentIndex(0), self.root.refresh_tables()))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.refresh_table()
        self.add_b.clicked.connect(self.add_dialog)
        self.table.cellDoubleClicked.connect(self.table_change)

    def table_change(self, row, column):
        selected_user_info = [self.table.item(row, i).text() for i in range(3)]
        self.change_dialog(selected_user_info)

    def refresh_table(self):
        head = ['id', 'ФИО', 'Книга']
        info = self.root.data.get_readers(True)
        self.change_info(info)
        show_tbl(self.table, info, head)

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
            n = self.d.user_name_in.text()
            if bool(n):
                self.root.data.add_user(n)
                self.d.close()
                self.refresh_table()
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('users_add_dialog.ui', self.d)
        self.d.show()
        self.d.cancel_btn.clicked.connect(close)
        self.d.ok_btn.clicked.connect(check)

    def change_dialog(self, info):
        def delete():
            dialog = QMessageBox(self.d)
            ret = dialog.question(self, '', "Удалить пользователя из базы данных?", dialog.Yes | dialog.No)
            if ret == dialog.Yes:
                self.root.data.delete_user(info[0])
                self.refresh_table()
                self.d.close()

        def close():
            self.d.close()

        def check():
            n = self.d.user_name_in.text()
            if bool(n):
                self.root.data.change_user(info[0], n)
                self.d.close()
                self.refresh_table()
            else:
                self.d.error.setText('Не все поля заполнены')

        self.d = QDialog()
        uic.loadUi('users_change_dialog.ui', self.d)
        self.d.show()
        self.d.user_name_in.setText(info[1])
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
