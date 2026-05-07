import sqlite3
import os
import sys
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="royal_hospital.db"):
        import shutil
        
        # Professional Approach: Store database in AppData
        app_data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'RoyalPetsClinic')
        
        # Create directory if it doesn't exist
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
            
        db_path = os.path.join(app_data_dir, db_name)
        
        # Migration: If DB exists in old location but not in AppData, move it
        if hasattr(sys, '_MEIPASS'):
            old_base_dir = os.path.dirname(sys.executable)
        else:
            old_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        old_db_path = os.path.join(old_base_dir, db_name)
        if os.path.exists(old_db_path) and not os.path.exists(db_path):
            try:
                shutil.copy2(old_db_path, db_path)
            except Exception:
                pass
                
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Enable WAL mode for better concurrency and scaling
        self.cursor.execute('PRAGMA journal_mode=WAL')
        
        self.create_tables()

    def create_tables(self):
        # Table for inventory (Feeds and Vaccines)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                weight TEXT,
                quantity INTEGER NOT NULL
            )
        ''')

        # Table for sales transactions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_name TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                product_name TEXT,
                treatment_cost REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                total_bill REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Index for faster date queries
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)')

        # Migration for discount in sales
        self.cursor.execute("PRAGMA table_info(sales)")
        cols_sales = [c[1] for c in self.cursor.fetchall()]
        if 'discount' not in cols_sales:
            self.cursor.execute("ALTER TABLE sales ADD COLUMN discount REAL DEFAULT 0")

        # Table for Credit (Udhaar)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Unpaid'
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_credit_date ON credit(date)')
        
        # Check if status column exists in credit table (Migration)
        self.cursor.execute("PRAGMA table_info(credit)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'status' not in columns:
            self.cursor.execute("ALTER TABLE credit ADD COLUMN status TEXT DEFAULT 'Unpaid'")

        # Table for Expenses (Kharcha)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')

        # Table for Treatments
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
            
        self.conn.commit()

    # Inventory Methods
    def add_product(self, name, category, price, quantity, weight=None):
        self.cursor.execute('''
            INSERT INTO inventory (name, category, price, quantity, weight)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, price, quantity, weight))
        self.conn.commit()

    def get_products_by_category(self, category):
        self.cursor.execute('SELECT name, price, quantity FROM inventory WHERE category = ? AND quantity > 0', (category,))
        return self.cursor.fetchall()

    def get_all_in_stock_products(self):
        self.cursor.execute('SELECT name, price, category FROM inventory WHERE quantity > 0')
        return self.cursor.fetchall()

    def get_all_inventory(self):
        self.cursor.execute('SELECT id, name, category, price, weight, quantity FROM inventory')
        return self.cursor.fetchall()

    def delete_product(self, product_id):
        self.cursor.execute('DELETE FROM inventory WHERE id = ?', (product_id,))
        self.conn.commit()

    def update_product(self, product_id, name, category, price, quantity, weight):
        self.cursor.execute('''
            UPDATE inventory 
            SET name = ?, category = ?, price = ?, quantity = ?, weight = ?
            WHERE id = ?
        ''', (name, category, price, quantity, weight, product_id))
        self.conn.commit()

    def update_stock(self, product_name, quantity_sold):
        self.cursor.execute('''
            UPDATE inventory SET quantity = quantity - ? WHERE name = ?
        ''', (quantity_sold, product_name))
        self.conn.commit()

    # Sales Methods
    def record_sale(self, pet_name, owner_name, product_name, treatment_cost, total_bill, discount=0):
        self.cursor.execute('''
            INSERT INTO sales (pet_name, owner_name, product_name, treatment_cost, discount, total_bill)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pet_name, owner_name, product_name, treatment_cost, discount, total_bill))
        self.conn.commit()

    def delete_sale(self, sale_id):
        self.cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
        self.conn.commit()

    def get_all_sales(self, limit=1000):
        self.cursor.execute('SELECT id, pet_name, owner_name, product_name, treatment_cost, discount, total_bill, datetime(sale_date, "localtime") FROM sales ORDER BY sale_date DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def get_sales_by_date(self, target_date):
        """target_date format: YYYY-MM-DD"""
        self.cursor.execute('SELECT id, pet_name, owner_name, product_name, treatment_cost, discount, total_bill, datetime(sale_date, "localtime") FROM sales WHERE date(sale_date, "localtime") = ? ORDER BY sale_date DESC', (target_date,))
        return self.cursor.fetchall()

    def get_sales_by_date_range(self, start_date, end_date):
        """dates format: YYYY-MM-DD"""
        self.cursor.execute('SELECT id, pet_name, owner_name, product_name, treatment_cost, discount, total_bill, datetime(sale_date, "localtime") FROM sales WHERE date(sale_date, "localtime") BETWEEN ? AND ? ORDER BY sale_date DESC', (start_date, end_date))
        return self.cursor.fetchall()

    def get_daily_sales_total(self):
        self.cursor.execute('''
            SELECT SUM(total_bill) FROM sales 
            WHERE date(sale_date, 'localtime') = date('now', 'localtime')
        ''')
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def get_total_sales(self):
        self.cursor.execute('SELECT SUM(total_bill) FROM sales')
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    # Credit (Udhaar) Methods
    def add_credit(self, name, phone, amount):
        self.cursor.execute('''
            INSERT INTO credit (name, phone, amount)
            VALUES (?, ?, ?)
        ''', (name, phone, amount))
        self.conn.commit()

    def get_all_credit(self, limit=1000):
        self.cursor.execute('SELECT id, name, phone, amount, datetime(date, "localtime"), status FROM credit ORDER BY date DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def delete_credit(self, credit_id):
        self.cursor.execute('DELETE FROM credit WHERE id = ?', (credit_id,))
        self.conn.commit()

    def mark_credit_paid(self, credit_id):
        self.cursor.execute("UPDATE credit SET status = 'Paid' WHERE id = ?", (credit_id,))
        self.conn.commit()

    # Expenses (Kharcha) Methods
    def add_expense(self, description, amount):
        self.cursor.execute('''
            INSERT INTO expenses (description, amount)
            VALUES (?, ?)
        ''', (description, amount))
        self.conn.commit()

    def get_all_expenses(self, limit=1000):
        self.cursor.execute('SELECT id, description, amount, datetime(date, "localtime") FROM expenses ORDER BY date DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def get_daily_expenses_total(self):
        self.cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE date(date, 'localtime') = date('now', 'localtime')
        ''')
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def get_total_expenses(self):
        self.cursor.execute('SELECT SUM(amount) FROM expenses')
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def delete_expense(self, expense_id):
        self.cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        self.conn.commit()

    def get_financial_report(self, start_date, end_date):
        """Calculates earnings breakdown for a specific date range (YYYY-MM-DD)."""
        # Get Sales Breakdown
        self.cursor.execute('''
            SELECT 
                SUM(treatment_cost) as total_treatments,
                SUM(total_bill + discount - treatment_cost) as total_products
            FROM sales 
            WHERE date(sale_date, 'localtime') BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        row = self.cursor.fetchone()
        treat_total = row[0] if row and row[0] else 0.0
        prod_total = row[1] if row and row[1] else 0.0
        
        # Get Expenses
        self.cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE date(date, 'localtime') BETWEEN ? AND ?
        ''', (start_date, end_date))
        exp_total = self.cursor.fetchone()[0] or 0.0
        
        return {
            "products": prod_total,
            "treatments": treat_total,
            "expenses": exp_total,
            "net": (prod_total + treat_total) - exp_total
        }

    # Treatment Methods
    def add_treatment(self, name, price):
        self.cursor.execute('INSERT INTO treatments (name, price) VALUES (?, ?)', (name, price))
        self.conn.commit()

    def get_all_treatments(self):
        self.cursor.execute('SELECT * FROM treatments')
        return self.cursor.fetchall()

    def delete_treatment(self, t_id):
        self.cursor.execute('DELETE FROM treatments WHERE id = ?', (t_id,))
        self.conn.commit()

    def search_treatments(self, query):
        self.cursor.execute('SELECT * FROM treatments WHERE name LIKE ?', (f'%{query}%',))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
