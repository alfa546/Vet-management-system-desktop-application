# ═══════════════════════════════════════════════════════
#  Royal Pets Hospital — Professional Design System
# ═══════════════════════════════════════════════════════

COLORS = {
    "primary":    "#0B2447",   # Midnight Navy
    "secondary":  "#19A7CE",   # Cyan Blue
    "background": "#F0F3F8",   # Soft Ice
    "white":      "#FFFFFF",
    "text":       "#1E293B",   # Slate
    "accent":     "#E8A317",   # Rich Gold
    "danger":     "#DC2626",   # Vivid Red
    "card_bg":    "#FFFFFF",
    "border":     "#CBD5E1",   # Soft Slate Border
    "header_bg":  "#0B2447",   # Matches primary
    "success":    "#059669",   # Emerald
    "muted":      "#94A3B8",   # Gray Muted
    "entry_bg":   "#F8FAFC",   # Very light entry
    "hover":      "#146C94",   # Hover accent
}

FONTS = {
    "title":     ("Segoe UI", 30, "bold"),
    "header":    ("Segoe UI", 22, "bold"),
    "subheader": ("Segoe UI", 16, "bold"),
    "label":     ("Segoe UI", 11),
    "label_bold":("Segoe UI", 11, "bold"),
    "button":    ("Segoe UI", 11, "bold"),
    "small":     ("Segoe UI", 9),
    "icon":      ("Segoe UI Emoji", 36),
    "stat":      ("Segoe UI", 14, "bold"),
}


def apply_button_style(button, color_type="primary"):
    """Apply a premium flat button style."""
    bg = COLORS.get(color_type, COLORS["primary"])
    button.config(
        bg=bg,
        fg=COLORS["white"],
        font=FONTS["button"],
        relief="flat",
        padx=24,
        pady=10,
        cursor="hand2",
        activebackground=COLORS["hover"],
        activeforeground=COLORS["white"],
        borderwidth=0,
    )


def apply_label_style(label, is_header=False):
    if is_header:
        label.config(font=FONTS["header"], fg=COLORS["primary"], bg=COLORS["background"])
    else:
        label.config(font=FONTS["label"], fg=COLORS["text"], bg=COLORS["background"])


def style_treeview():
    """Return a ttk Style configured for premium tables."""
    import tkinter.ttk as ttk
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
        background=COLORS["white"],
        foreground=COLORS["text"],
        rowheight=30,
        fieldbackground=COLORS["white"],
        font=("Segoe UI", 10),
        borderwidth=0,
    )
    style.configure("Treeview.Heading",
        background=COLORS["primary"],
        foreground=COLORS["white"],
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    style.map("Treeview.Heading",
        background=[("active", COLORS["hover"])],
    )
    style.map("Treeview",
        background=[("selected", COLORS["secondary"])],
        foreground=[("selected", COLORS["white"])],
    )
    return style
