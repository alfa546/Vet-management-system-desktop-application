import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style
from datetime import datetime
import os

# ──────────────────────────────────────────────
#  SALES HISTORY
# ──────────────────────────────────────────────
def open_sales(app):
    win = app._new_window("Sales History", 920, 580)

    # ── Financial Stats Bar ──
    stats_bar = tk.Frame(win, bg=COLORS["card_bg"], pady=15, padx=20,
                         highlightthickness=1, highlightbackground=COLORS["border"])
    stats_bar.pack(fill="x", padx=20, pady=(14, 10))

    def _stat_item(parent, label, color):
        frame = tk.Frame(parent, bg=COLORS["card_bg"])
        frame.pack(side="left", expand=True)
        tk.Label(frame, text=label, font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack()
        var = tk.StringVar(value="Rs 0")
        tk.Label(frame, textvariable=var, font=FONTS["stat"], bg=COLORS["card_bg"], fg=color).pack()
        return var

    sales_var = _stat_item(stats_bar, "Total Sales (Gross)", COLORS["primary"])
    exp_var = _stat_item(stats_bar, "Total Expenses (Kharcha)", COLORS["danger"])
    net_var = _stat_item(stats_bar, "Net Earning (Profit)", COLORS["success"])

    def refresh_stats(start_date=None, end_date=None):
        s = start_date if start_date else "2000-01-01"
        e = end_date if end_date else "2099-12-31"
        data = app.db.get_financial_report(s, e)
        sales_var.set(f"Rs {data['products'] + data['treatments']:,.0f}")
        exp_var.set(f"Rs {data['expenses']:,.0f}")
        net_var.set(f"Rs {data['net']:,.0f}")

    # ── Filter Bar ──
    filter_bar = tk.Frame(win, bg=COLORS["background"], padx=20)
    filter_bar.pack(fill="x", pady=(0, 10))

    # Today / Week / Month
    btn_group = tk.Frame(filter_bar, bg=COLORS["background"])
    btn_group.pack(side="left", padx=(0, 10))

    tk.Button(btn_group, text="📅 Today", command=lambda: apply_filter("today"), 
              bg=COLORS["secondary"], fg=COLORS["white"], font=FONTS["small"], relief="flat", padx=10).pack(side="left", padx=2)
    
    tk.Button(btn_group, text="📅 This Week", command=lambda: apply_filter("week"), 
              bg="#6366f1", fg=COLORS["white"], font=FONTS["small"], relief="flat", padx=10).pack(side="left", padx=2)
    
    tk.Button(btn_group, text="📅 This Month", command=lambda: apply_filter("month"), 
              bg=COLORS["success"], fg=COLORS["white"], font=FONTS["small"], relief="flat", padx=10).pack(side="left", padx=2)

    # Date Range Inputs
    range_group = tk.Frame(filter_bar, bg=COLORS["background"])
    range_group.pack(side="left", padx=10)

    tk.Label(range_group, text="Range:", font=FONTS["small"], bg=COLORS["background"]).pack(side="left")
    from_ent = tk.Entry(range_group, font=FONTS["small"], width=10)
    from_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
    from_ent.pack(side="left", padx=2)
    tk.Label(range_group, text="-", bg=COLORS["background"]).pack(side="left")
    to_ent = tk.Entry(range_group, font=FONTS["small"], width=10)
    to_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
    to_ent.pack(side="left", padx=2)
    tk.Button(range_group, text="Go", command=lambda: apply_filter("range"),
              bg=COLORS["primary"], fg=COLORS["white"], font=FONTS["small"], relief="flat", padx=8).pack(side="left", padx=2)

    # Search Owner
    tk.Label(filter_bar, text="🔍 Owner Search:", font=FONTS["small"], bg=COLORS["background"]).pack(side="left", padx=(10, 2))
    owner_search_ent = tk.Entry(filter_bar, font=FONTS["small"], width=15)
    owner_search_ent.pack(side="left", padx=2, ipady=2)

    reset_btn = tk.Button(filter_bar, text="🔄 Reset All", command=lambda: refresh_table(reset=True),
                           bg=COLORS["muted"], fg=COLORS["white"], font=FONTS["small"], relief="flat", padx=10)
    reset_btn.pack(side="right", padx=10)

    # Enter key bindings
    from_ent.bind("<Return>", lambda e: apply_filter("range"))
    to_ent.bind("<Return>", lambda e: apply_filter("range"))

    # ── Table ──
    tree_frame = tk.Frame(win, bg=COLORS["background"])
    tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

    cols = ("ID", "Pet", "Owner", "Items", "Treatment", "Discount", "Total", "Date", "Day")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="extended")
    widths = {"ID": 40, "Pet": 80, "Owner": 100, "Items": 150,
              "Treatment": 80, "Discount": 80, "Total": 80, "Date": 130, "Day": 80}
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=widths[c], anchor="center")

    scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    def refresh_table(data=None, reset=False):
        if reset:
            owner_search_ent.delete(0, tk.END)
            from_ent.delete(0, tk.END)
            from_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
            to_ent.delete(0, tk.END)
            to_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
            # BUG FIX: After reset, fetch today's data explicitly
            data = app.db.get_all_sales()

        query = owner_search_ent.get().strip().lower()
        for item in tree.get_children():
            tree.delete(item)
        
        if data is not None:
            raw_data = data
        else:
            s = from_ent.get().strip()
            e = to_ent.get().strip()
            if s and e:
                raw_data = app.db.get_sales_by_date_range(s, e)
            else:
                raw_data = app.db.get_all_sales()
        
        # Highlight and move to top logic
        if query:
            matches = [s for s in raw_data if query in str(s[2]).lower()]
            others  = [s for s in raw_data if query not in str(s[2]).lower()]
            sales_data = matches + others
        else:
            sales_data = raw_data
        
        for s in sales_data:
            # BUG FIX: Parse date robustly - handle both HH:MM:SS and HH:MM formats
            try:
                raw_date = s[7] or ""
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        dt = datetime.strptime(raw_date, fmt)
                        day_name = dt.strftime("%A")
                        disp_date = raw_date
                        break
                    except ValueError:
                        continue
                else:
                    day_name = "N/A"
                    disp_date = raw_date
            except Exception:
                day_name = "N/A"
                disp_date = s[7] if len(s) > 7 else "N/A"
            
            # Check if this row is a search match
            is_match = query and query in str(s[2]).lower()
            tag = "search_match" if is_match else ""

            tree.insert("", "end", values=(
                s[0], s[1], s[2], s[3],
                f"Rs {float(s[4] or 0):.0f}", 
                f"Rs {float(s[5] or 0):.0f}", 
                f"Rs {float(s[6] or 0):.0f}", 
                disp_date, day_name),
                tags=(tag,))
        
        # Configure the red highlight tag
        tree.tag_configure("search_match", foreground=COLORS["danger"], font=FONTS["label_bold"])
        
        # Determine the date range to update financial stats
        # If we have filter entries, use them, otherwise default to all time
        s = from_ent.get().strip() or "2000-01-01"
        e = to_ent.get().strip() or "2099-12-31"
        refresh_stats(s, e)

    def apply_filter(mode):
        from datetime import timedelta
        import calendar
        
        if mode == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            from_ent.delete(0, tk.END); from_ent.insert(0, today)
            to_ent.delete(0, tk.END); to_ent.insert(0, today)
            data = app.db.get_sales_by_date(today)
        elif mode == "week":
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=6)
            s, e = start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")
            from_ent.delete(0, tk.END); from_ent.insert(0, s)
            to_ent.delete(0, tk.END); to_ent.insert(0, e)
            data = app.db.get_sales_by_date_range(s, e)
        elif mode == "month":
            today = datetime.now()
            s = today.strftime("%Y-%m-01")
            last_day = calendar.monthrange(today.year, today.month)[1]
            e = today.strftime(f"%Y-%m-{last_day:02d}")
            from_ent.delete(0, tk.END); from_ent.insert(0, s)
            to_ent.delete(0, tk.END); to_ent.insert(0, e)
            data = app.db.get_sales_by_date_range(s, e)
        elif mode == "range":
            s = from_ent.get().strip()
            e = to_ent.get().strip()
            if not s or not e:
                return messagebox.showwarning("Input Error", "Please enter both From and To dates.")
            data = app.db.get_sales_by_date_range(s, e)
        
        refresh_table(data)

    owner_search_ent.bind("<KeyRelease>", lambda e: refresh_table())
    refresh_table()

    # ── Delete Button ──
    def delete_sales_action():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Select",
                                          "Select one or more sales to delete.")
        if messagebox.askyesno("Confirm",
                f"Delete {len(sel)} record(s)?"):
            for item in sel:
                app.db.delete_sale(tree.item(item)['values'][0])
            refresh_table()
            messagebox.showinfo("Done",
                                f"{len(sel)} record(s) removed.")

    def delete_sales():
        app._require_admin(delete_sales_action)

    btn_bar = tk.Frame(win, bg=COLORS["background"])
    btn_bar.pack(pady=12)
    del_btn = tk.Button(btn_bar, text="🗑  Delete Selected", command=delete_sales)
    apply_button_style(del_btn, "danger")
    del_btn.pack()


