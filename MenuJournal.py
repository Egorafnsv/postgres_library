import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as box

import psycopg2
import tkcalendar
import datetime


class MenuJournal:
    def __init__(self, connection, table, main):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.table = table
        self.number_books = int()
        self.main = main
        self.changed = False
        self.state = 2

    def insert_record(self, book_id, client_id):
        try:
            if self.number_books >= 10:
                box.showerror("Превышен лимит", "На руках у читателя уже 10 книг")
                return

            book_id = book_id.split()[0][:-1]
            client_id = client_id.split()[0][:-1]

            self.cursor.execute(f"select \"TYPE_ID\" from books where \"ID\"={book_id}")
            type_id = self.cursor.fetchone()[0]

            self.cursor.execute(f"select \"DAY_COUNT\" from book_types where \"ID\"={type_id}")
            days = self.cursor.fetchone()[0]

            date_end = datetime.datetime.now().date() + datetime.timedelta(days=days)

            self.cursor.execute(
                f"insert into journal values (DEFAULT, '{book_id}', {client_id}, '{datetime.datetime.now()}', '{date_end}', DEFAULT)")

            self.cursor.execute(f"update books set \"CNT\"=\"CNT\"-1 where \"ID\"={book_id}")

            self.connection.commit()
            self.changed = True
        except ZeroDivisionError:
            box.showerror("Ошибочка", "Incorrect data")
            self.connection.rollback()
        finally:
            self.journal_window.destroy()

    def add_record(self):
        self.journal_window = tk.Toplevel(self.main)
        self.journal_window.geometry('580x200')
        self.journal_window.title('Выдать книгу')
        self.journal_window.iconbitmap('book_education_icon_217331.ico')
        self.journal_window.resizable(width=False, height=False)
        self.journal_window.grab_set()

        self.number_books = "--"

        self.cursor.execute("select * from books where \"CNT\">0 order by \"ID\"")
        books = self.cursor.fetchall()

        self.cursor.execute("select * from clients order by \"ID\"")
        clients = self.cursor.fetchall()

        # print(books)

        values_book = []

        for record in books:
            values_book.append(f"{record[0]}: {record[1]}")

        # print(clients)
        values_client = []
        for record in clients:
            values_client.append(f"{record[0]}: {record[1]} {record[2]} {record[3]} {record[4]} {record[5]}")

        books_label = tk.Label(self.journal_window, text='Книга:')
        books_label.grid(row=0, column=0, pady=25, padx=10)
        books_list = ttk.Combobox(self.journal_window, values=values_book, state='readonly', width=55)
        books_list.grid(row=0, column=1)

        clients_label = tk.Label(self.journal_window, text='Читатель:')
        clients_label.grid(row=1, column=0, padx=10)
        clients_list = ttk.Combobox(self.journal_window, values=values_client, state='readonly', width=55)
        clients_list.grid(row=1, column=1)
        clients_list.bind("<<ComboboxSelected>>", self.count_books)
        how_many_books = tk.Label(self.journal_window, text=f"Книг на руках: {self.number_books}")
        how_many_books.grid(row=1, column=2, padx=25, pady=25)

        tk.Button(self.journal_window, text='Добавить',
                  command=lambda: self.insert_record(books_list.get(),
                                                     clients_list.get())).grid(row=3, columnspan=2)

    def count_books(self, event):
        id = int(event.widget.get().split()[0][:-1])
        self.cursor.execute(f"select \"count\" from how_many_books where \"ID\"={id}")
        self.number_books = self.cursor.fetchone()[0]
        self.journal_window.children['!label3']['text'] = f"Книг на руках: {self.number_books}"

    def return_book(self):
        def create_list(event):
            id = int(event.widget.get().split()[-1])
            self.cursor.execute(f"select \"BOOK_ID\", books.\"NAME\", \"DATE_BEG\", journal.\"ID\" " +
                                f"from journal join books on \"BOOK_ID\"=books.\"ID\" " +
                                f"where \"CLIENT_ID\"={id} and \"DATE_RET\" is null order by books.\"NAME\"")

            records_list = [k for k in self.cursor.fetchall()]
            # print(records_list)
            for k in range(len(records_list)):
                records_list[k] = f"{records_list[k][1]}, {records_list[k][2].date()} id: {records_list[k][-1]}"

            record['state'] = 'readonly'
            record['value'] = records_list

        self.journal_window = tk.Toplevel(self.main)
        self.journal_window.grab_set()
        self.journal_window.geometry('450x400')
        self.journal_window.title('Принять книгу')
        self.journal_window.iconbitmap('book_education_icon_217331.ico')
        self.journal_window.resizable(width=False, height=False)

        self.cursor.execute(f"select * from how_many_books where \"count\">0 order by \"LAST_NAME\"")

        clients = self.cursor.fetchall()
        # print(clients)

        for i in range(len(clients)):
            clients[
                i] = f"{clients[i][2]} {clients[i][1]} {clients[i][3]}, {clients[i][-3]} {clients[i][-2]}, id: {clients[i][0]}"

        clients_label = tk.Label(self.journal_window, text='Читатель:')
        clients_label.grid(row=0, column=0, pady=25, padx=10)
        clients_list = ttk.Combobox(self.journal_window, values=clients, state='readonly', width=55)
        clients_list.grid(row=0, column=1)
        clients_list.bind("<<ComboboxSelected>>", create_list)

        record_label = tk.Label(self.journal_window, text='Книга:')
        record_label.grid(row=1, column=0, padx=10)
        record = ttk.Combobox(self.journal_window, state='disabled', width=55)
        record.grid(row=1, column=1)

        calendar_selector = tkcalendar.Calendar(self.journal_window, selectmode='day')
        calendar_selector.grid(row=2, column=0, columnspan=2, pady=25, padx=0)

        tk.Button(self.journal_window, text='Принять',
                  command=lambda: self.update_record(record.get().split()[-1], calendar_selector.get_date())).grid(
            row=3, columnspan=2)

    def update_record(self, record_id, date):
        try:
            self.cursor.execute(f"update journal set \"DATE_RET\"='{date}' where \"ID\"={record_id}")

            self.cursor.execute(
                f"update books set \"CNT\"=\"CNT\"+1 where \"ID\" in (select distinct \"BOOK_ID\" from journal where journal.\"ID\"={record_id})")

            self.connection.commit()
            self.changed = True

            self.cursor.execute(
                f"select sum(book_types.\"FINE\" * (CAST(journal.\"DATE_RET\" as date) - CAST (journal.\"DATE_END\" as date))) from journal LEFT JOIN books on journal.\"BOOK_ID\"=books.\"ID\" LEFT JOIN book_types on books.\"TYPE_ID\"=book_types.\"ID\" where journal.\"ID\"={record_id}")
            fine = self.cursor.fetchone()[0]

            if fine > 0:
                box.showwarning("ШТРАФ", f"Сумма штрафа: {fine} рублей")

        except psycopg2.InternalError:
            box.showerror("Ошибка даты", "Книга возвращена раньше даты выдачи")
            self.connection.rollback()
        except:
            box.showerror("Ошибка", "Какая-то неизвестная доселе ошибка")
            self.connection.rollback()
        finally:
            self.journal_window.destroy()
