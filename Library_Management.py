import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Establish connection to MySQL
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='library_management',  # Replace with your database name
            user='root',                    # Replace with your MySQL username
            password='seshaa3'             # Replace with your MySQL password
        )
        if conn.is_connected():
            print("Connected to MySQL database")
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Log user login activity
def log_login_activity(user_id):
    conn = connect_to_database()
    cursor = conn.cursor()
    login_time = datetime.now()

    query = "INSERT INTO login_activity (user_id, login_time) VALUES (%s, %s)"
    values = (user_id, login_time)

    cursor.execute(query, values)
    conn.commit()
    conn.close()

# User login function
def login_user(mobile, password):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "SELECT id FROM users WHERE mobile = %s AND password = %s"
    cursor.execute(query, (mobile, password))

    user = cursor.fetchone()

    if user:
        log_login_activity(user[0])  # Log the login activity
        messagebox.showinfo("Success", "Login successful!")
        open_book_selection(user[0])  # Open the book selection after login
    else:
        messagebox.showerror("Error", "Invalid credentials!")

    conn.close()

# Admin login function
def admin_login(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "SELECT * FROM admins WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()

    if admin:
        messagebox.showinfo("Success", "Admin login successful!")
        open_admin_portal()
    else:
        messagebox.showerror("Error", "Invalid admin credentials!")

    conn.close()

# Open the list of books (after user login)
def open_book_selection(user_id):
    book_selection_window = tk.Tk()
    book_selection_window.title("Available Books")
    book_selection_window.geometry("400x400")
    book_selection_window.configure(bg='#e6f7ff')

    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, author FROM books WHERE available = TRUE")
    books = cursor.fetchall()

    tk.Label(book_selection_window, text="Available Books", font=("Arial", 16), bg='#e6f7ff').pack(pady=10)

    def borrow_book(book_id):
        borrow_book_function(book_id, user_id)

    for book in books:
        tk.Label(book_selection_window, text=f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}", bg='#e6f7ff').pack()
        tk.Button(book_selection_window, text="Borrow", command=lambda b_id=book[0]: borrow_book(b_id)).pack(pady=5)

    # Return Book Section
    tk.Label(book_selection_window, text="Return a Book", font=("Arial", 14), bg='#e6f7ff').pack(pady=10)

    tk.Label(book_selection_window, text="Book ID:", bg='#e6f7ff').pack()
    entry_return_id = tk.Entry(book_selection_window)
    entry_return_id.pack()

    tk.Button(book_selection_window, text="Return Book", command=lambda: return_book(entry_return_id.get(), user_id)).pack(pady=10)

    book_selection_window.mainloop()

# Function to borrow a book
def borrow_book_function(book_id, user_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    # Check if the book is available
    cursor.execute("SELECT available FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()

    if book and book[0]:  # If book is available
        cursor.execute("UPDATE books SET available = %s WHERE id = %s", (False, book_id))
        cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_date) VALUES (%s, %s, %s)",
                       (user_id, book_id, datetime.now()))
        conn.commit()
        messagebox.showinfo("Success", "Book borrowed successfully!")
    else:
        messagebox.showerror("Error", "Book is not available!")

    conn.close()

# Function to return a book
def return_book(book_id, user_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM borrowed_books WHERE user_id = %s AND book_id = %s", (user_id, book_id))
    borrowed = cursor.fetchone()

    if borrowed:
        cursor.execute("UPDATE books SET available = %s WHERE id = %s", (True, book_id))
        cursor.execute("DELETE FROM borrowed_books WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        conn.commit()
        messagebox.showinfo("Success", "Book returned successfully!")
    else:
        messagebox.showerror("Error", "You did not borrow this book!")

    conn.close()

# Admin Portal for adding/removing books
def open_admin_portal():
    admin_window = tk.Tk()
    admin_window.title("Admin Portal - Manage Books")
    admin_window.geometry("400x300")
    admin_window.configure(bg='#f5f5dc')

    # Add book section
    tk.Label(admin_window, text="Add a Book", font=("Arial", 14), bg='#f5f5dc').pack(pady=10)

    tk.Label(admin_window, text="Title:", bg='#f5f5dc').pack()
    entry_title = tk.Entry(admin_window)
    entry_title.pack()

    tk.Label(admin_window, text="Author:", bg='#f5f5dc').pack()
    entry_author = tk.Entry(admin_window)
    entry_author.pack()

    tk.Button(admin_window, text="Add Book", command=lambda: add_book(entry_title.get(), entry_author.get())).pack(pady=10)

    # Remove book section
    tk.Label(admin_window, text="Remove a Book", font=("Arial", 14), bg='#f5f5dc').pack(pady=10)

    tk.Label(admin_window, text="Book ID:", bg='#f5f5dc').pack()
    entry_book_id = tk.Entry(admin_window)
    entry_book_id.pack()

    tk.Button(admin_window, text="Remove Book", command=lambda: remove_book(entry_book_id.get())).pack(pady=10)

    admin_window.mainloop()

# Book management (Admin feature)
def add_book(title, author):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "INSERT INTO books (title, author, available) VALUES (%s, %s, %s)"
    values = (title, author, True)

    cursor.execute(query, values)
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Book added successfully!")

def remove_book(book_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    query = "DELETE FROM books WHERE id = %s"
    cursor.execute(query, (book_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Book with ID {book_id} has been removed!")

# Register Page for new users
def open_register_page():
    register_window = tk.Tk()
    register_window.title("Register")
    register_window.geometry("300x400")
    register_window.configure(bg='#e6ffe6')

    # Registration form
    tk.Label(register_window, text="Name:", bg='#e6ffe6').pack(pady=5)
    entry_name = tk.Entry(register_window)
    entry_name.pack()

    tk.Label(register_window, text="Email:", bg='#e6ffe6').pack(pady=5)
    entry_email = tk.Entry(register_window)
    entry_email.pack()

    tk.Label(register_window, text="Mobile:", bg='#e6ffe6').pack(pady=5)
    entry_mobile = tk.Entry(register_window)
    entry_mobile.pack()

    tk.Label(register_window, text="Address:", bg='#e6ffe6').pack(pady=5)
    entry_address = tk.Entry(register_window)
    entry_address.pack()

    tk.Label(register_window, text="Password:", bg='#e6ffe6').pack(pady=5)
    entry_password = tk.Entry(register_window, show="*")
    entry_password.pack()

    tk.Button(register_window, text="Register", command=lambda: register_user(
        entry_name.get(),
        entry_email.get(),
        entry_mobile.get(),
        entry_password.get(),
        entry_address.get()
    )).pack(pady=10)

    register_window.mainloop()

# Login Page
def open_login_window():
    login_window = tk.Tk()
    login_window.title("Library Login")
    login_window.geometry("300x300")
    login_window.configure(bg='#ffe6e6')

    tk.Label(login_window, text="Mobile Number or Username:", bg='#ffe6e6').pack(pady=10)
    entry_mobile_or_username = tk.Entry(login_window)
    entry_mobile_or_username.pack()

    tk.Label(login_window, text="Password:", bg='#ffe6e6').pack(pady=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()

    def process_login():
        input_text = entry_mobile_or_username.get()
        input_password = entry_password.get()

        if input_text == "admin" and input_password == "password123":
            admin_login(input_text, input_password)
        else:
            login_user(input_text, input_password)

    tk.Button(login_window, text="Login", command=process_login).pack(pady=10)
    tk.Button(login_window, text="Register", command=open_register_page).pack(pady=10)

    login_window.mainloop()

# Start the application with the login window
open_login_window()
