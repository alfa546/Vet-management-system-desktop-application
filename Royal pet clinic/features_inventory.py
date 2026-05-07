import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style
from datetime import datetime
import os

def open_add_item(app):
    win = app._new_window("Add New Product", 480, 640)

    form = tk.Frame(win, bg=COLORS["card_bg"], padx=28, pady=18,
                    highlightthickness=1, highlightbackground=COLORS["border"])
    form.pack(padx=30, pady=20, fill="both", expand=True)

    def _field(parent, label_text):
        tk.Label(parent, text=label_text, font=FONTS["label_bold"],
                 bg=COLORS["card_bg"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
        e = tk.Entry(parent, font=FONTS["label"], bg=COLORS["entry_bg"],
                     relief="solid", borderwidth=1)
        e.pack(fill="x", ipady=4)
        return e

    # Category Selection
    tk.Label(form, text="Category", font=FONTS["label_bold"],
             bg=COLORS["card_bg"], fg=COLORS["text"]).pack(anchor="w", pady=(8, 2))
    cat_cb = ttk.Combobox(form, values=["Feed", "Litter", "Vaccine", "Treats", "Accessories"], 
                          font=FONTS["label"], state="readonly")
    cat_cb.pack(fill="x", ipady=2)
    cat_cb.set("Feed")

    name_ent = _field(form, "Product Name")
    sell_ent = _field(form, "Selling Price (Rs)")
    qty_ent  = _field(form, "Quantity")
    
    # Weight field (Initially hidden/shown based on category)
    weight_label = tk.Label(form, text="Weight (kg/Size)", font=FONTS["label_bold"],
                          bg=COLORS["card_bg"], fg=COLORS["text"])
    weight_ent = tk.Entry(form, font=FONTS["label"], bg=COLORS["entry_bg"],
                        relief="solid", borderwidth=1)

    def toggle_weight(e=None):
        if cat_cb.get() in ["Feed", "Litter"]:
            weight_label.pack(anchor="w", pady=(8, 2), after=qty_ent)
            weight_ent.pack(fill="x", ipady=4, after=weight_label)
        else:
            weight_label.pack_forget()
            weight_ent.pack_forget()

    cat_cb.bind("<<ComboboxSelected>>", toggle_weight)
    toggle_weight() # Initial state

    def save():
        try:
            cat = cat_cb.get()
            name = name_ent.get().strip()
            sell_str = sell_ent.get().strip()
            qty_str = qty_ent.get().strip()
            weight = weight_ent.get().strip() if cat in ["Feed", "Litter"] else None
            
            if not name:
                raise ValueError("Product name is required")
            if not sell_str:
                raise ValueError("Selling price is required")
            sell = float(sell_str)
            # BUG FIX: Block zero or negative prices
            if sell <= 0:
                raise ValueError("Selling price must be greater than 0")
            qty = int(qty_str or 0)
            if qty < 0:
                raise ValueError("Quantity cannot be negative")
            
            app.db.add_product(name, cat, sell, qty, weight)
            messagebox.showinfo("Success", f"Product '{name}' added successfully!")
            win.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    save_btn = tk.Button(win, text="Save to Inventory", command=save)
    apply_button_style(save_btn, "secondary")
    save_btn.pack(pady=16)
    
    # BUG FIX: Add Enter key navigation
    name_ent.bind("<Return>", lambda e: sell_ent.focus_set())
    sell_ent.bind("<Return>", lambda e: qty_ent.focus_set())
    qty_ent.bind("<Return>", lambda e: weight_ent.focus_set() if cat_cb.get() in ["Feed", "Litter"] else save())
    weight_ent.bind("<Return>", lambda e: save())
    name_ent.focus_set()

# ──────────────────────────────────────────────
#  INVENTORY MANAGER
# ──────────────────────────────────────────────
def open_inventory_manager(app):
    win = app._new_window("Inventory Manager", 900, 600)
    # ── Search Bar ──
    search_frame = tk.Frame(win, bg=COLORS["card_bg"], padx=20, pady=12,
                            highlightthickness=1, highlightbackground=COLORS["border"])
    search_frame.pack(fill="x", padx=20, pady=(16, 0))

    tk.Label(search_frame, text="🔍 Search Product Name:", font=FONTS["label_bold"],
             bg=COLORS["card_bg"], fg=COLORS["text"]).pack(side="left")
    
    search_ent = tk.Entry(search_frame, font=FONTS["label"], width=30, relief="solid", borderwidth=1)
    search_ent.pack(side="left", padx=10, ipady=4)

    def clear_search():
        search_ent.delete(0, tk.END)
        refresh()

    clear_btn = tk.Button(search_frame, text="Clear", command=clear_search, font=FONTS["small"],
                          bg=COLORS["muted"], fg=COLORS["white"], relief="flat", padx=10)
    clear_btn.pack(side="left")

    tree_frame = tk.Frame(win, bg=COLORS["background"])
    tree_frame.pack(fill="both", expand=True, padx=20, pady=(10, 6))

    cols = ("ID", "Name", "Category", "Price", "Weight", "Stock")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")
    
    # Red highlight tag for search matches
    tree.tag_configure("highlight", foreground="#ef4444", font=FONTS["label_bold"])

    widths = {"ID": 40, "Name": 200, "Category": 120, "Price": 120, "Weight": 100, "Stock": 100}
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=widths[c], anchor="center")

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def refresh(event=None):
        query = search_ent.get().strip().lower()
        for item in tree.get_children():
            tree.delete(item)
        
        data = app.db.get_all_inventory()
        
        # Sort logic: matches go to the top
        if query:
            matches = [p for p in data if query in str(p[1]).lower()]
            others  = [p for p in data if query not in str(p[1]).lower()]
            display_list = matches + others
        else:
            display_list = data

        for p in display_list:
            # p format: (id, name, category, price, weight, qty)
            name = str(p[1]).lower()
            tag = "highlight" if query and query in name else ""
            tree.insert("", "end", values=p, tags=(tag,))

    search_ent.bind("<KeyRelease>", refresh)
    search_ent.bind("<Return>", lambda e: refresh())
    refresh()

    def delete_item_action():
        selected = tree.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select product(s) to delete.")
        if messagebox.askyesno("Confirm", f"Delete {len(selected)} product(s)?"):
            for s in selected:
                app.db.delete_product(tree.item(s)['values'][0])
            refresh()

    def edit_item_action():
        selected = tree.selection()
        if not selected:
            return messagebox.showwarning("Select", "Select a product to edit.")
        if len(selected) > 1:
            return messagebox.showwarning("Selection", "Please select only one product to edit.")
        
        item_values = tree.item(selected[0])['values']
        p_id, p_name, p_cat, p_sell, p_weight, p_stock = item_values

        edit_win = tk.Toplevel(win)
        edit_win.title(f"Edit Product - {p_name}")
        edit_win.geometry("450x620")
        edit_win.configure(bg=COLORS["card_bg"])
        edit_win.grab_set()

        form = tk.Frame(edit_win, bg=COLORS["card_bg"], padx=20, pady=10)
        form.pack(fill="both", expand=True)

        tk.Label(form, text=f"Update {p_name}", font=FONTS["subheader"], bg=COLORS["card_bg"]).pack(pady=10)

        def _ent(label, val):
            tk.Label(form, text=label, font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w")
            e = tk.Entry(form, font=FONTS["label"], width=35)
            e.insert(0, str(val))
            e.pack(pady=5)
            return e

        cat_cb = ttk.Combobox(form, values=["Feed", "Litter", "Vaccine", "Treats", "Accessories"], 
                            font=FONTS["label"], state="readonly", width=33)
        cat_cb.set(p_cat)
        tk.Label(form, text="Category:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w")
        cat_cb.pack(pady=5)

        name_ent = _ent("Name:", p_name)
        sell_ent = _ent("Selling Price:", p_sell)
        qty_ent  = _ent("Quantity:", p_stock)
        
        weight_label = tk.Label(form, text="Weight/Size:", font=FONTS["label"], bg=COLORS["card_bg"])
        weight_ent = tk.Entry(form, font=FONTS["label"], width=35)
        weight_ent.insert(0, str(p_weight) if p_weight and str(p_weight) != "None" else "")

        def toggle_edit_weight(e=None):
            if cat_cb.get() in ["Feed", "Litter"]:
                weight_label.pack(anchor="w")
                weight_ent.pack(pady=5)
            else:
                weight_label.pack_forget()
                weight_ent.pack_forget()

        cat_cb.bind("<<ComboboxSelected>>", toggle_edit_weight)
        toggle_edit_weight()

        def save_edit():
            try:
                cat = cat_cb.get()
                n = name_ent.get().strip()
                sell_str = sell_ent.get().strip()
                qty_str = qty_ent.get().strip()
                w = weight_ent.get().strip() if cat in ["Feed", "Litter"] else None
                
                if not n:
                    raise ValueError("Name cannot be empty")
                if not sell_str:
                    raise ValueError("Selling price is required")
                s = float(sell_str)
                # BUG FIX: Block zero or negative prices in edit too
                if s <= 0:
                    raise ValueError("Selling price must be greater than 0")
                q = int(qty_str or 0)
                if q < 0:
                    raise ValueError("Quantity cannot be negative")
                
                app.db.update_product(p_id, n, cat, s, q, w)
                refresh()
                edit_win.destroy()
                messagebox.showinfo("Success", "Product updated successfully!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid Input: {e}")

        save_btn = tk.Button(form, text="Save Changes", command=save_edit)
        apply_button_style(save_btn, "secondary")
        save_btn.pack(pady=20)
        
        # BUG FIX: Enter key navigation for edit form
        name_ent.bind("<Return>", lambda e: sell_ent.focus_set())
        sell_ent.bind("<Return>", lambda e: qty_ent.focus_set())
        qty_ent.bind("<Return>", lambda e: weight_ent.focus_set() if cat_cb.get() in ["Feed", "Litter"] else save_edit())
        weight_ent.bind("<Return>", lambda e: save_edit())
        name_ent.focus_set()

    def delete_item():
        app._require_admin(delete_item_action)

    def edit_item():
        app._require_admin(edit_item_action)

    btn_bar = tk.Frame(win, bg=COLORS["background"])
    btn_bar.pack(pady=14)
    
    edit_btn = tk.Button(btn_bar, text="✏️ Edit Selected", command=edit_item)
    apply_button_style(edit_btn, "accent")
    edit_btn.pack(side="left", padx=10)

    del_btn = tk.Button(btn_bar, text="🗑  Delete Selected", command=delete_item)
    apply_button_style(del_btn, "danger")
    del_btn.pack(side="left", padx=10)


