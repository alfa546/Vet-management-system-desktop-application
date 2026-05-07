import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style, style_treeview
from datetime import datetime
import os
import base64
import tempfile
try:
    import win32api
    import win32print
except ImportError:
    win32api = None
    win32print = None

# ──────────────────────────────────────────────
#  MULTI-ITEM BILLING (CART SYSTEM)
# ──────────────────────────────────────────────
def open_billing(app):
    win = app._new_window("Super Checkout (Multi-Item)", 1050, 700)
    
    # Apply Treeview Style
    style_treeview()

    main_frame = tk.Frame(win, bg=COLORS["background"])
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Split into Left (Form) and Right (Cart)
    left_pane = tk.Frame(main_frame, bg=COLORS["card_bg"], highlightthickness=1, highlightbackground=COLORS["border"], width=420)
    left_pane.pack(side="left", fill="y", padx=(0, 10))
    left_pane.pack_propagate(False)
    
    right_pane = tk.Frame(main_frame, bg=COLORS["card_bg"], highlightthickness=1, highlightbackground=COLORS["border"])
    right_pane.pack(side="right", fill="both", expand=True)

    # State variables
    cart_items = []  # To hold dicts: {'type', 'name', 'qty', 'price', 'total'}
    
    # ─── LEFT PANE: ADD ITEMS ───
    tk.Label(left_pane, text="1. Customer Info", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(15, 5))
    
    def _field(parent, label_text):
        f = tk.Frame(parent, bg=COLORS["card_bg"])
        f.pack(fill="x", padx=20, pady=5)
        tk.Label(f, text=label_text, font=FONTS["label_bold"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(anchor="w")
        e = tk.Entry(f, font=FONTS["label"], bg=COLORS["entry_bg"], relief="solid", borderwidth=1)
        e.pack(fill="x", ipady=4)
        return e

    pet_entry = _field(left_pane, "Pet Name")
    owner_entry = _field(left_pane, "Owner Name *")
    
    tk.Frame(left_pane, height=2, bg=COLORS["border"]).pack(fill="x", padx=20, pady=10)
    
    tk.Label(left_pane, text="2. Add Product", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(5, 5))
    
    p_frame = tk.Frame(left_pane, bg=COLORS["card_bg"])
    p_frame.pack(fill="x", padx=20)
    tk.Label(p_frame, text="Select Item:", font=FONTS["label_bold"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(anchor="w")
    
    item_search_var = tk.StringVar()
    item_cb = ttk.Combobox(p_frame, textvariable=item_search_var, font=FONTS["label"])
    all_p_data = app.db.get_all_in_stock_products()
    item_cb['values'] = [p[0] for p in all_p_data]
    item_cb.pack(fill="x", ipady=3)
    
    # Quantity for Product
    q_frame = tk.Frame(left_pane, bg=COLORS["card_bg"])
    q_frame.pack(fill="x", padx=20, pady=5)
    tk.Label(q_frame, text="Quantity:", font=FONTS["label_bold"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(side="left")
    qty_entry = tk.Entry(q_frame, font=FONTS["label"], bg=COLORS["entry_bg"], width=8, justify="center")
    qty_entry.insert(0, "1")
    qty_entry.pack(side="left", padx=10, ipady=3)
    
    def add_product_to_cart():
        name = item_cb.get().strip()
        if not name: return
        try:
            qty = int(qty_entry.get().strip() or 1)
        except ValueError:
            qty = 1
            
        p_data = next((p for p in all_p_data if p[0] == name), None)
        if not p_data:
            messagebox.showwarning("Error", "Item not found in stock!")
            return
            
        price = float(p_data[1])
        total = price * qty
        
        cart_items.append({'type': 'Product', 'name': name, 'qty': qty, 'price': price, 'total': total})
        item_cb.set('')
        qty_entry.delete(0, 'end')
        qty_entry.insert(0, "1")
        refresh_cart()

    btn_add_p = tk.Button(left_pane, text="➕ Add Product to Cart", command=add_product_to_cart, bg=COLORS["secondary"], fg=COLORS["white"], font=FONTS["button"], relief="flat", cursor="hand2")
    btn_add_p.pack(fill="x", padx=20, pady=10, ipady=5)

    tk.Frame(left_pane, height=2, bg=COLORS["border"]).pack(fill="x", padx=20, pady=10)
    
    tk.Label(left_pane, text="3. Add Treatment", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(5, 5))
    
    t_frame = tk.Frame(left_pane, bg=COLORS["card_bg"])
    t_frame.pack(fill="x", padx=20)
    tk.Label(t_frame, text="Select Treatment:", font=FONTS["label_bold"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(anchor="w")
    
    treat_search_var = tk.StringVar()
    treat_cb = ttk.Combobox(t_frame, textvariable=treat_search_var, font=FONTS["label"])
    all_t_data = app.db.get_all_treatments()
    treat_cb['values'] = [t[1] for t in all_t_data]
    treat_cb.pack(fill="x", ipady=3)
    
    def add_treat_to_cart():
        name = treat_cb.get().strip()
        if not name: return
        
        t_data = next((t for t in all_t_data if t[1] == name), None)
        if not t_data:
            messagebox.showwarning("Error", "Treatment not found!")
            return
            
        price = float(t_data[2])
        
        cart_items.append({'type': 'Treatment', 'name': name, 'qty': 1, 'price': price, 'total': price})
        treat_cb.set('')
        refresh_cart()

    btn_add_t = tk.Button(left_pane, text="➕ Add Treatment to Cart", command=add_treat_to_cart, bg=COLORS["success"], fg=COLORS["white"], font=FONTS["button"], relief="flat", cursor="hand2")
    btn_add_t.pack(fill="x", padx=20, pady=10, ipady=5)
    
    # Autocomplete bindings
    def filter_items(event):
        if event.keysym in ("Down", "Up", "Return", "Escape", "Tab"): return
        val = item_search_var.get().strip().lower()
        all_p = app.db.get_all_in_stock_products()
        if not val: item_cb['values'] = [p[0] for p in all_p]
        else:
            starts = [p[0] for p in all_p if p[0].lower().startswith(val)]
            contains = [p[0] for p in all_p if val in p[0].lower() and not p[0].lower().startswith(val)]
            item_cb['values'] = starts + contains
        item_cb.event_generate('<Down>')
    item_cb.bind("<KeyRelease>", filter_items)
    
    def filter_treats(event):
        if event.keysym in ("Down", "Up", "Return", "Escape", "Tab"): return
        val = treat_search_var.get().strip().lower()
        all_t = app.db.get_all_treatments()
        if not val: treat_cb['values'] = [t[1] for t in all_t]
        else:
            starts = [t[1] for t in all_t if t[1].lower().startswith(val)]
            contains = [t[1] for t in all_t if val in t[1].lower() and not t[1].lower().startswith(val)]
            treat_cb['values'] = starts + contains
        treat_cb.event_generate('<Down>')
    treat_cb.bind("<KeyRelease>", filter_treats)

    # ─── RIGHT PANE: CART & CHECKOUT ───
    tk.Label(right_pane, text="🛒 Shopping Cart", font=FONTS["subheader"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(15, 10))
    
    columns = ("Type", "Name", "Qty", "Price", "Total")
    cart_tree = ttk.Treeview(right_pane, columns=columns, show="headings", height=12)
    for col in columns:
        cart_tree.heading(col, text=col)
    cart_tree.column("Type", width=90, anchor="center")
    cart_tree.column("Name", width=220, anchor="w")
    cart_tree.column("Qty", width=50, anchor="center")
    cart_tree.column("Price", width=80, anchor="e")
    cart_tree.column("Total", width=80, anchor="e")
    cart_tree.pack(fill="both", expand=True, padx=20)
    
    def remove_selected():
        selected = cart_tree.selection()
        if not selected: return
        idx = cart_tree.index(selected[0])
        cart_items.pop(idx)
        refresh_cart()
        
    tk.Button(right_pane, text="🗑 Remove Selected", command=remove_selected, bg=COLORS["danger"], fg=COLORS["white"], font=FONTS["small"], relief="flat", cursor="hand2").pack(anchor="e", padx=20, pady=5)
    
    # Totals Area
    bottom_right = tk.Frame(right_pane, bg=COLORS["background"], padx=20, pady=10, highlightthickness=1, highlightbackground=COLORS["border"])
    bottom_right.pack(fill="x", side="bottom", padx=20, pady=20)
    
    calc_frame = tk.Frame(bottom_right, bg=COLORS["background"])
    calc_frame.pack(side="left", pady=10)
    
    tk.Label(calc_frame, text="Discount (Rs):", font=FONTS["label_bold"], bg=COLORS["background"], fg=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=5)
    disc_entry = tk.Entry(calc_frame, font=FONTS["label"], width=10, justify="right")
    disc_entry.insert(0, "0")
    disc_entry.grid(row=0, column=1, padx=10)
    
    tk.Label(calc_frame, text="Select Printer:", font=FONTS["label_bold"], bg=COLORS["background"], fg=COLORS["text"]).grid(row=1, column=0, sticky="w", pady=5)
    printer_var = tk.StringVar()
    printer_cb = ttk.Combobox(calc_frame, textvariable=printer_var, font=FONTS["label"], state="readonly", width=18)
    
    # Auto-select printer
    all_printers = [p[2] for p in win32print.EnumPrinters(2)] if win32print else ["Default"]
    printer_cb['values'] = all_printers
    keywords = ["thermal", "pos", "58mm", "80mm", "xprinter", "receipt", "generic"]
    default_printer = next((p for p in all_printers if any(kw in p.lower() for kw in keywords)), "")
    if default_printer: printer_cb.set(default_printer)
    elif all_printers: printer_cb.set(all_printers[0])
    printer_cb.grid(row=1, column=1, padx=10)
    
    total_lbl = tk.Label(bottom_right, text="Total: Rs 0", font=("Segoe UI", 26, "bold"), bg=COLORS["background"], fg=COLORS["accent"])
    total_lbl.pack(side="right", padx=20, pady=10)
    
    def refresh_cart(event=None):
        for item in cart_tree.get_children():
            cart_tree.delete(item)
            
        subtotal = 0
        for item in cart_items:
            cart_tree.insert("", "end", values=(item['type'], item['name'], item['qty'], item['price'], item['total']))
            subtotal += item['total']
            
        try: disc = float(disc_entry.get().strip() or 0)
        except ValueError: disc = 0
        
        final = max(0, subtotal - disc)
        total_lbl.config(text=f"Total: Rs {final:.0f}")

    disc_entry.bind("<KeyRelease>", refresh_cart)
    
    # ── CHECKOUT & PRINT ──
    def generate_bill():
        if not cart_items:
            return messagebox.showwarning("Cart Empty", "Please add at least one Item or Treatment.")
            
        owner = owner_entry.get().strip()
        if not owner:
            return messagebox.showwarning("Validation Error", "Please enter the Owner Name.")
            
        pet = pet_entry.get().strip() or "NA"
        selected_printer = printer_var.get()
        
        try: discount = float(disc_entry.get().strip() or 0)
        except ValueError: return messagebox.showwarning("Validation Error", "Invalid Discount.")
        
        # Aggregation
        product_names = []
        total_treat_cost = 0
        subtotal = 0
        
        for item in cart_items:
            subtotal += item['total']
            if item['type'] == 'Product':
                product_names.append(f"{item['name']} (x{item['qty']})")
                app.db.update_stock(item['name'], item['qty'])
            else:
                product_names.append(f"[Trt] {item['name']}")
                total_treat_cost += item['total']
                
        final_total = max(0, subtotal - discount)
        products_str = " + ".join(product_names)
        
        app.db.record_sale(pet, owner, products_str, total_treat_cost, final_total, discount)
        
        # ── RECEIPT GENERATION ──
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        def center(text, width=32): return text.center(width)[:width]
        def left_right(left, right, width=32):
            spaces = width - len(left) - len(right)
            return (left + " " * max(1, spaces) + right)[:width]

        Initialize = b'\x1b\x40'
        FontA = b'\x1b\x4d\x00'
        DoubleSize = b'\x1d\x21\x11'
        NormalSize = b'\x1d\x21\x00'
        BoldOn = b'\x1b\x45\x01'
        BoldOff = b'\x1b\x45\x00'
        Cut = b'\x1d\x56\x00'

        payload = bytearray()
        payload += Initialize + FontA
        payload += DoubleSize + BoldOn + "ROYAL PETS".center(16).encode('ascii') + b'\n' + NormalSize + BoldOff
        
        lines = []
        lines.append(center("Engine Street, Jinnah Rd, Okara"))
        lines.append(center("Contact: 0322-9544687"))
        lines.append("-" * 32)
        lines.append(f"Date:  {now}")
        lines.append(f"Owner: {owner}")
        lines.append(f"Pet:   {pet}")
        lines.append("-" * 32)
        
        for item in cart_items:
            if item['type'] == 'Product':
                lines.append(f"{item['name'][:26]}")
                lines.append(left_right(f"  Rs {item['price']:.0f} x {item['qty']}", f"Rs {item['total']:.0f}"))
            else:
                lines.append(f"Trt: {item['name'][:26]}")
                lines.append(left_right(f"  Cost:", f"Rs {item['total']:.0f}"))
        
        lines.append("-" * 32)
        lines.append(left_right("SUBTOTAL:", f"Rs {subtotal:.0f}"))
        lines.append(left_right("DISCOUNT:", f"Rs {discount:.0f}"))
        lines.append(left_right("TOTAL BILL:", f"Rs {final_total:.0f}"))
        lines.append("-" * 32)
        lines.append(center("Doctors: Aamir, Haseeb, Absar"))
        lines.append(center("Stay Happy, Stay Healthy!"))
        lines.append("*" * 32)
        lines.append("\n\n")

        payload += "\n".join(lines).encode('ascii', errors='replace') + Cut

        # Print
        if selected_printer and selected_printer != "Default" and win32print:
            try:
                hPrinter = win32print.OpenPrinter(selected_printer)
                try:
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, bytes(payload))
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                    messagebox.showinfo("Success", "Bill Recorded & Printed successfully!")
                finally:
                    win32print.ClosePrinter(hPrinter)
            except Exception as e:
                messagebox.showerror("Print Error", f"Error: {e}")
        else:
            try:
                temp_path = os.path.join(tempfile.gettempdir(), "receipt.txt")
                with open(temp_path, "w") as f: f.write("\n".join(lines))
                if os.name == 'nt':
                    os.startfile(temp_path, "print")
                messagebox.showinfo("Success", "Bill Recorded & Sent to Printer!")
            except Exception as e:
                messagebox.showinfo("Success", f"Bill Recorded Successfully! (Print skipped: {e})")
            
        win.destroy()

    btn_checkout = tk.Button(right_pane, text="💳 CHECKOUT & PRINT BILL", command=generate_bill, bg=COLORS["accent"], fg=COLORS["white"], font=("Segoe UI", 16, "bold"), relief="flat", cursor="hand2")
    btn_checkout.pack(fill="x", padx=20, pady=20, ipady=12)
