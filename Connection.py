import sys

import psycopg2
import hashlib
import tkinter.messagebox as box
import tkinter as tk
from MainWindow import MainWindow

# 2 пользователя в БД (логин - пароль):
# Egor - test12345
# usertest - puser


class Connection:
    def __init__(self):
        self.enter_window = tk.Tk()

    def hello_window(self):
        try:
            connection = psycopg2.connect(user="postgres",
                                          password="puser",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="libraryDB")
        except psycopg2.OperationalError:
            box.showerror("Ошибка", "Проблемы с подключением к базе данных")
            sys.exit(1)

        self.enter_window.title('Library')
        self.enter_window.iconbitmap('book_education_icon_217331.ico')
        self.enter_window['bg'] = '#ccc'
        self.enter_window.geometry('350x450')
        self.enter_window.resizable(width=False, height=False)

        frame = tk.Frame(self.enter_window, bg='#ccc')
        frame.pack(pady=75)

        title = tk.Label(frame, text='Вход', bg='#ccc', font=('Arial', 15))
        title.grid(row=0, column=0, columnspan=2, pady=20)

        label_login = tk.Label(frame, text='Логин: ', bg='#ccc', font=('Arial', 12))
        label_login.grid(row=1, column=0, pady=20)
        login_input = tk.Entry(frame, bg='white')
        login_input.grid(row=1, column=1, pady=20)

        label_pass = tk.Label(frame, text='Пароль: ', bg='#ccc', font=('Arial', 12))
        label_pass.grid(row=2, column=0, pady=20)
        pass_field = tk.Entry(frame, bg='white', show='*')
        pass_field.grid(row=2, column=1, pady=20)

        btn = tk.Button(frame, text='Connect', font=('Arial', 10), bg='white',
                        command=lambda: self.connect(login_input.get(), pass_field.get(), connection),
                        width=10)
        btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.enter_window.mainloop()

    def connect(self, user, password, connection):
        try:
            curs = connection.cursor()
            password = hashlib.md5(password.encode()).hexdigest()
            curs.execute(f"select \"password\" from users where \"login\"='{user}'")
            db_password = curs.fetchone()[0]

            if password == db_password:
                self.enter_window.destroy()
                MainWindow(connection)
            else:
                box.showerror("Ошибка в пароле", "Неверный пароль")
        except TypeError:
            box.showerror("Ошибка в логине", "Такой пользователь отсутствует")
        except psycopg2.InternalError:
            box.showerror("Ошибка", "Какая-то ошибка, обратитесь к Егору")
