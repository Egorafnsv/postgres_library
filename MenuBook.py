import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as box

import psycopg2


class MenuBook:
    def __init__(self, connection, table, main):
        self.main = main
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.table = table
        self.changed = False
        self.state = 0

    def insert_book(self, name, count, types):
        try:
            self.cursor.execute(f"insert into books values (DEFAULT, '{name}', {count}, {types})")
            self.connection.commit()
            self.changed = True
        except:
            box.showerror("Ошибочка", "Incorrect data")
            self.connection.rollback()
        finally:
            self.book_window.destroy()

    def update_book(self, id, name, count, types):

        try:
            self.cursor.execute(
                f"update books set \"NAME\"='{name}', \"CNT\"={count}, \"TYPE_ID\"={types} where \"ID\"={id}")
            self.connection.commit()
            self.changed = True
        except:
            box.showerror("Ошибочка", "Incorrect data")
            self.connection.rollback()
        finally:
            self.book_window.destroy()

    def add_book(self):
        self.book_window = tk.Toplevel(self.main)
        self.book_window.grab_set()
        self.book_window.geometry('420x210')
        self.book_window.title('Добавить книгу')
        self.book_window.iconbitmap('book_education_icon_217331.ico')
        self.book_window.resizable(width=False, height=False)

        name_book_label = tk.Label(self.book_window, text='Название книги:')
        name_book_label.grid(row=0, column=0, pady=25, padx=10)
        name_book = tk.Entry(self.book_window, bg='white', width=40)
        name_book.grid(row=0, column=1, columnspan=3, sticky='W')

        count_books_label = tk.Label(self.book_window, text='Количество:')
        count_books_label.grid(row=1, column=0, pady=0, padx=10)
        count_books = tk.Entry(self.book_window, bg='white')
        count_books.grid(row=1, column=1, sticky='W')

        type_books_label = tk.Label(self.book_window, text='Тип:')
        type_books_label.grid(row=2, column=0, pady=25, padx=10)
        type_books = ttk.Combobox(self.book_window, values=[1, 2, 3], width=5, state='readonly')
        type_books.grid(row=2, column=1, sticky='W')

        tk.Button(self.book_window, text='Добавить',
                  command=lambda: self.insert_book(name_book.get(), count_books.get(),
                                                   type_books.get())).grid(row=3,
                                                                           columnspan=2)

    def change_book(self):
        info = self.table.item(self.table.selection())['values']
        if len(info) == 0:
            return

        self.book_window = tk.Toplevel(self.main)
        self.book_window.grab_set()
        self.book_window.geometry('420x210')
        self.book_window.title('Изменить книгу')
        self.book_window.iconbitmap('book_education_icon_217331.ico')
        self.book_window.resizable(width=False, height=False)

        name_book_label = tk.Label(self.book_window, text='Название книги:')
        name_book_label.grid(row=0, column=0, pady=25, padx=10)
        name_book = tk.Entry(self.book_window, bg='white', width=40)
        name_book.insert(0, f'{info[1]}')
        name_book.grid(row=0, column=1, columnspan=3, sticky='W')

        count_books_label = tk.Label(self.book_window, text='Количество:')
        count_books_label.grid(row=1, column=0, pady=0, padx=10)
        count_books = tk.Entry(self.book_window, bg='white')
        count_books.insert(0, f'{info[2]}')
        count_books.grid(row=1, column=1, sticky='W')

        type_books_label = tk.Label(self.book_window, text='Тип:')
        type_books_label.grid(row=2, column=0, pady=25, padx=10)
        type_books = ttk.Combobox(self.book_window, values=[1, 2, 3], width=5, state='readonly')
        type_books.set(info[3])
        type_books.grid(row=2, column=1, sticky='W')

        tk.Button(self.book_window, text='Изменить',
                  command=lambda: self.update_book(info[0], name_book.get(), count_books.get(),
                                                   type_books.get())).grid(row=3,
                                                                           columnspan=2)

    def delete_book(self):
        info = self.table.item(self.table.selection())['values']
        if len(info) == 0:
            return

        if box.askyesno("Удаление", f"Удалить книгу {info[1]} и все записи в журнале, связанные с ней?"):
            try:
                self.cursor.execute(f"delete from journal where \"BOOK_ID\"={info[0]}")
                self.cursor.execute(f"delete from books where \"ID\"={info[0]}")
                self.connection.commit()
                self.changed = True
            except psycopg2.InternalError:
                box.showerror("Журнал", "Экземпляры этой книги находятся у читателей")
                self.connection.rollback()
            except:
                box.showerror("Ошибочка", "Что-то пошло не так")
                self.connection.rollback()
