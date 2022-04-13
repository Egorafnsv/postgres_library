import tkinter as tk
import tkinter.ttk as ttk
from MenuBook import MenuBook
from MenuClients import MenuClients
from MenuJournal import MenuJournal


class MainWindow:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.main = tk.Tk()
        self.table_frame = tk.Frame(self.main)
        self.change_frame = tk.Frame(self.main)
        self.btn_frame = tk.Frame(self.main)
        self.menu_frame = tk.Frame(self.main)
        self.table_state = tk.IntVar()
        self.table_state.set(0)

        self.main_window()

    def main_window(self):
        self.main.geometry('1100x500')
        self.main.title('Library')
        self.main.iconbitmap('book_education_icon_217331.ico')
        self.change_frame.pack(pady=30)

        self.table_frame.pack(pady=10)
        self.menu_frame.pack()

        t1 = tk.Radiobutton(self.change_frame, text='Книги', font=('Arial', 11), variable=self.table_state, value=0,
                            command=self.change)
        t1.pack(side=tk.LEFT)

        t2 = tk.Radiobutton(self.change_frame, text='Читатели', font=('Arial', 11), variable=self.table_state, value=1,
                            command=self.change)
        t2.pack(side=tk.LEFT, padx=25)

        t3 = tk.Radiobutton(self.change_frame, text='Журнал', font=('Arial', 11), variable=self.table_state, value=2,
                            command=self.change)
        t3.pack(side=tk.LEFT)

        self.change()

        self.main.mainloop()

    def change(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        if self.table_state.get() == 0:
            self.show_books()

        elif self.table_state.get() == 1:
            self.show_clients()

        elif self.table_state.get() == 2:
            self.show_journals()

    def create_table(self, sql_req, columns, display_columns, real_names):
        table = ttk.Treeview(self.table_frame, show='headings', columns=columns, height=10)

        scrl_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=table.yview)
        scrl_y.pack(side=tk.RIGHT, fill='y')

        scrl_x = ttk.Scrollbar(self.table_frame, orient="horizontal", command=table.xview)
        scrl_x.pack(side=tk.BOTTOM, fill='x')

        table.configure(yscrollcommand=scrl_y.set)
        table.configure(xscrollcommand=scrl_x.set)

        for i in range(len(columns)):
            table.heading(columns[i], text=real_names[i])
            table.column(columns[i], width=200)

        self.cursor.execute(sql_req)

        for i in self.cursor.fetchall():
            table.insert(parent='', index='end', text='',
                         values=i)

        table['displaycolumns'] = display_columns

        return table

    def check_update(self, menu_class):
        if menu_class.changed:
            self.change()
        elif menu_class.state != self.table_state.get():
            return
        else:
            self.main.after(1000, lambda: self.check_update(menu_class))

    def show_books(self):
        columns = ("id", "Name", "count", "Type")
        real_names = ("id", "Название", "Количество", "Тип книги")
        req = """ select * from books order by books."NAME" """

        table = self.create_table(req, columns, columns[1:], real_names)
        table.pack()

        manage_books = MenuBook(self.connection, table, self.main)

        self.check_update(manage_books)

        add_btn = tk.Button(self.menu_frame, text='Добавить...', font=('Arial', 10), bg='white',
                            command=manage_books.add_book, width=10)
        add_btn.pack(side=tk.LEFT, pady=10)

        change_btn = tk.Button(self.menu_frame, text='Изменить', font=('Arial', 10), bg='white',
                               command=manage_books.change_book, width=10)
        change_btn.pack(side=tk.LEFT, padx=10)

        delete_btn = tk.Button(self.menu_frame, text='Удалить', font=('Arial', 10), bg='white',
                               command=manage_books.delete_book, width=10)
        delete_btn.pack(side=tk.LEFT)

    def show_clients(self):
        columns = ("id", "First_Name", "Last_Name", "Pat_Name", "Passport_Seria", "Passport_Num")
        real_names = ("id", "Имя", "Фамилия", "Отчество", "Паспорт серия", "Паспорт номер")
        req = """select * from clients order by "LAST_NAME" """

        table = self.create_table(req, columns, columns[1:], real_names)
        table.pack()

        manage_clients = MenuClients(self.connection, table, self.main)

        self.check_update(manage_clients)

        add_client_btn = tk.Button(self.menu_frame, text='Добавить читателя...', font=('Arial', 10), bg='white',
                                   command=manage_clients.add_client)
        add_client_btn.pack(side=tk.LEFT, pady=10)

        delete_btn = tk.Button(self.menu_frame, text='Удалить читателя', font=('Arial', 10), bg='white',
                               command=manage_clients.delete_client)
        delete_btn.pack(side=tk.LEFT, padx=10)

    def show_journals(self):
        columns = ("id", "First_name", "Last_name", "Patr_name", "Book_name", "Date_beg", "Date_end", "Date_ret")

        real_names = (
            "id", "Имя", "Фамилия", "Отчество", "Название книги", "Дата выдачи",
            "Вернуть до", "Дата возвращения")

        req = """select journal."ID", clients."FIRST_NAME", clients."LAST_NAME", clients."PATHER_NAME", books."NAME",
                                CAST(journal."DATE_BEG" as date), CAST(journal."DATE_END" as date), CAST(journal."DATE_RET" as date)
                                 from ((clients join journal on clients."ID" = journal."CLIENT_ID") join
                                books on books."ID"=journal."BOOK_ID") order by journal."DATE_RET" DESC, journal."DATE_BEG" DESC"""

        table = self.create_table(req, columns, columns[1:], real_names)
        table.pack()

        manage_journal = MenuJournal(self.connection, table, self.main)

        self.check_update(manage_journal)

        add_client_btn = tk.Button(self.menu_frame, text='Выдать книгу', font=('Arial', 10), bg='white',
                                   command=manage_journal.add_record)
        add_client_btn.pack(side=tk.LEFT, pady=10)

        return_btn = tk.Button(self.menu_frame, text='Принять книгу', font=('Arial', 10), bg='white',
                               command=manage_journal.return_book)
        return_btn.pack(side=tk.LEFT, pady=10, padx=10)
