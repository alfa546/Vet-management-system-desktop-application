import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style

def open_treatment_manager(app):
    win = app._new_window("Manage Treatments", 800, 500)
    
    # Left Side: Form to add treatment
    form_frame = tk.Frame(win, bg=COLORS["card_bg"], padx=20, pady=20,
                          highlightthickness=1, highlightbackground=COLORS["border"])
    form_frame.pack(side="left", fill="y", padx=20, pady=20)
    
    tk.Label(form_frame, text="Add New Treatment", font=FONTS["subheader"],
             bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(0, 20))
    
    tk.Label(form_frame, text="Treatment Name:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w")
    name_ent = tk.Entry(form_frame, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
    name_ent.pack(pady=5, ipady=4)
    
    tk.Label(form_frame, text="Price (Rs):", font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(10, 0))
    price_ent = tk.Entry(form_frame, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
    price_ent.pack(pady=5, ipady=4)
    
    def save_treatment(event=None):
        name = name_ent.get().strip()
        price = price_ent.get().strip()
        
        if not name or not price:
            return messagebox.showwarning("Error", "Please fill all fields.")
        
        try:
            price = float(price)
            app.db.add_treatment(name, price)
            messagebox.showinfo("Success", "Treatment added successfully!")
            name_ent.delete(0, tk.END)
            price_ent.delete(0, tk.END)
            refresh_table()
            name_ent.focus_set()
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")

    save_btn = tk.Button(form_frame, text="💾 Save Treatment", command=save_treatment)
    apply_button_style(save_btn, "success")
    save_btn.pack(pady=20)
    
    name_ent.bind("<Return>", lambda e: price_ent.focus_set())
    price_ent.bind("<Return>", save_treatment)
    name_ent.focus_set()
    
    # Right Side: Table to view/delete treatments
    table_frame = tk.Frame(win, bg=COLORS["background"])
    table_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)
    
    cols = ("id", "name", "price")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Treatment Name")
    tree.heading("price", text="Price (Rs)")
    
    tree.column("id", width=50, anchor="center")
    tree.column("name", width=250, anchor="center")
    tree.column("price", width=100, anchor="center")
    
    tree.pack(fill="both", expand=True)
    
    def refresh_table():
        for item in tree.get_children():
            tree.delete(item)
        for t in app.db.get_all_treatments():
            tree.insert("", "end", values=t)
            
    def delete_treatment_action():
        sel = tree.selection()
        if not sel:
            return messagebox.showwarning("Select", "Select a treatment to delete.")
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this treatment?"):
            for item in sel:
                t_id = tree.item(item)['values'][0]
                app.db.delete_treatment(t_id)
            refresh_table()
            messagebox.showinfo("Done", "Treatment deleted.")

    def delete_treatment():
        app._require_admin(delete_treatment_action)

    del_btn = tk.Button(table_frame, text="🗑 Delete Selected", command=delete_treatment)
    apply_button_style(del_btn, "danger")
    del_btn.pack(pady=10)
    
    refresh_table()
