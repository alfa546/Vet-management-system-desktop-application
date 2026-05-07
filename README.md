# Royal Pets Hospital — Desktop Management System

A Tkinter-based desktop application for managing a veterinary clinic: inventory, billing, sales, treatments, expenses and credit (udhaar) tracking.

**Key Features**
- Inventory management (add items, low-stock alerts)
- Billing & sales receipts
- Treatments record
- Expense tracking
- Credit / Udhaar book
- Simple admin authorization for sensitive actions

**Requirements**
- Python 3.8+
- See `requirements.txt` for packaging tools (pyinstaller)

**Quick start (development)**
1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if any additional are needed):

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python "royal_clinic_main.py"
```

**Packaging**
A PyInstaller spec file (`royal_clinic_main.spec`) is included. Build an executable with:

```powershell
pip install pyinstaller
pyinstaller --onefile "royal_clinic_main.spec"
```

**Project layout**
- `royal_clinic_main.py` — application entry and UI layout
- `database_manager.py` — SQLite wrapper and DB logic
- `features_*.py` — modular feature implementations (billing, inventory, sales, etc.)
- `styles.py` — color palette and UI helper styles
- `requirements.txt` — packaging/dependency notes
- `screenshots/` — placeholder screenshots added by Copilot
- `Receipts/` — saved receipt files (if any)

**Notes & Next steps**
- Replace the placeholder SVGs in `screenshots/` with real screenshots captured on your machine for authentic visuals.
- Add any missing Python packages to `requirements.txt` if running into ImportError (e.g., `Pillow`).

---
Generated on May 8, 2026 — prepared for inclusion in the repository.
