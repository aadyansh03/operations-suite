# -*- coding: utf-8 -*-
"""
Exhar Formulations - Internal Ops Desk
Author: Aadyansh Sinha
Last Modified: Aug 2026
Note: Production-grade desktop manager for stock tracking, raw batch formulation, and farm ledger.
"""

from datetime import datetime
import os
import re
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Local DB path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "exhar_suite.db")


# -------------------------------------------------------------
# DATABASE SETUP & ACCESS HELPERS
# -------------------------------------------------------------
def get_db():
    """Context-safe DB connection helper."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Initializes tables matching the existing project schema."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Table 1: Farm Credit & Receivables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS farm_credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                total_amount REAL NOT NULL,
                amount_paid REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """
        )

        # Table 2: Inventory & Batches
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                batch_no TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                expiry_date TEXT NOT NULL
            )
        """
        )
        conn.commit()


# -------------------------------------------------------------
# MAIN APPLICATION INTERFACE
# -------------------------------------------------------------
class ExharSuiteApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Exhar Formulations | Central Operations Suite")
        self.master.geometry("960x640")
        self.master.minsize(850, 520)

        # Natural theme palette for agro-veterinary formulations
        self.brand_green = "#1b5e20"
        self.btn_green = "#2e7d32"
        self.bg_muted = "#f4f7f4"

        self._init_theme_styles()
        self._render_header_banner()

        # Tab Navigation
        self.tabs_container = ttk.Notebook(self.master)
        self.tabs_container.pack(
            fill="both", expand=True, padx=12, pady=(0, 10)
        )

        self.tab_credit = tk.Frame(self.tabs_container, bg=self.bg_muted)
        self.tab_inventory = tk.Frame(self.tabs_container, bg=self.bg_muted)
        self.tab_calc = tk.Frame(self.tabs_container, bg=self.bg_muted)

        self.tabs_container.add(self.tab_credit, text="  Farm Credit Ledger  ")
        self.tabs_container.add(
            self.tab_inventory, text="  Inventory & Expiries  "
        )
        self.tabs_container.add(self.tab_calc, text="  Batch Calculator  ")

        # Build sub-views
        self._build_credit_tab()
        self._build_inventory_tab()
        self._build_calc_tab()

    def _init_theme_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#e2e8f0", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=[18, 6],
            background="#cbd5e1",
            foreground="#334155",
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.brand_green)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", rowheight=24, font=("Segoe UI", 9))

    def _render_header_banner(self):
        banner = tk.Frame(self.master, bg=self.brand_green, pady=12, padx=15)
        banner.pack(fill="x", side="top", pady=(0, 8))

        lbl_title = tk.Label(
            banner,
            text="EXHAR FORMULATIONS",
            font=("Helvetica", 14, "bold"),
            fg="#ffffff",
            bg=self.brand_green,
        )
        lbl_title.pack(side="left")

        lbl_sub = tk.Label(
            banner,
            text="| Central Operations & Production Suite",
            font=("Helvetica", 10),
            fg="#c8e6c9",
            bg=self.brand_green,
        )
        lbl_sub.pack(side="left", padx=8, pady=(2, 0))

    # =========================================================
    # TAB 1: FARM CREDIT LEDGER
    # =========================================================
    def _build_credit_tab(self):
        form_frame = tk.LabelFrame(
            self.tab_credit,
            text=" Record New Transaction ",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_muted,
            padx=12,
            pady=8,
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        # Row 0
        tk.Label(form_frame, text="Farm Name:", bg=self.bg_muted).grid(
            row=0, column=0, sticky="w", pady=4
        )
        self.ent_farm = tk.Entry(form_frame, width=22)
        self.ent_farm.grid(row=0, column=1, padx=6, pady=4)

        tk.Label(form_frame, text="Contact:", bg=self.bg_muted).grid(
            row=0, column=2, sticky="w", pady=4
        )
        self.ent_contact = tk.Entry(form_frame, width=20)
        self.ent_contact.grid(row=0, column=3, padx=6, pady=4)

        # Row 1
        tk.Label(form_frame, text="Total Bill (₹):", bg=self.bg_muted).grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.ent_total = tk.Entry(form_frame, width=22)
        self.ent_total.grid(row=1, column=1, padx=6, pady=4)

        tk.Label(form_frame, text="Paid (₹):", bg=self.bg_muted).grid(
            row=1, column=2, sticky="w", pady=4
        )
        self.ent_paid = tk.Entry(form_frame, width=20)
        self.ent_paid.grid(row=1, column=3, padx=6, pady=4)

        # Row 2
        tk.Label(
            form_frame, text="Due Date (YYYY-MM-DD):", bg=self.bg_muted
        ).grid(row=2, column=0, sticky="w", pady=4)
        self.ent_due = tk.Entry(form_frame, width=22)
        self.ent_due.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_due.grid(row=2, column=1, padx=6, pady=4)

        btn_add = tk.Button(
            form_frame,
            text="Add Record",
            command=self.add_credit,
            bg=self.btn_green,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
        )
        btn_add.grid(row=2, column=3, sticky="e", pady=6)

        # Treeview Ledger
        cols = ("id", "farm", "contact", "total", "paid", "bal", "due", "status")
        self.tree_credit = ttk.Treeview(
            self.tab_credit, columns=cols, show="headings", height=11
        )

        headers = {
            "id": "ID",
            "farm": "Farm Name",
            "contact": "Contact",
            "total": "Total Bill",
            "paid": "Paid",
            "bal": "Balance Due",
            "due": "Due Date",
            "status": "Status",
        }
        col_widths = {
            "id": 40,
            "farm": 180,
            "contact": 110,
            "total": 100,
            "paid": 100,
            "bal": 100,
            "due": 100,
            "status": 90,
        }

        for col, title in headers.items():
            self.tree_credit.heading(col, text=title)
            self.tree_credit.column(col, width=col_widths[col], anchor="center")
        self.tree_credit.column("farm", anchor="w")

        # Scrollbar
        sb_credit = ttk.Scrollbar(
            self.tab_credit, orient="vertical", command=self.tree_credit.yview
        )
        self.tree_credit.configure(yscrollcommand=sb_credit.set)
        self.tree_credit.pack(
            side="left", fill="both", expand=True, padx=(10, 0), pady=6
        )
        sb_credit.pack(side="right", fill="y", padx=(0, 10), pady=6)

        self.load_credit()

    def add_credit(self):
        farm = self.ent_farm.get().strip()
        contact = self.ent_contact.get().strip()
        total_raw = self.ent_total.get().strip()
        paid_raw = self.ent_paid.get().strip()
        due = self.ent_due.get().strip()

        if not farm or not contact:
            messagebox.showwarning(
                "Missing Data", "Please fill in Farm Name and Contact Number."
            )
            return

        if not re.match(r"^[0-9+\-\s]{7,15}$", contact):
            messagebox.showwarning(
                "Invalid Contact", "Please enter a valid phone/contact number."
            )
            return

        try:
            total = float(total_raw)
            paid = float(paid_raw) if paid_raw else 0.0
            if total < 0 or paid < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Total and Paid amounts must be valid non-negative numbers."
            )
            return

        try:
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Date Error", "Due Date must be in YYYY-MM-DD format."
            )
            return

        status = "Cleared" if (total - paid) <= 0.01 else "Pending"

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO farm_credit (farm_name, contact, total_amount, amount_paid, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (farm, contact, total, paid, due, status),
            )
            conn.commit()

        # Clean form inputs
        self.ent_farm.delete(0, tk.END)
        self.ent_contact.delete(0, tk.END)
        self.ent_total.delete(0, tk.END)
        self.ent_paid.delete(0, tk.END)
        self.load_credit()

    def load_credit(self):
        for row in self.tree_credit.get_children():
            self.tree_credit.delete(row)

        with get_db() as conn:
            rows = conn.execute(
                "SELECT id, farm_name, contact, total_amount, amount_paid, due_date, status FROM farm_credit ORDER BY id DESC"
            ).fetchall()
            for row in rows:
                bal = max(0.0, row[3] - row[4])
                self.tree_credit.insert(
                    "",
                    "end",
                    values=(
                        row[0],
                        row[1],
                        row[2],
                        f"₹{row[3]:,.2f}",
                        f"₹{row[4]:,.2f}",
                        f"₹{bal:,.2f}",
                        row[5],
                        row[6],
                    ),
                )

    # =========================================================
    # TAB 2: INVENTORY & EXPIRIES
    # =========================================================
    def _build_inventory_tab(self):
        form_frame = tk.LabelFrame(
            self.tab_inventory,
            text=" Add New Stock Batch ",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_muted,
            padx=12,
            pady=8,
        )
        form_frame.pack(fill="x", padx=10, pady=8)

        # Row 0
        tk.Label(form_frame, text="Product Name:", bg=self.bg_muted).grid(
            row=0, column=0, sticky="w", pady=4
        )
        self.ent_prod = tk.Entry(form_frame, width=22)
        self.ent_prod.grid(row=0, column=1, padx=6, pady=4)

        tk.Label(form_frame, text="Batch No:", bg=self.bg_muted).grid(
            row=0, column=2, sticky="w", pady=4
        )
        self.ent_batch = tk.Entry(form_frame, width=20)
        self.ent_batch.grid(row=0, column=3, padx=6, pady=4)

        # Row 1
        tk.Label(form_frame, text="Quantity:", bg=self.bg_muted).grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.ent_qty = tk.Entry(form_frame, width=22)
        self.ent_qty.grid(row=1, column=1, padx=6, pady=4)

        tk.Label(form_frame, text="Expiry Date:", bg=self.bg_muted).grid(
            row=1, column=2, sticky="w", pady=4
        )
        self.ent_exp = tk.Entry(form_frame, width=20)
        self.ent_exp.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_exp.grid(row=1, column=3, padx=6, pady=4)

        btn_stock = tk.Button(
            form_frame,
            text="Add Stock",
            command=self.add_inventory,
            bg=self.btn_green,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
        )
        btn_stock.grid(row=1, column=4, padx=10, pady=4)

        # Inventory Table
        cols = ("id", "product", "batch", "qty", "expiry", "status")
        self.tree_inv = ttk.Treeview(
            self.tab_inventory, columns=cols, show="headings", height=11
        )

        headers = {
            "id": "ID",
            "product": "Product Name",
            "batch": "Batch No",
            "qty": "Quantity",
            "expiry": "Expiry Date",
            "status": "Shelf Status",
        }
        for col, title in headers.items():
            self.tree_inv.heading(col, text=title)
            self.tree_inv.column(col, width=120, anchor="center")
        self.tree_inv.column("product", width=220, anchor="w")

        # Scrollbar
        sb_inv = ttk.Scrollbar(
            self.tab_inventory, orient="vertical", command=self.tree_inv.yview
        )
        self.tree_inv.configure(yscrollcommand=sb_inv.set)
        self.tree_inv.pack(
            side="left", fill="both", expand=True, padx=(10, 0), pady=6
        )
        sb_inv.pack(side="right", fill="y", padx=(0, 10), pady=6)

        self.load_inventory()

    def add_inventory(self):
        prod = self.ent_prod.get().strip()
        batch = self.ent_batch.get().strip()
        qty_raw = self.ent_qty.get().strip()
        exp = self.ent_exp.get().strip()

        if not prod or not batch:
            messagebox.showwarning(
                "Missing Fields", "Please enter product name and batch number."
            )
            return

        try:
            qty = int(qty_raw)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Quantity must be a positive whole integer."
            )
            return

        try:
            datetime.strptime(exp, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Date Error", "Expiry Date must be in YYYY-MM-DD format."
            )
            return

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO inventory (product_name, batch_no, quantity, expiry_date)
                VALUES (?, ?, ?, ?)
            """,
                (prod, batch, qty, exp),
            )
            conn.commit()

        self.ent_prod.delete(0, tk.END)
        self.ent_batch.delete(0, tk.END)
        self.ent_qty.delete(0, tk.END)
        self.load_inventory()

    def load_inventory(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)

        today = datetime.now().date()
        with get_db() as conn:
            rows = conn.execute(
                "SELECT id, product_name, batch_no, quantity, expiry_date FROM inventory ORDER BY expiry_date ASC"
            ).fetchall()
            for row in rows:
                try:
                    exp_dt = datetime.strptime(row[4], "%Y-%m-%d").date()
                    delta = (exp_dt - today).days
                    if delta < 0:
                        status = "EXPIRED"
                    elif delta <= 60:
                        status = "Expiring Soon"
                    else:
                        status = "Good"
                except ValueError:
                    status = "Check Date"

                self.tree_inv.insert(
                    "",
                    "end",
                    values=(row[0], row[1], row[2], row[3], row[4], status),
                )

    # =========================================================
    # TAB 3: BATCH CALCULATOR
    # =========================================================
    def _build_calc_tab(self):
        frame = tk.Frame(self.tab_calc, bg=self.bg_muted, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Select Formulation Formula:",
            bg=self.bg_muted,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=10)

        self.product_var = tk.StringVar()
        self.formulas = {
            "Exhar-Cal Gel (Per Liter)": {
                "Calcium Carbonate": (43.5, "g"),
                "Phosphorus": (21.7, "g"),
                "Vitamin D3": (8000, "IU"),
                "Syrup Base": (920.0, "ml"),
            },
            "MastiGuard Bolus (Per 1000 Boluses)": {
                "Serratiopeptidase": (15.0, "g"),
                "Herbal Extract Blend": (500.0, "g"),
                "Starch Binder": (150.0, "g"),
            },
        }

        self.dd_products = ttk.Combobox(
            frame,
            textvariable=self.product_var,
            values=list(self.formulas.keys()),
            width=38,
            state="readonly",
        )
        self.dd_products.grid(row=0, column=1, sticky="w", pady=10)
        self.dd_products.current(0)

        tk.Label(
            frame,
            text="Target Batch Multiplier:",
            bg=self.bg_muted,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=10)

        self.ent_multiplier = tk.Entry(frame, width=15)
        self.ent_multiplier.insert(0, "1")
        self.ent_multiplier.grid(row=1, column=1, sticky="w", pady=10)

        tk.Button(
            frame,
            text="Calculate Raw Materials",
            command=self.calculate_batch,
            bg=self.brand_green,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
        ).grid(row=2, column=1, sticky="w", pady=10)

        self.calc_result = tk.Text(
            frame,
            height=11,
            width=62,
            font=("Consolas", 10),
            bg="#f8fafc",
            relief="solid",
            bd=1,
        )
        self.calc_result.grid(
            row=3, column=0, columnspan=2, pady=15, sticky="w"
        )

    def calculate_batch(self):
        try:
            prod = self.product_var.get()
            mult = float(self.ent_multiplier.get().strip())
            if mult <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Multiplier must be a valid positive number."
            )
            return

        recipe = self.formulas.get(prod, {})
        timestamp = datetime.now().strftime("%d-%b-%Y %H:%M")

        self.calc_result.delete("1.0", tk.END)
        self.calc_result.insert(
            tk.END, f"{'=' * 58}\n"
        )
        self.calc_result.insert(
            tk.END, f"  RAW MATERIAL REQUIREMENT (BOM)\n"
        )
        self.calc_result.insert(
            tk.END, f"  Generated: {timestamp}\n"
        )
        self.calc_result.insert(
            tk.END, f"{'=' * 58}\n"
        )
        self.calc_result.insert(tk.END, f"Product         : {prod}\n")
        self.calc_result.insert(tk.END, f"Batch Multiplier: {mult:,.2f}x\n\n")

        for ing, (amt, unit) in recipe.items():
            total_amt = amt * mult
            self.calc_result.insert(
                tk.END, f"  ➤ {ing:<26} : {total_amt:>10,.2f} {unit}\n"
            )

        self.calc_result.insert(
            tk.END, f"{'=' * 58}\n"
        )


# -------------------------------------------------------------
# APPLICATION RUNNER
# -------------------------------------------------------------
if __name__ == "__main__":
    init_database()
    root = tk.Tk()
    app = ExharSuiteApp(root)
    root.mainloop()
