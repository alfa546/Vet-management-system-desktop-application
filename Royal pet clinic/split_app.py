import os

with open('royal_clinic_main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_block(start_marker, end_marker=None):
    start_idx = -1
    end_idx = len(lines)
    for i, line in enumerate(lines):
        if start_marker in line:
            start_idx = i - 1  # include the separator line above
            break
    if start_idx == -1: return []
    
    if end_marker:
        for i in range(start_idx + 2, len(lines)):
            if end_marker in lines[i]:
                end_idx = i - 1
                break
    return lines[start_idx:end_idx]

imports = """import tkinter as tk
from tkinter import ttk, messagebox
from styles import COLORS, FONTS, apply_button_style
from datetime import datetime
import os
"""

# Extract blocks
add_items_code = get_block("ADD FEED / VACCINE", "INVENTORY MANAGER")
inventory_code = get_block("INVENTORY MANAGER", "BILLING")
billing_code = get_block("BILLING", "SALES HISTORY")
sales_code = get_block("SALES HISTORY", "UDHAAR / CREDIT")
credit_code = get_block("UDHAAR / CREDIT", "KHARCHA / EXPENSE")
expense_code = get_block("KHARCHA / EXPENSE", "ENTRY POINT")

def write_module(filename, code_lines):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(imports + "\n")
        # Remove the leading 4 spaces for the class methods so they become standalone functions
        for line in code_lines:
            if line.startswith("    "):
                # Replace 'self.' with 'app.' and 'self' with 'app'
                modified_line = line[4:].replace('self._require_admin', 'app._require_admin')
                modified_line = modified_line.replace('self._new_window', 'app._new_window')
                modified_line = modified_line.replace('self.db', 'app.db')
                # Wait, what about 'def open_... (self)'?
                if modified_line.startswith("def open_") or modified_line.startswith("def _show_"):
                    modified_line = modified_line.replace("(self", "(app").replace("(self,", "(app,")
                f.write(modified_line)
            else:
                f.write(line)

write_module("features_inventory.py", add_items_code + inventory_code)
write_module("features_billing.py", billing_code)
write_module("features_sales.py", sales_code)
write_module("features_credit.py", credit_code)
write_module("features_expense.py", expense_code)

print("Split completed.")
