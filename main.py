import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *

import sqlite3 as sl


global authorization_db
global cursor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('basic.ui', self) # Load the .ui file
        self.show() # Show the GUI

        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.regist)
        self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(self.authorization)

    def regist(self):
        self.reg = Reg()
        self.reg.show()
        self.hide() 

    def authorization(self):
        self.auth = Auth()
        self.auth.show()
        self.hide() 


class Reg(QtWidgets.QMainWindow):
    def __init__(self):
        super(Reg, self).__init__()
        uic.loadUi('reg.ui', self)
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.registration)
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.lineEdit2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(self.home)

    def registration(self):
        login = self.lineEdit.text()
        password = self.lineEdit2.text()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        if passCheck(password):
            if loginCheck(login):
                cursor.execute(f"INSERT INTO users VALUES (?,?)", (login, password))
                self.home()
            else:
                self.lineEdit.setText('')
                self.lineEdit2.setText('')
                msg.setText("Это имя уже занято!")
                msg.exec_()
        else:
            self.lineEdit.setText('')
            self.lineEdit2.setText('')
            msg.setText("Неверный формат пароля!")
            msg.exec_()
    
    def home(self):
        self.w = MainWindow()
        self.w.show()
        self.hide()


    
class Auth(QtWidgets.QMainWindow):
    def __init__(self):
        super(Auth, self).__init__()
        uic.loadUi('authorization.ui', self)
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.authorization)
        self.lineEdit = self.findChild(QtWidgets.QLineEdit, 'lineEdit')
        self.lineEdit2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_2')
        self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(self.home)

    def authorization(self):
        login = self.lineEdit.text()
        password = self.lineEdit2.text()
        cursor.execute(f"SELECT username, password FROM users WHERE username ='{login}' AND password = '{password}'")
        authorization_db.commit()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        if not cursor.fetchone():
            self.lineEdit.setText('')
            self.lineEdit2.setText('')
            msg.setText("Нет такого пользователя")
            msg.exec_()
            logging.info("Неверная попытка входа под логином {0}".format(login))
            f = open('count.txt', )
            with open('count.txt', mode='r') as f:
                lines = f.readlines()
            count_all, count_ancorrect = int(lines[0]), int(lines[1])
            count_all += 1
            count_ancorrect += 1
            new_lines = f'{count_all}\n{count_ancorrect}'
            with open('count.txt', mode='w') as f:
                f.write(new_lines)
        else:
            self.hide()
            logging.info(f"Вход пользователя {login}")
            with open('count.txt', mode='r+') as f:
                lines = f.readlines()
            count_all, count_ancorrect = int(lines[0]), int(lines[1])
            count_all += 1
            
            new_lines = f'{count_all}\n{count_ancorrect}'
            with open('count.txt', mode='w') as f:
                f.write(new_lines)
            if login == 'admin':
                self.admin = Admin()
                self.admin.show()
            else:
                self.user = User()
                self.user.show()
    
    def home(self):
        self.w = MainWindow()
        self.w.show()
        self.hide()
                

class Admin(QtWidgets.QMainWindow):
    def __init__(self):
        super(Admin, self).__init__()
        uic.loadUi('admin.ui', self)
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.tableWidget.setHorizontalHeaderLabels(["Логин", "Пароль"])
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.home)
        self.loaddata()

    def loaddata(self):
        self.tableWidget.setRowCount(50)
        tableindex = 0
        for row in cursor.execute("SELECT * FROM users LIMIT 50"):
            self.tableWidget.setItem(tableindex, 0, QtWidgets.QTableWidgetItem(row[0]))
            self.tableWidget.setItem(tableindex, 1, QtWidgets.QTableWidgetItem(row[1]))
            tableindex += 1

    def home(self):
        self.w = MainWindow()
        self.w.show()
        self.hide()

    

class User(QtWidgets.QMainWindow):
    def __init__(self):
        super(User, self).__init__()
        uic.loadUi('user.ui', self)
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.home)

    def home(self):
        self.w = MainWindow()
        self.w.show()
        self.hide()




def passCheck(password):
    letters = 'уеыаояюиэeyuioa'
    for i in (password.lower()):
        if i not in letters:
            return False
    return True

def loginCheck(login):
    cursor.execute(f"SELECT username FROM users WHERE username = '{login}'")
    answer = list(cursor.fetchall())
    if answer:
        return False
    return True


if __name__ == '__main__':
    authorization_db = sl.connect("identAndAutorithat.db")
    cursor = authorization_db.cursor()
    with authorization_db:
        authorization_db.execute("""
            CREATE TABLE IF NOT EXISTS "users" (
                "username" TEXT,
                "password" TEXT)""")
    cursor.execute(f"INSERT INTO users VALUES (?,?)", ("admin", "admin"))
    authorization_db.commit()


    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
    authorization_db.execute("DELETE FROM users")

