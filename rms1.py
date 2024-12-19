from tkinter import *
from tkinter import ttk
import psycopg2
from tkinter import messagebox
from datetime import datetime
import sys
import os
from models import session, Customer, Employee, Order, User, OrderDetail, Menu, Payment
from sqlalchemy import func, and_

def main():
    win = Tk()
    app = LoginPage(win)
    win.mainloop()

class LoginPage:
    def __init__(self, win):
        self.win = win
        self.win.geometry("1350x750+0+0")
        self.win.title("Restaurant Management System")

        self.title_label = Label(self.win, text="Restaurant Management System", font=('Arial', 35, 'bold'),
                                 bg ="lightgrey", bd=8, relief = GROOVE)
        self.title_label.pack(side=TOP, fill=X)

        self.main_frame = Frame(self.win, bg="lightgrey", bd=6, relief = GROOVE)
        self.main_frame.place(x=250, y=150, width=800, height=450)

        self.login_lbl = Label(self.main_frame, text="Login", bd=6, relief=GROOVE, anchor=CENTER,
                               bg="lightgrey", font=('sans-serif', 25, 'bold'))
        self.login_lbl.pack(side=TOP, fill=X)

        self.entry_frame = LabelFrame(self.main_frame, text="Enter Details", bd=6, relief = GROOVE, bg="lightgrey",
                                      font=('sans-serif', 18))
        self.entry_frame.pack(fill=BOTH, expand=TRUE)

        self.entus_lbl=Label(self.entry_frame, text="Enter Username: ", bg="lightgrey",
                             font=('sans-serif', 15))
        self.entus_lbl.grid(row=0, column=0, padx=2,pady=2)

        username = StringVar()
        password = StringVar()

        self.entus_ent = Entry(self.entry_frame, font=('sans-serif', 15), bd=6, textvariable=username)
        self.entus_ent.grid(row=0, column=1, padx=2, pady=2)

        self.entpass_lbl = Label(self.entry_frame, text="Enter Password: ", bg="lightgrey", font=('sans-serif', 15))
        self.entpass_lbl.grid(row=1, column=0, padx=2, pady=2)

        self.entpass_ent = Entry(self.entry_frame, font=('sans-serif', 15), bd=6, textvariable=password, show="*")
        self.entpass_ent.grid(row=1, column=1, padx=2, pady=2)

        def open_admin_panel():
            admin_window = Toplevel(self.win)
            AdminPanel(admin_window)

        def check_login():
            try:
                connection = psycopg2.connect(
                    dbname="postgres",
                    user="postgres",
                    password="password",
                    host="localhost",
                    port=5432
                )
                cursor = connection.cursor()
                query = "SELECT role FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username.get(), password.get()))
                result = cursor.fetchone()

                if result:
                    role = result[0]
                    if role == 'admin':
                        messagebox.showinfo("Success", "Welcome Admin!")
                        open_admin_panel()
                    else:
                        messagebox.showinfo("Success", "Welcome!")
                else:
                    messagebox.showerror("Error", "Invalid username or password")
                    username.set("")
                    password.set("")
            except Exception as e:
                messagebox.showerror("Error", f"Database connection error: {e}")
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'connection' in locals() and connection:
                    connection.close()

        def reset():
            username.set("")
            password.set("")

        self.button_frame = LabelFrame(self.entry_frame, text="Options", font = ('Arial', 15), bg="lightgrey", bd=7, relief=GROOVE)
        self.button_frame.place(x=20, y=100, width=730, height=85)

        self.login_btn = Button(self.button_frame, text="Login", font=('Arial', 15), bd=5, width=15, command=check_login)
        self.login_btn.grid(row=0, column=0, padx=20, pady=2)

        self.reset_btn = Button(self.button_frame, text="Reset", font=('Arial', 15), bd=5, width=15, command=reset)
        self.reset_btn.grid(row=0, column=1, padx=20, pady=2)

