import customtkinter as c
from tkinter import *
import  matplotlib.pyplot as plt
import sqlite3 as sql
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Global Value
Value = 0

# Functions
def create_table():
    conn =  sql.connect('expenses.db')
    cur_obj=conn.cursor()
    cur_obj.execute("CREATE TABLE IF NOT EXISTS expenses(Date TEXT, Category TEXT, Amount INTEGER);")
    conn.commit
    conn.close()
    
def add():
    global Value
    date = en1.get()
    cat = en2.get()
    amt = en3.get()

    if date == "" or cat == "" or amt == "":
        mb.showwarning("Warning", "Please fill all fields")
        return

    try:
        amt = int(amt) 
    except ValueError:
        mb.showerror("Error", "Amount must be a number")
        return

    conn = sql.connect('expenses.db')
    cur_obj = conn.cursor()
    create_table()
    cur_obj.execute("INSERT INTO expenses (Date, Category, Amount) VALUES (?, ?, ?)", (date, cat, amt))
    conn.commit()

    # Update total expenses
    Value += amt
    update_total_expenses()

    # Refresh the Listbox with updated data
    fetch_data()

    conn.close()

    # Clear the entry fields
    en1.set("")
    en2.set("")
    en3.set("")

    mb.showinfo("Info", "Expenses Added Successfully!")

def delete():
    try:
        selected_item_index = lb.curselection()[0]  
        if selected_item_index > 1: 
            data=lb.get(selected_item_index)
            data_values = data.split('|')
            date = data_values[0].strip()
            cat = data_values[1].strip()
            amt = data_values[2].strip()

            lb.delete(selected_item_index)

            conn = sql.connect('expenses.db')
            cur_obj = conn.cursor()

            # Delete the corresponding row from the database
            cur_obj.execute("DELETE FROM expenses WHERE Date = ? AND Category = ? AND Amount = ?", (date, cat, amt))
            conn.commit()

            # Update total expenses
            global Value
            Value -= int(amt)
            update_total_expenses()

            conn.close()

            mb.showinfo("Info", "Entry Deleted Successfully!")
        else:
            mb.showwarning("Warning", "You cannot delete the header or separator")
    except IndexError:
        mb.showwarning("Warning", "Please select an item to delete")

def fetch_data():
 
    lb.delete(2, END)

    conn = sql.connect('expenses.db')
    cur_obj = conn.cursor()


    cur_obj.execute("SELECT * FROM expenses")
    rows = cur_obj.fetchall()

    global Value
    Value = 0

    # Insert data into the Listbox
    for row in rows:
        lb.insert(END, f" {row[0]:<15} | {row[1]:<15} | {row[2]:<15}")
        Value += row[2]

    # Update total expenses
    update_total_expenses()

    conn.close()

def update_total_expenses():
    total_lb.delete(0, END)
    total_lb.insert(END, f"Total Expenses: ${Value}")

def save_as_pdf():
    conn = sql.connect('expenses.db')
    cur_obj = conn.cursor()

    # Fetch all data from the database
    cur_obj.execute("SELECT * FROM expenses")
    rows = cur_obj.fetchall()

    if not rows:
        mb.showwarning("Warning", "No data to save!")
        return

    # Prompt user to select a save location and file name
    file_path = fd.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

    if not file_path:
        return  # User cancelled the save

    # Create a PDF using reportlab
    pdf = canvas.Canvas(file_path, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    # Title
    pdf.drawString(200, 750, "Personal Expenses")

    # Column headers
    pdf.drawString(100, 730, "Date")
    pdf.drawString(250, 730, "Category")
    pdf.drawString(400, 730, "Amount")

    y = 710

    # Add rows to the PDF
    for row in rows:
        pdf.drawString(100, y, row[0])
        pdf.drawString(250, y, row[1])
        pdf.drawString(400, y, str(row[2]))
        y -= 20  # Move to the next line

        if y < 50:
            pdf.showPage()  # Add a new page if space runs out
            pdf.setFont("Helvetica", 12)
            y = 750

    pdf.save()
    mb.showinfo("Info", f"Data saved successfully at {file_path}")

    conn.close()

def visualize():
    conn = sql.connect('expenses.db')
    cur_obj = conn.cursor()

    cur_obj.execute("SELECT Category, SUM(Amount) FROM expenses GROUP BY Category")
    data = cur_obj.fetchall()

    if not data:
        mb.showwarning("Warning", "No data to visualize")
        return

    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.figure(figsize=(8, 6))
    plt.bar(categories, amounts, color='skyblue')
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.show()
    fetch_data()
    conn.close()

# root window
root = c.CTk()
root.geometry('650x500')
root.config(bg="Green")
root.title('Personal Expenses Tracker')
script_dir = os.path.dirname(os.path.abspath(__file__))
icon = os.path.join(script_dir,"c:\\MINI PROJECT 2024 -JCAS\\personal expenses tracker", "spending.ico")
root.iconbitmap(icon)
root.resizable(False, False)

# labels
c.CTkLabel(root, text="Date", fg_color='green', bg_color="green").grid(row=0, column=0, padx=10, pady=10)
c.CTkLabel(root, text="Expenses", fg_color='green', bg_color="Green").grid(row=1, column=0, padx=10, pady=10)
c.CTkLabel(root, text="Amount", fg_color='green', bg_color="Green").grid(row=2, column=0, padx=10, pady=10)

# Small Listbox to display total expenses
total_lb = Listbox(root, width=30, height=1)
total_lb.place(x=70, y=300)

# Entry fields
en1 = StringVar()
en2 = StringVar()
en3 = StringVar()
c.CTkEntry(root, textvariable=en1, bg_color="green").grid(row=0, column=1, padx=10, pady=10)
c.CTkEntry(root, textvariable=en2, bg_color="green").grid(row=1, column=1, padx=10, pady=10)
c.CTkEntry(root, textvariable=en3, bg_color="Green").grid(row=2, column=1, padx=10, pady=10)

# Buttons
c.CTkButton(root, text='Add', width=40, fg_color="light pink", text_color="Blue", corner_radius=16, bg_color="green", command=add).grid(row=5, column=0, padx=40, pady=10)
c.CTkButton(root, text='Delete', width=40, fg_color="light pink", text_color="Blue", corner_radius=12, bg_color="green", command=delete).grid(row=6, column=0, padx=40, pady=20)
c.CTkButton(root, text='Save as PDF', width=50, fg_color="light pink", text_color="Blue", corner_radius=12, bg_color="green", command=save_as_pdf).grid(row=5, column=1)
c.CTkButton(root, text='Visualize', width=50, fg_color="light pink", text_color="Blue", corner_radius=12, bg_color="green", command=visualize).grid(row=6, column=1)

# Listbox for displaying expenses
lb = Listbox(root, width=40, height=23)
lb.insert(0, "       Date         |       Category      |       Amount")
lb.insert(1, "-------------------------------------------------------")
lb.place(x=340, y=15)

# Load the data into Listbox when the app starts
create_table()
fetch_data()

# Run the GUI event loop
root.mainloop()