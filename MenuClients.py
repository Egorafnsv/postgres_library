import tkinter as tk
import tkinter.messagebox as box

import psycopg2


class MenuClients:
    def __init__(self, connection, table, main):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.table = table
        self.main = main
        self.changed = False
        self.state = 1

    def insert_client(self, name, surname, patronymic, series, num):
        if len(series) != 4 or len(num) != 6:
            box.showerror("Error", "Некорректные пасспортные данные!")
            return

        try:
            self.cursor.execute(
                f"insert into clients values (DEFAULT, '{name}', '{surname}', '{patronymic}', '{series}', '{num}')")
            self.connection.commit()
            self.changed = True
        except psycopg2.InternalError:
            box.showerror("Ошибка", "Читатель с такими паспортными данными уже существует")
            self.connection.rollback()
        except ZeroDivisionError:
            box.showerror("Ошибочка", "Incorrect data")
            self.connection.rollback()
        finally:
            self.clients_window.destroy()

    def add_client(self):
        self.clients_window = tk.Toplevel(self.main)
        self.clients_window.grab_set()
        self.clients_window.geometry('250x300')
        self.clients_window.title('Добавить')
        self.clients_window.iconbitmap('book_education_icon_217331.ico')
        self.clients_window.resizable(width=False, height=False)

        entry_frame = tk.Frame(self.clients_window)
        entry_frame.pack(pady=15)

        surname_label = tk.Label(entry_frame, text='Фамилия:')
        surname_label.grid(row=0, column=0, pady=20, padx=10)
        surname = tk.Entry(entry_frame, bg='white')
        surname.grid(row=0, column=1)

        name_label = tk.Label(entry_frame, text='Имя:')
        name_label.grid(row=1, column=0, pady=0, padx=10)
        name = tk.Entry(entry_frame, bg='white')
        name.grid(row=1, column=1)

        patronymic_label = tk.Label(entry_frame, text='Отчество:')
        patronymic_label.grid(row=2, column=0, pady=20, padx=10)
        patronymic = tk.Entry(entry_frame, bg='white')
        patronymic.grid(row=2, column=1)

        series_label = tk.Label(entry_frame, text='Серия:')
        series_label.grid(row=3, column=0, pady=0, padx=10)
        series = tk.Entry(entry_frame, bg='white')
        series.grid(row=3, column=1)

        num_label = tk.Label(entry_frame, text='Номер:')
        num_label.grid(row=4, column=0, pady=20, padx=10)
        num = tk.Entry(entry_frame, bg='white')
        num.grid(row=4, column=1)

        tk.Button(entry_frame, text='Добавить',
                  command=lambda: self.insert_client(name.get(), surname.get(),
                                                     patronymic.get(), series.get(), num.get())).grid(row=5,
                                                                                                      columnspan=2)

    def delete_client(self):
        info = self.table.item(self.table.selection())['values']
        if len(info) == 0:
            return

        if box.askyesno("Удаление", f"Удалить читателя {info[1]} {info[2]} {info[3]} и все записи в журнале, связанные с ним?"):
            try:
                self.cursor.execute(f"delete from journal where \"CLIENT_ID\"={info[0]}")
                self.cursor.execute(f"delete from clients where \"ID\"={info[0]}")
                self.connection.commit()
                self.changed = True
            except psycopg2.InternalError:
                box.showerror("Журнал", f"Читатель {info[1]} {info[2]} {info[3]} не вернул книги")
                self.connection.rollback()
            except:
                box.showerror("Ошибочка", "Что-то пошло не так")
                self.connection.rollback()