class AdminPanel:
    def __init__(self, win):
        self.win = win
        self.win.geometry("1200x700")
        self.win.title("Admin Panel")

        title = Label(self.win, text="Admin Panel", font=("Arial", 25, "bold"), bg="lightblue", relief="groove")
        title.pack(side=TOP, fill=X)

        self.main_frame = Frame(self.win, bd=4, relief="ridge", bg="lightgrey")
        self.main_frame.place(x=20, y=70, width=1150, height=600)

        # Верхняя панель с элементами управления
        control_frame = Frame(self.main_frame, bg="lightgrey")
        control_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)

        Label(control_frame, text="Select Table:", font=("Arial", 12), bg="lightgrey").grid(row=0, column=0, padx=5)
        self.table_combobox = ttk.Combobox(control_frame, font=("Arial", 12), state="readonly")
        # Добавим Payments
        self.table_combobox["values"] = ("Customers", "Employees", "Orders", "Payments")
        self.table_combobox.grid(row=0, column=1, padx=5)
        self.table_combobox.bind("<<ComboboxSelected>>", self.load_data)

        # Поиск
        Label(control_frame, text="Search:", font=("Arial", 12), bg="lightgrey").grid(row=0, column=2, padx=5)
        self.search_var = StringVar()
        self.search_entry = Entry(control_frame, textvariable=self.search_var, font=("Arial",12), width=20)
        self.search_entry.grid(row=0, column=3, padx=5)

        # Кнопки
        self.show_btn = Button(control_frame, text="Отобразить данные", command=self.load_data)
        self.show_btn.grid(row=1, column=0, padx=5, pady=5)
        self.search_btn = Button(control_frame, text="Поиск", command=self.search_data)
        self.search_btn.grid(row=1, column=1, padx=5, pady=5)

        self.add_btn = Button(control_frame, text="Добавить запись", command=self.add_record)
        self.add_btn.grid(row=1, column=2, padx=5, pady=5)
        self.update_btn = Button(control_frame, text="Обновить запись", command=self.update_record)
        self.update_btn.grid(row=1, column=3, padx=5, pady=5)

        self.delete_btn = Button(control_frame, text="Удалить запись", command=self.delete_selected)
        self.delete_btn.grid(row=1, column=4, padx=5, pady=5)

        self.compute_btn = Button(control_frame, text="Выполнить вычисление", command=self.compute_totals)
        self.compute_btn.grid(row=1, column=5, padx=5, pady=5)

        self.sort_btn = Button(control_frame, text="Сортировка", command=self.sort_data)
        self.sort_btn.grid(row=1, column=6, padx=5, pady=5)

        self.cross_btn = Button(control_frame, text="Перекрестный запрос", command=self.cross_query)
        self.cross_btn.grid(row=1, column=7, padx=5, pady=5)

        # Treeview для отображения данных
        self.tree = ttk.Treeview(self.main_frame, columns=("col1","col2","col3","col4"), show="headings")
        self.tree.place(x=10, y=130, width=1120, height=450)

        self.add_columns_default()

    def add_columns_default(self):
        # Изначально зададим колонки
        self.tree.heading("col1", text="Column 1")
        self.tree.heading("col2", text="Column 2")
        self.tree.heading("col3", text="Column 3")
        self.tree.heading("col4", text="Column 4")

    def get_selected_table(self):
        return self.table_combobox.get()

    def load_data(self, event=None):
        selected_table = self.get_selected_table()
        self.tree.delete(*self.tree.get_children())

        if selected_table == "Customers":
            self.tree["columns"] = ("ID", "Name", "Phone", "Email")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Name", text="Name")
            self.tree.heading("Phone", text="Phone Number")
            self.tree.heading("Email", text="Email")

            customers = session.query(Customer).all()
            for c in customers:
                self.tree.insert("", "end", values=(c.CustomerID, c.Name, c.PhoneNumber, c.Email))

        elif selected_table == "Employees":
            self.tree["columns"] = ("ID", "Name", "Position", "Contact")
            self.tree.heading("ID", text="ID")
            self.tree.heading("Name", text="Name")
            self.tree.heading("Position", text="Position")
            self.tree.heading("Contact", text="Contact Info")

            employees = session.query(Employee).all()
            for e in employees:
                self.tree.insert("", "end", values=(e.EmployeeID, e.Name, e.Position, e.ContactInfo))

        elif selected_table == "Orders":
            self.tree["columns"] = ("ID", "Date", "CustomerID", "Total")
            self.tree.heading("ID", text="Order ID")
            self.tree.heading("Date", text="Order Date")
            self.tree.heading("CustomerID", text="Customer ID")
            self.tree.heading("Total", text="Total Amount")

            orders = session.query(Order).all()
            for o in orders:
                self.tree.insert("", "end", values=(o.OrderID, o.OrderDate, o.CustomerID, o.TotalAmount))

        elif selected_table == "Payments":
            self.tree["columns"] = ("PaymentID", "OrderID", "Amount", "PaymentStatus")
            self.tree.heading("PaymentID", text="Payment ID")
            self.tree.heading("OrderID", text="Order ID")
            self.tree.heading("Amount", text="Amount")
            self.tree.heading("PaymentStatus", text="Payment Status")

            payments = session.query(Payment).all()
            for p in payments:
                self.tree.insert("", "end", values=(p.PaymentID, p.OrderID, p.Amount, p.PaymentStatus))

    def search_data(self):
        selected_table = self.get_selected_table()
        search_value = self.search_var.get().strip()

        self.tree.delete(*self.tree.get_children())

        if selected_table == "Customers":
            # Поиск по имени
            customers = session.query(Customer).filter(Customer.Name.ilike(f"%{search_value}%")).all()
            for c in customers:
                self.tree.insert("", "end", values=(c.CustomerID, c.Name, c.PhoneNumber, c.Email))

        elif selected_table == "Employees":
            # Поиск по имени сотрудника
            employees = session.query(Employee).filter(Employee.Name.ilike(f"%{search_value}%")).all()
            for e in employees:
                self.tree.insert("", "end", values=(e.EmployeeID, e.Name, e.Position, e.ContactInfo))

        elif selected_table == "Orders":
            # Поиск по дате
            try:
                search_date = datetime.strptime(search_value, "%Y-%m-%d").date()
                orders = session.query(Order).filter(Order.OrderDate == search_date).all()
            except:
                orders = []
            for o in orders:
                self.tree.insert("", "end", values=(o.OrderID, o.OrderDate, o.CustomerID, o.TotalAmount))

        elif selected_table == "Payments":
            # Поиск по PaymentStatus
            payments = session.query(Payment).filter(Payment.PaymentStatus.ilike(f"%{search_value}%")).all()
            for p in payments:
                self.tree.insert("", "end", values=(p.PaymentID, p.OrderID, p.Amount, p.PaymentStatus))

    def add_record(self):
        selected_table = self.get_selected_table()
        AddUpdateWindow(self.win, selected_table, "add", self.refresh_data)

    def update_record(self):
        selected_table = self.get_selected_table()
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "No record selected")
            return
        item = self.tree.item(selection[0])
        vals = item['values']
        AddUpdateWindow(self.win, selected_table, "update", self.refresh_data, vals)

    def delete_selected(self):
        selected_table = self.get_selected_table()
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        vals = item['values']

        if selected_table == "Customers":
            cust_id = vals[0]
            c = session.query(Customer).filter_by(CustomerID=cust_id).first()
            if c:
                session.delete(c)
                session.commit()
        elif selected_table == "Employees":
            emp_id = vals[0]
            e = session.query(Employee).filter_by(EmployeeID=emp_id).first()
            if e:
                session.delete(e)
                session.commit()
        elif selected_table == "Orders":
            order_id = vals[0]
            o = session.query(Order).filter_by(OrderID=order_id).first()
            if o:
                # удаляем связанные детали
                for od in o.orderdetails:
                    session.delete(od)
                # удаляем платеж
                p = session.query(Payment).filter_by(OrderID=o.OrderID).first()
                if p:
                    session.delete(p)
                session.delete(o)
                session.commit()
        elif selected_table == "Payments":
            pay_id = vals[0]
            p = session.query(Payment).filter_by(PaymentID=pay_id).first()
            if p:
                session.delete(p)
                session.commit()

        self.refresh_data()

    def refresh_data(self):
        self.load_data()

    def compute_totals(self):
        # Пример: подсчитать общую сумму заказов за все время
        # Если выбраны Orders, считаем сумму TotalAmount
        selected_table = self.get_selected_table()
        if selected_table == "Orders":
            result = session.query(func.sum(Order.TotalAmount)).scalar()
            messagebox.showinfo("Computation Result", f"Total sales: {result}")
        elif selected_table == "Payments":
            # Например, посчитаем сумму всех платежей
            result = session.query(func.sum(Payment.Amount)).scalar()
            messagebox.showinfo("Computation Result", f"Total payments: {result}")
        else:
            messagebox.showinfo("Info", "No computation defined for this table.")

    def sort_data(self):
        selected_table = self.get_selected_table()
        self.tree.delete(*self.tree.get_children())
        if selected_table == "Customers":
            customers = session.query(Customer).order_by(Customer.Name).all()
            for c in customers:
                self.tree.insert("", "end", values=(c.CustomerID, c.Name, c.PhoneNumber, c.Email))
        elif selected_table == "Employees":
            employees = session.query(Employee).order_by(Employee.Name).all()
            for e in employees:
                self.tree.insert("", "end", values=(e.EmployeeID, e.Name, e.Position, e.ContactInfo))
        elif selected_table == "Orders":
            orders = session.query(Order).order_by(Order.OrderDate).all()
            for o in orders:
                self.tree.insert("", "end", values=(o.OrderID, o.OrderDate, o.CustomerID, o.TotalAmount))
        elif selected_table == "Payments":
            payments = session.query(Payment).order_by(Payment.PaymentID).all()
            for p in payments:
                self.tree.insert("", "end", values=(p.PaymentID, p.OrderID, p.Amount, p.PaymentStatus))

    def cross_query(self):
        # Пример перекрестного запроса: Показать имя клиента, дату заказа и блюда из Menu
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("CustomerName", "OrderDate", "ItemName", "Quantity")
        self.tree.heading("CustomerName", text="Customer Name")
        self.tree.heading("OrderDate", text="Order Date")
        self.tree.heading("ItemName", text="Item Name")
        self.tree.heading("Quantity", text="Quantity")

        query = (session.query(Customer.Name, Order.OrderDate, Menu.Name, OrderDetail.Quantity)
                 .join(Order, Customer.CustomerID == Order.CustomerID)
                 .join(OrderDetail, Order.OrderID == OrderDetail.OrderID)
                 .join(Menu, Menu.MenuItemID == OrderDetail.MenuItemID)
                 .all())
        for row in query:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))


