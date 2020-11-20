import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout

from scripts.book_widget_class import BookWidget
from scripts.db_class import Data
from scripts.give_widget_class import GiveWidget
from scripts.users_widget_class import UsersWidget


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.data = Data()
        self.initUI()

    def initUI(self):
        self.widget = QStackedWidget(self)
        main = uic.loadUi('UI/main_widget.ui')
        self.book = BookWidget(self)
        self.give = GiveWidget(self)
        self.users = UsersWidget(self)

        self.widget.addWidget(main)
        self.widget.addWidget(self.book)
        self.widget.addWidget(self.give)
        self.widget.addWidget(self.users)

        main.find_books.clicked.connect(lambda: (self.widget.setCurrentIndex(1), self.refresh_tables()))
        main.give_books.clicked.connect(lambda: (self.widget.setCurrentIndex(2), self.refresh_tables()))
        main.work.clicked.connect(lambda: (self.widget.setCurrentIndex(3), self.refresh_tables()))

        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)

    def refresh_tables(self):
        self.book.refresh_tables()
        self.give.refresh_table()
        self.users.refresh_table()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
