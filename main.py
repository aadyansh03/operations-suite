# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 18:20:48 2026

@author: Aadyansh Sinha
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- DATABASE SETUP ---
DB_NAME = "exhar_suite.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table 1: Finance / Credit
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_credit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_name TEXT NOT NULL,
            contact TEXT NOT NULL,
            total_amount REAL NOT NULL,
            amount_paid REAL NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    # Table 2: Inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- MAIN APPLICATION CLASS ---
class ExharSuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exhar Formulations - Operations Suite")
        self.root.geometry("900x600")
        
        # Style configurations
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#f4f7f4")
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", "#1b5e20")], foreground=[("selected", "white")])

        # App Header
        # App Header
        header = tk.Frame(self.root, bg="#1b5e20", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Exhar Formulations | Central Operations Suite", font=("Helvetica", 16, "bold"), fg="white", bg="#1b5e20").pack()

        # Tab Setup
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Tabs
        self.tab_credit = tk.Frame(self.notebook, bg="#f4f7f4")
        self.tab_inventory = tk.Frame(self.notebook, bg="#f4f7f4")
        self.tab_calc = tk.Frame(self.notebook, bg="#f4f7f4")

        self.notebook.add(self.tab_credit, text="Farm Credit Ledger")
        self.notebook.add(self.tab_inventory, text="Inventory & Expiries")
        self.notebook.add(self.tab_calc, text="Batch Calculator")

        # Build UI for each tab
        self.build_credit_tab()
        self.build_inventory_tab()
        self.build_calc_tab()

    # ==========================================
    # TAB 1: FARM CREDIT LEDGER
    # ==========================================
    def build_credit_tab(self):
        form_frame = tk.LabelFrame(self.tab_credit, text=" Record New Transaction ", font=("Helvetica", 10, "bold"), bg="#f4f7f4", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Farm Name:", bg="#f4f7f4").grid(row=0, column=0, pady=5)
        self.ent_farm = tk.Entry(form_frame, width=20)
        self.ent_farm.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Contact:", bg="#f4f7f4").grid(row=0, column=2, pady=5)
        self.ent_contact = tk.Entry(form_frame, width=20)
        self.ent_contact.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Total Bill (₹):", bg="#f4f7f4").grid(row=1, column=0, pady=5)
        self.ent_total = tk.Entry(form_frame, width=20)
        self.ent_total.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Paid (₹):", bg="#f4f7f4").grid(row=1, column=2, pady=5)
        self.ent_paid = tk.Entry(form_frame, width=20)
        self.ent_paid.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Due Date:", bg="#f4f7f4").grid(row=2, column=0, pady=5)
        self.ent_due = tk.Entry(form_frame, width=20)
        self.ent_due.insert(0, "YYYY-MM-DD")
        self.ent_due.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Add Record", command=self.add_credit, bg="#2e7d32", fg="white", width=15).grid(row=2, column=3, pady=5)

        # Treeview
        self.tree_credit = ttk.Treeview(self.tab_credit, columns=("id", "farm", "contact", "total", "paid", "bal", "due", "status"), show="headings", height=10)
        for col in self.tree_credit["columns"]:
            self.tree_credit.heading(col, text=col.title())
            self.tree_credit.column(col, width=100)
        self.tree_credit.pack(fill="both", expand=True, padx=10, pady=5)
        self.load_credit()

    def add_credit(self):
        try:
            farm = self.ent_farm.get()
            contact = self.ent_contact.get()
            total = float(self.ent_total.get())
            paid = float(self.ent_paid.get())
            due = self.ent_due.get()
            
            status = "Cleared" if (total - paid) <= 0 else "Pending"
            
            conn = sqlite3.connect(DB_NAME)
            conn.execute("INSERT INTO farm_credit (farm_name, contact, total_amount, amount_paid, due_date, status) VALUES (?,?,?,?,?,?)", 
                         (farm, contact, total, paid, due, status))
            conn.commit()
            conn.close()
            self.load_credit()
        except Exception as e:
            messagebox.showerror("Error", "Check your inputs. Numbers required for amounts.")

    def load_credit(self):
        for row in self.tree_credit.get_children(): self.tree_credit.delete(row)
        conn = sqlite3.connect(DB_NAME)
        for row in conn.execute("SELECT * FROM farm_credit").fetchall():
            bal = row[3] - row[4]
            self.tree_credit.insert("", "end", values=(row[0], row[1], row[2], f"₹{row[3]}", f"₹{row[4]}", f"₹{bal}", row[5], row[6]))
        conn.close()

    # ==========================================
    # TAB 2: INVENTORY & EXPIRIES
    # ==========================================
    def build_inventory_tab(self):
        form_frame = tk.LabelFrame(self.tab_inventory, text=" Add New Stock Batch ", font=("Helvetica", 10, "bold"), bg="#f4f7f4", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Product Name:", bg="#f4f7f4").grid(row=0, column=0, pady=5)
        self.ent_prod = tk.Entry(form_frame, width=20)
        self.ent_prod.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Batch No:", bg="#f4f7f4").grid(row=0, column=2, pady=5)
        self.ent_batch = tk.Entry(form_frame, width=20)
        self.ent_batch.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Quantity:", bg="#f4f7f4").grid(row=1, column=0, pady=5)
        self.ent_qty = tk.Entry(form_frame, width=20)
        self.ent_qty.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Expiry Date:", bg="#f4f7f4").grid(row=1, column=2, pady=5)
        self.ent_exp = tk.Entry(form_frame, width=20)
        self.ent_exp.insert(0, "YYYY-MM-DD")
        self.ent_exp.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(form_frame, text="Add Stock", command=self.add_inventory, bg="#2e7d32", fg="white", width=15).grid(row=1, column=4, padx=10)

        # Treeview
        self.tree_inv = ttk.Treeview(self.tab_inventory, columns=("id", "product", "batch", "qty", "expiry"), show="headings", height=10)
        for col in self.tree_inv["columns"]:
            self.tree_inv.heading(col, text=col.title())
        self.tree_inv.pack(fill="both", expand=True, padx=10, pady=5)
        self.load_inventory()

    def add_inventory(self):
        try:
            prod = self.ent_prod.get()
            batch = self.ent_batch.get()
            qty = int(self.ent_qty.get())
            exp = self.ent_exp.get()
            
            conn = sqlite3.connect(DB_NAME)
            conn.execute("INSERT INTO inventory (product_name, batch_no, quantity, expiry_date) VALUES (?,?,?,?)", (prod, batch, qty, exp))
            conn.commit()
            conn.close()
            self.load_inventory()
        except:
            messagebox.showerror("Error", "Quantity must be an integer.")

    def load_inventory(self):
        for row in self.tree_inv.get_children(): self.tree_inv.delete(row)
        conn = sqlite3.connect(DB_NAME)
        for row in conn.execute("SELECT * FROM inventory").fetchall():
            self.tree_inv.insert("", "end", values=row)
        conn.close()

    # ==========================================
    # TAB 3: BATCH CALCULATOR
    # ==========================================
    def build_calc_tab(self):
        frame = tk.Frame(self.tab_calc, bg="#f4f7f4", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Select Formulation Formula:", bg="#f4f7f4", font=("Helvetica", 11, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        self.product_var = tk.StringVar()
        products = ["Exhar-Cal Gel (Per Liter)", "MastiGuard Bolus (Per 1000 Boluses)"]
        self.dd_products = ttk.Combobox(frame, textvariable=self.product_var, values=products, width=35)
        self.dd_products.grid(row=0, column=1, pady=10)
        self.dd_products.current(0)

        tk.Label(frame, text="Target Batch Multiplier:", bg="#f4f7f4", font=("Helvetica", 11, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.ent_multiplier = tk.Entry(frame, width=15)
        self.ent_multiplier.insert(0, "1")
        self.ent_multiplier.grid(row=1, column=1, sticky="w", pady=10)

        tk.Button(frame, text="Calculate Raw Materials", command=self.calculate_batch, bg="#1b5e20", fg="white", font=("Helvetica", 10, "bold")).grid(row=2, column=1, sticky="w", pady=10)

        self.calc_result = tk.Text(frame, height=10, width=55, font=("Courier", 11), bg="#e8f5e9")
        self.calc_result.grid(row=3, column=0, columnspan=2, pady=15)

    def calculate_batch(self):
        # Base recipes per 1 Unit (1 Liter or 1000 Boluses)
        formulas = {
            "Exhar-Cal Gel (Per Liter)": {"Calcium Carbonate": "43.5 g", "Phosphorus": "21.7 g", "Vitamin D3": "8000 IU", "Syrup Base": "920 ml"},
            "MastiGuard Bolus (Per 1000 Boluses)": {"Serratiopeptidase": "15 g", "Herbal Extract Blend": "500 g", "Starch Binder": "150 g"}
        }
        
        try:
            prod = self.product_var.get()
            mult = float(self.ent_multiplier.get())
            recipe = formulas[prod]
            
            self.calc_result.delete(1.0, tk.END)
            self.calc_result.insert(tk.END, f"--- RAW MATERIAL REQUIREMENT ---\nProduct: {prod}\nBatch Multiplier: {mult}\n\n")
            
            for ing, amt in recipe.items():
                value, unit = amt.split(" ")
                total_amt = float(value) * mult
                self.calc_result.insert(tk.END, f"➤ {ing}: {total_amt:.2f} {unit}\n")
        except ValueError:
            messagebox.showerror("Error", "Multiplier must be a valid number.")

# --- ENTRY POINT ---
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExharSuiteApp(root)
    root.mainloop()