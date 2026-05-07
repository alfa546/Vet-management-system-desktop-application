import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style
from datetime import datetime
import os

# ──────────────────────────────────────────────
#  KHARCHA / EXPENSE MANAGER
# ──────────────────────────────────────────────
def open_expense_manager(app):
    win = app._new_window("Kharcha / Expenses", 700, 500)

    top_frame = tk.Frame(win, bg=COLORS["card_bg"], pady=12, padx=20, highlightthickness=1, highlightbackground=COLORS["border"])
    top_frame.pack(fill="x", padx=20, pady=(14, 6))

    tk.Label(top_frame, text="Daily Expense Tracker", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack()

    # ── Table ──
    tree_frame = tk.Frame(win, bg=COLORS["background"])
    tree_frame.pack(fill="both", expand=True, padx=20, pady=(6, 6))

    cols = ("ID", "Description", "Amount", "Date", "Day")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")
    widths = {"ID": 40, "Description": 260, "Amount": 90, "Date": 140, "Day": 90}
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=widths[c], anchor="center")

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def refresh_table():
        for item in tree.get_children():
            tree.delete(item)
        for e in app.db.get_all_expenses():
            # BUG FIX: Robust date parsing
            try:
                raw_date = e[3] or ""
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(raw_date, fmt)
                        day_name = dt.strftime("%A")
                        break
                    except ValueError:
                        continue
                else:
                    day_name = "N/A"
            except Exception:
                day_name = "N/A"
            tree.insert("", "end", values=(e[0], e[1], f"Rs {float(e[2] or 0):.0f}", e[3], day_name))

    refresh_table()

    # ── Actions ──
    def open_add_expense():
        add_win = tk.Toplevel(win)
        add_win.title("Add Kharcha")
        add_win.geometry("350x300")
        add_win.configure(bg=COLORS["card_bg"])
        add_win.grab_set()

        tk.Label(add_win, text="Kharcha Description:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(pady=(20,2))
        desc_ent = tk.Entry(add_win, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        desc_ent.pack(pady=5, ipady=4)

        tk.Label(add_win, text="Amount (Rs):", font=FONTS["label"], bg=COLORS["card_bg"]).pack(pady=(10,2))
        amount_ent = tk.Entry(add_win, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        amount_ent.pack(pady=5, ipady=4)

        def save_expense(event=None):
            try:
                d = desc_ent.get().strip()
                a = float(amount_ent.get())
                if not d: raise ValueError("Description is required")
                app.db.add_expense(d, a)
                refresh_table()
                add_win.destroy()
                messagebox.showinfo("Success", "Kharcha added successfully!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid Input: {e}")

        save_btn = tk.Button(add_win, text="Save Kharcha", command=save_expense)
        apply_button_style(save_btn, "accent")
        save_btn.pack(pady=20)
        
        desc_ent.bind("<Return>", lambda e: amount_ent.focus_set())
        amount_ent.bind("<Return>", save_expense)
        desc_ent.focus_set()

    def delete_expense():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete!")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            for item in selected:
                expense_id = tree.item(item, "values")[0]
                app.db.delete_expense(expense_id)
            refresh_table()
            messagebox.showinfo("Success", "Kharcha deleted successfully!")

    btn_bar = tk.Frame(win, bg=COLORS["background"])
    btn_bar.pack(pady=12)

    add_btn = tk.Button(btn_bar, text="➕ Add Kharcha", command=open_add_expense)
    apply_button_style(add_btn, "accent")
    add_btn.pack(side="left", padx=10, pady=10)

    del_btn = tk.Button(btn_bar, text="🗑️ Delete Kharcha", command=lambda: app._require_admin(delete_expense))
    apply_button_style(del_btn, "danger")
    del_btn.pack(side="left", padx=10, pady=10)

