# Gestion Commerce Desktop POS v0.2

A modern, offline-first, multi-language Point-of-Sale (POS) system designed for Algerian stores.

## Key Features
- **Framework**: PyQt6 for a responsive and high-impact desktop experience.
- **Offline-First**: Uses SQLite3 for local-only, zero-configuration storage.
- **Multi-Language**: Full support for Arabic (RTL), French, and English with dynamic switching.
- **Multi-Tab Sales**: Handle multiple sales sessions simultaneously.
- **Inventory Management**: Track products, categories, and stock with optimistic locking.
- **Finance**: Secure cash register management (Open/Close/Withdrawals).
- **Parcel Tracking**: Specialized module for delivery-based sales and collection.
- **Security**: Role-based access (Admin/Cashier) with audit logging.

## Installation & Running

1. **Install Python 3.12+**
2. **Setup Dependencies**:
   ```bash
   pip install -r desktop/requirements.txt
   ```
3. **Initialize Database**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/desktop
   python3 desktop/src/init_db.py
   ```
4. **Run Application**:
   ```bash
   python3 desktop/src/main.py
   ```

## Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

---
*Created as part of the Step 10: Desktop POS Transformation.*
