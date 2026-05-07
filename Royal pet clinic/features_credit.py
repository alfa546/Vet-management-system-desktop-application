import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style
from datetime import datetime
import os

# ──────────────────────────────────────────────
#  UDHAAR / CREDIT MANAGER
# ──────────────────────────────────────────────
def open_credit_manager(app):
    win = app._new_window("Udhaar Book", 850, 600)

    top_frame = tk.Frame(win, bg=COLORS["card_bg"], pady=12, padx=20, highlightthickness=1, highlightbackground=COLORS["border"])
    top_frame.pack(fill="x", padx=20, pady=(14, 6))

    tk.Label(top_frame, text="Udhaar / Credit Management", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack()

    # ── Table ──
    tree_frame = tk.Frame(win, bg=COLORS["background"])
    tree_frame.pack(fill="both", expand=True, padx=20, pady=(6, 6))

    cols = ("ID", "Name", "Phone", "Amount", "Date", "Day", "Status")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")
    widths = {"ID": 40, "Name": 130, "Phone": 110, "Amount": 90, "Date": 140, "Day": 90, "Status": 90}
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=widths[c], anchor="center")

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    # Configure tag for 'Paid' status
    tree.tag_configure('paid', foreground=COLORS["success"])

    def refresh_table():
        for item in tree.get_children():
            tree.delete(item)
        for c in app.db.get_all_credit():
            # BUG FIX: Robust date parsing
            try:
                raw_date = c[4] or ""
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
            
            status = c[5] if len(c) > 5 else "Unpaid"
            tags = ('paid',) if status == "Paid" else ()
            
            tree.insert("", "end", values=(
                c[0], c[1], c[2], f"Rs {float(c[3] or 0):.0f}", c[4], day_name, status
            ), tags=tags)

    refresh_table()

    # ── Actions ──
    def add_credit_action():
        add_win = tk.Toplevel(win)
        add_win.title("Add New Udhaar")
        add_win.geometry("350x400")
        add_win.configure(bg=COLORS["card_bg"])
        add_win.grab_set()

        tk.Label(add_win, text="Customer Name:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(pady=(20,2))
        name_ent = tk.Entry(add_win, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        name_ent.pack(pady=5, ipady=4)

        tk.Label(add_win, text="Phone Number:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(pady=(10,2))
        phone_ent = tk.Entry(add_win, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        phone_ent.pack(pady=5, ipady=4)

        tk.Label(add_win, text="Amount (Rs):", font=FONTS["label"], bg=COLORS["card_bg"]).pack(pady=(10,2))
        amount_ent = tk.Entry(add_win, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        amount_ent.pack(pady=5, ipady=4)

        def save_credit(event=None):
            try:
                n = name_ent.get().strip()
                p = phone_ent.get().strip()
                a = float(amount_ent.get())
                if not n or not p: raise ValueError("Name and Phone are required")
                app.db.add_credit(n, p, a)
                refresh_table()
                add_win.destroy()
                messagebox.showinfo("Success", "Udhaar recorded successfully!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid Input: {e}")

        save_btn = tk.Button(add_win, text="Save Udhaar", command=save_credit)
        apply_button_style(save_btn, "accent")
        save_btn.pack(pady=20)
        
        name_ent.bind("<Return>", lambda e: phone_ent.focus_set())
        phone_ent.bind("<Return>", lambda e: amount_ent.focus_set())
        amount_ent.bind("<Return>", save_credit)
        name_ent.focus_set()

    def delete_credit_action():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select records to delete.")
        if messagebox.askyesno("Confirm", f"Delete {len(sel)} record(s)?"):
            for item in sel:
                app.db.delete_credit(tree.item(item)['values'][0])
            refresh_table()
            messagebox.showinfo("Done", f"{len(sel)} record(s) removed.")

    def mark_paid_action():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select records to mark as paid.")
        if messagebox.askyesno("Confirm", f"Mark {len(sel)} record(s) as Paid?"):
            for item in sel:
                app.db.mark_credit_paid(tree.item(item)['values'][0])
            refresh_table()
            messagebox.showinfo("Done", f"{len(sel)} record(s) marked as Paid.")

    def open_add():
        add_credit_action()

    def open_delete():
        app._require_admin(delete_credit_action)
        
    def open_mark_paid():
        app._require_admin(mark_paid_action)

    btn_bar = tk.Frame(win, bg=COLORS["background"])
    btn_bar.pack(pady=12)

    add_btn = tk.Button(btn_bar, text="➕ Add Udhaar", command=open_add)
    apply_button_style(add_btn, "accent")
    add_btn.pack(side="left", padx=10)

    paid_btn = tk.Button(btn_bar, text="✅ Mark as Paid", command=open_mark_paid)
    apply_button_style(paid_btn, "secondary")
    paid_btn.pack(side="left", padx=10)

    del_btn = tk.Button(btn_bar, text="🗑  Delete", command=open_delete)
    apply_button_style(del_btn, "danger")
    del_btn.pack(side="left", padx=10)

