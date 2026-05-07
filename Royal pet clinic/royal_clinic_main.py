import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
from styles import COLORS, FONTS, apply_button_style, apply_label_style, style_treeview
import os
import sys
from datetime import datetime
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))


class RoyalPetsHospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROYAL PETS HOSPITAL OKARA — Management System")
        self.root.geometry("960x680")
        self.root.configure(bg=COLORS["background"])
        self.root.minsize(900, 650)
        self.root.state('zoomed') # Open main window in full screen

        # Apply premium Treeview styling globally
        style_treeview()

        # Initialize Database
        self.db = DatabaseManager()

        self.create_splash_screen()

    # ──────────────────────────────────────────────
    #  SPLASH / STARTER PAGE
    # ──────────────────────────────────────────────
    def create_splash_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        splash_frame = tk.Frame(self.root, bg=COLORS["background"])
        splash_frame.pack(fill="both", expand=True)
        
        # Center Content
        center_box = tk.Frame(splash_frame, bg=COLORS["background"])
        center_box.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icon
        logo_path = os.path.join(get_base_path(), "logo.jpg")
        if Image and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((180, 180), Image.Resampling.LANCZOS)
                self.splash_logo = ImageTk.PhotoImage(img)
                tk.Label(center_box, image=self.splash_logo, bg=COLORS["background"]).pack(pady=(0, 20))
            except Exception as e:
                print(f"Error loading logo: {e}")
                tk.Label(center_box, text="🐾", font=("Segoe UI Emoji", 70),
                         bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 20))
        else:
            tk.Label(center_box, text="🐾", font=("Segoe UI Emoji", 70),
                     bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 20))
                 
        # Title
        tk.Label(center_box, text="ROYAL PETS HOSPITAL",
                 font=("Segoe UI", 56, "bold"), fg=COLORS["primary"],
                 bg=COLORS["background"]).pack()
                 
        # Address
        tk.Label(center_box, text="📍 Engine Street, M.A. Jinnah Road, Okara",
                 font=("Segoe UI", 18), fg=COLORS["text"],
                 bg=COLORS["background"]).pack(pady=(5, 40))
                 
        # Start Button
        start_btn = tk.Button(center_box, text="START SYSTEM", font=("Segoe UI", 16, "bold"),
                              bg=COLORS["accent"], fg=COLORS["primary"],
                              activebackground="#FDE047", activeforeground=COLORS["primary"],
                              relief="flat", cursor="hand2", padx=40, pady=12,
                              command=self.create_dashboard)
        start_btn.pack()
        
        # Button Hover Effect
        start_btn.bind("<Enter>", lambda e: e.widget.config(bg="#FDE047"))
        start_btn.bind("<Leave>", lambda e: e.widget.config(bg=COLORS["accent"]))

    # ──────────────────────────────────────────────
    #  DASHBOARD
    # ──────────────────────────────────────────────
    def create_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # ── Header Bar ──
        header = tk.Frame(self.root, bg=COLORS["primary"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = tk.Frame(header, bg=COLORS["primary"])
        header_inner.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = os.path.join(get_base_path(), "logo.jpg")
        if Image and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.header_logo = ImageTk.PhotoImage(img)
                tk.Label(header_inner, image=self.header_logo, bg=COLORS["primary"]).pack(side="left", padx=(0, 12))
            except Exception as e:
                print(f"Error loading logo: {e}")
                tk.Label(header_inner, text="🐾", font=("Segoe UI Emoji", 26),
                         bg=COLORS["primary"], fg=COLORS["white"]).pack(side="left", padx=(0, 12))
        else:
            tk.Label(header_inner, text="🐾", font=("Segoe UI Emoji", 26),
                     bg=COLORS["primary"], fg=COLORS["white"]).pack(side="left", padx=(0, 12))

        title_block = tk.Frame(header_inner, bg=COLORS["primary"])
        title_block.pack(side="left")
        tk.Label(title_block, text="ROYAL PETS HOSPITAL",
                 font=("Segoe UI", 28, "bold"), fg=COLORS["white"],
                 bg=COLORS["primary"]).pack(anchor="w")

        # ── Center Content ──
        center = tk.Frame(self.root, bg=COLORS["background"])
        center.pack(expand=True)

        # Card data: (title, icon, callback, color_key)
        cards = [
            ("Add Items",        "📦", self.open_add_item,          "secondary"),
            ("Treatments",       "💉", self.open_treatment_manager, "success"),
            ("Inventory",        "📋", self.open_inventory_manager, "primary"),
            ("Billing",          "💰", self.open_billing,           "accent"),
            ("Sales History",    "📊", self.open_sales,             "primary"),
            ("Kharcha (Expense)","💸", self.open_expense_manager,   "accent"),
            ("Udhaar Book",      "📒", self.open_credit_manager,    "danger"),
        ]

        # Row 1: 4 cards — Row 2: 4 cards (centered)
        row1 = tk.Frame(center, bg=COLORS["background"])
        row1.pack(pady=(20, 10))
        row2 = tk.Frame(center, bg=COLORS["background"])
        row2.pack(pady=(0, 10))

        for idx, (title, icon, cmd, ckey) in enumerate(cards):
            parent = row1 if idx < 4 else row2
            self._make_card(parent, title, icon, cmd, COLORS[ckey])

        # ── Low Stock Alerts ──
        self.check_low_stock(center)

        # ── Footer ──
        tk.Label(self.root,
                 text="© 2026 Royal Pets Hospital  •  Elite Edition",
                 font=FONTS["small"], fg=COLORS["muted"],
                 bg=COLORS["background"]).pack(side="bottom", pady=14)

    def _make_card(self, parent, title, icon, command, color):
        """Create a single dashboard card with hover animation."""
        card = tk.Frame(parent, bg=COLORS["card_bg"], padx=18, pady=14,
                        highlightthickness=1, highlightbackground=COLORS["border"],
                        cursor="hand2")
        card.pack(side="left", padx=14, pady=6)

        tk.Label(card, text=icon, font=FONTS["icon"],
                 bg=COLORS["card_bg"]).pack(pady=(4, 2))
        tk.Label(card, text=title, font=FONTS["label_bold"],
                 bg=COLORS["card_bg"], fg=COLORS["text"]).pack()

        btn = tk.Button(card, text="Open", command=command, borderwidth=0,
                        relief="flat", bg=color, fg=COLORS["white"],
                        font=FONTS["button"], padx=28, pady=6, cursor="hand2",
                        activebackground=self._darken(color),
                        activeforeground=COLORS["white"])
        btn.pack(pady=(10, 4))

        # Hover: lighten card border
        def _enter(e):
            card.config(highlightbackground=color, highlightthickness=2)
            btn.config(bg=self._darken(color))
        def _leave(e):
            card.config(highlightbackground=COLORS["border"], highlightthickness=1)
            btn.config(bg=color)

        for w in [card, btn] + list(card.winfo_children()):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

    @staticmethod
    def _darken(hex_color, amount=25):
        h = hex_color.lstrip('#')
        rgb = tuple(max(0, int(h[i:i+2], 16) - amount) for i in (0, 2, 4))
        return '#%02x%02x%02x' % rgb

    def check_low_stock(self, parent_frame):
        inventory = self.db.get_all_inventory() # id, name, category, price, weight, quantity
        # Filter items with quantity <= 5
        low_stock_items = [item for item in inventory if item[5] <= 5]
        
        if low_stock_items:
            alert_frame = tk.Frame(parent_frame, bg="#FEF2F2", highlightthickness=1, highlightbackground=COLORS["danger"])
            alert_frame.pack(fill="x", padx=40, pady=(20, 0))
            
            icon_lbl = tk.Label(alert_frame, text="⚠️", font=("Segoe UI Emoji", 20), bg="#FEF2F2", fg=COLORS["danger"])
            icon_lbl.pack(side="left", padx=(15, 5), pady=10)
            
            names = ", ".join([f"{i[1]} ({i[5]} left)" for i in low_stock_items[:3]])
            if len(low_stock_items) > 3:
                names += f" and {len(low_stock_items)-3} more..."
                
            text_lbl = tk.Label(alert_frame, text=f"SMART ALERT: Low Stock Detected - {names}. Please reorder!", font=FONTS["label_bold"], fg=COLORS["danger"], bg="#FEF2F2")
            text_lbl.pack(side="left", pady=10)
            
            # Simple blink animation
            def blink():
                current_color = text_lbl.cget("fg")
                next_color = "#991B1B" if current_color == COLORS["danger"] else COLORS["danger"]
                text_lbl.config(fg=next_color)
                self.root.after(800, blink)
                
            blink()

    # ──────────────────────────────────────────────
    #  HELPER — styled top-level window
    # ──────────────────────────────────────────────
    def _new_window(self, title, width=700, height=560):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{width}x{height}")
        win.configure(bg=COLORS["background"])
        win.state('zoomed') # Open child window in full screen
        win.grab_set()

        # Mini header inside child windows
        hdr = tk.Frame(win, bg=COLORS["primary"], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        
        # Back button now just closes the window
        back_btn = tk.Button(hdr, text="← Back to Dashboard", command=win.destroy,
                             bg=COLORS["primary"], fg=COLORS["white"], font=FONTS["label_bold"],
                             relief="flat", cursor="hand2", activebackground=COLORS["secondary"],
                             activeforeground=COLORS["white"])
        back_btn.pack(side="left", padx=20)

        tk.Label(hdr, text=title, font=FONTS["subheader"],
                 fg=COLORS["white"], bg=COLORS["primary"]).pack(expand=True)
        return win

    def _require_admin(self, callback):
        """Prompt for admin credentials before executing callback."""
        auth_win = tk.Toplevel(self.root)
        auth_win.title("Admin Login Required")
        auth_win.geometry("900x600")
        auth_win.configure(bg=COLORS["background"])
        auth_win.state('zoomed')
        auth_win.grab_set()

        center_frame = tk.Frame(auth_win, bg=COLORS["card_bg"], padx=40, pady=40,
                                highlightthickness=1, highlightbackground=COLORS["border"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center_frame, text="🔒 Admin Authorization", font=FONTS["subheader"],
                 bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(0, 20))

        tk.Label(center_frame, text="Username:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w")
        user_ent = tk.Entry(center_frame, font=FONTS["label"], bg=COLORS["entry_bg"], width=25)
        user_ent.pack(pady=5, ipady=4)

        tk.Label(center_frame, text="Password:", font=FONTS["label"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(10, 0))
        pass_ent = tk.Entry(center_frame, font=FONTS["label"], show="*", bg=COLORS["entry_bg"], width=25)
        pass_ent.pack(pady=5, ipady=4)

        def verify(event=None):
            if user_ent.get() == "admin123" and pass_ent.get() == "royal":
                auth_win.destroy()
                callback()
            else:
                messagebox.showerror("Access Denied", "Incorrect Admin Username or Password!")

        btn = tk.Button(center_frame, text="Login", command=verify)
        apply_button_style(btn, "accent")
        btn.pack(pady=(20, 0))
        
        user_ent.bind("<Return>", verify)
        pass_ent.bind("<Return>", verify)
        user_ent.focus_set()

    # ──────────────────────────────────────────────
    #  FEATURE PROXIES (Modular System)
    # ──────────────────────────────────────────────
    def open_add_item(self):
        from features_inventory import open_add_item
        open_add_item(self)

    def open_inventory_manager(self):
        from features_inventory import open_inventory_manager
        open_inventory_manager(self)

    def open_billing(self):
        from features_billing import open_billing
        open_billing(self)

    def open_sales(self):
        from features_sales import open_sales
        open_sales(self)

    def open_credit_manager(self):
        from features_credit import open_credit_manager
        open_credit_manager(self)

    def open_expense_manager(self):
        from features_expense import open_expense_manager
        open_expense_manager(self)

    def open_treatment_manager(self):
        from features_treatment import open_treatment_manager
        open_treatment_manager(self)



# ══════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    if os.name == 'nt':
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    try:
        root = tk.Tk()
        app = RoyalPetsHospitalApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nSystem closed by user.")
        sys.exit(0)