class AddUpdateWindow:
    def __init__(self, parent, table, mode, refresh_callback, vals=None):
        self.table = table
        self.mode = mode
        self.refresh_callback = refresh_callback
        self.top = Toplevel(parent)
        self.top.title("Add/Update Record")
        self.entries = {}
        if self.table == "Customers":
            Label(self.top, text="Name").grid(row=0,column=0)
            self.entries["Name"] = Entry(self.top)
            self.entries["Name"].grid(row=0,column=1)

            Label(self.top, text="Phone").grid(row=1,column=0)
            self.entries["PhoneNumber"] = Entry(self.top)
            self.entries["PhoneNumber"].grid(row=1,column=1)

            Label(self.top, text="Email").grid(row=2,column=0)
            self.entries["Email"] = Entry(self.top)
            self.entries["Email"].grid(row=2,column=1)

            Label(self.top, text="Password").grid(row=3,column=0)
            self.entries["Password"] = Entry(self.top)
            self.entries["Password"].grid(row=3,column=1)

            if self.mode == "update" and vals:
                self.record_id = vals[0]
                self.entries["Name"].insert(0, vals[1])
                self.entries["PhoneNumber"].insert(0, vals[2])
                self.entries["Email"].insert(0, vals[3])
                self.entries["Password"].insert(0, "userpassword")

        elif self.table == "Employees":
            Label(self.top, text="Name").grid(row=0,column=0)
            self.entries["Name"] = Entry(self.top)
            self.entries["Name"].grid(row=0,column=1)

            Label(self.top, text="Position").grid(row=1,column=0)
            self.entries["Position"] = Entry(self.top)
            self.entries["Position"].grid(row=1,column=1)

            Label(self.top, text="ContactInfo").grid(row=2,column=0)
            self.entries["ContactInfo"] = Entry(self.top)
            self.entries["ContactInfo"].grid(row=2,column=1)

            if self.mode == "update" and vals:
                self.record_id = vals[0]
                self.entries["Name"].insert(0, vals[1])
                self.entries["Position"].insert(0, vals[2])
                self.entries["ContactInfo"].insert(0, vals[3])

        elif self.table == "Orders":
            Label(self.top, text="CustomerID").grid(row=0,column=0)
            self.entries["CustomerID"] = Entry(self.top)
            self.entries["CustomerID"].grid(row=0,column=1)

            Label(self.top, text="OrderDate (YYYY-MM-DD)").grid(row=1,column=0)
            self.entries["OrderDate"] = Entry(self.top)
            self.entries["OrderDate"].grid(row=1,column=1)

            Label(self.top, text="TotalAmount").grid(row=2,column=0)
            self.entries["TotalAmount"] = Entry(self.top)
            self.entries["TotalAmount"].grid(row=2,column=1)

            if self.mode == "update" and vals:
                self.record_id = vals[0]
                self.entries["CustomerID"].insert(0, vals[2])
                self.entries["OrderDate"].insert(0, vals[1])
                self.entries["TotalAmount"].insert(0, vals[3])

        elif self.table == "Payments":
            Label(self.top, text="OrderID").grid(row=0,column=0)
            self.entries["OrderID"] = Entry(self.top)
            self.entries["OrderID"].grid(row=0,column=1)

            Label(self.top, text="Amount").grid(row=1,column=0)
            self.entries["Amount"] = Entry(self.top)
            self.entries["Amount"].grid(row=1,column=1)

            Label(self.top, text="PaymentStatus (Paid/Pending/Failed)").grid(row=2,column=0)
            self.entries["PaymentStatus"] = Entry(self.top)
            self.entries["PaymentStatus"].grid(row=2,column=1)

            if self.mode == "update" and vals:
                # vals = (PaymentID, OrderID, Amount, PaymentStatus)
                self.record_id = vals[0]
                self.entries["OrderID"].insert(0, vals[1])
                self.entries["Amount"].insert(0, vals[2])
                self.entries["PaymentStatus"].insert(0, vals[3])

        Button(self.top, text="Save", command=self.save_record).grid(row=10, column=0, columnspan=2)

    def save_record(self):
        if self.table == "Customers":
            name = self.entries["Name"].get()
            phone = self.entries["PhoneNumber"].get()
            email = self.entries["Email"].get()
            pwd = self.entries["Password"].get()
            if self.mode == "add":
                c = Customer(Name=name, PhoneNumber=phone, Email=email, Password=pwd)
                session.add(c)
                session.commit()
            else:
                c = session.query(Customer).filter_by(CustomerID=self.record_id).first()
                if c:
                    c.Name = name
                    c.PhoneNumber = phone
                    c.Email = email
                    c.Password = pwd
                    session.commit()

        elif self.table == "Employees":
            name = self.entries["Name"].get()
            pos = self.entries["Position"].get()
            cont = self.entries["ContactInfo"].get()
            if self.mode == "add":
                e = Employee(Name=name, Position=pos, ContactInfo=cont)
                session.add(e)
                session.commit()
            else:
                e = session.query(Employee).filter_by(EmployeeID=self.record_id).first()
                if e:
                    e.Name = name
                    e.Position = pos
                    e.ContactInfo = cont
                    session.commit()

        elif self.table == "Orders":
            cust_id = int(self.entries["CustomerID"].get())
            order_date = datetime.strptime(self.entries["OrderDate"].get(), "%Y-%m-%d").date()
            total = float(self.entries["TotalAmount"].get())
            if self.mode == "add":
                o = Order(CustomerID=cust_id, OrderDate=order_date, TotalAmount=total)
                session.add(o)
                session.commit()
            else:
                o = session.query(Order).filter_by(OrderID=self.record_id).first()
                if o:
                    o.CustomerID = cust_id
                    o.OrderDate = order_date
                    o.TotalAmount = total
                    session.commit()

        elif self.table == "Payments":
            order_id = int(self.entries["OrderID"].get())
            amount = float(self.entries["Amount"].get())
            status = self.entries["PaymentStatus"].get()
            if status not in ('Paid','Pending','Failed'):
                messagebox.showerror("Error", "PaymentStatus must be one of: Paid, Pending, Failed")
                return
            if self.mode == "add":
                # Убедимся, что для этого OrderID нет уже записи в Payments
                existing = session.query(Payment).filter_by(OrderID=order_id).first()
                if existing:
                    messagebox.showerror("Error", f"Order {order_id} already has a payment!")
                    return
                p = Payment(OrderID=order_id, Amount=amount, PaymentStatus=status)
                session.add(p)
                session.commit()
            else:
                p = session.query(Payment).filter_by(PaymentID=self.record_id).first()
                if p:
                    p.OrderID = order_id
                    p.Amount = amount
                    p.PaymentStatus = status
                    session.commit()

        self.refresh_callback()
        self.top.destroy()

if __name__ == "__main__":
    main()
