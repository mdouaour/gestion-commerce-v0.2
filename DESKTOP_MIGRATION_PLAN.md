# Desktop Migration Plan: Offline POS System

This document outlines the strategy for transforming the existing web-based POS system (FastAPI/React) into a secure, offline-first desktop application for Algerian stores.

## 1. Architecture Overview
- **Framework**: PyQt6 (Python) for a robust and modern desktop experience.
- **Database**: SQLite3 for local, zero-configuration storage.
- **Business Logic**: Migrated from FastAPI services to pure Python modules.
- **State Management**: Reactive UI components using PyQt signals/slots.
- **Offline-First**: Local-only operations with a synchronization-ready schema.

## 2. Multi-Language Strategy (Arabic, French, English)
- **Resource Files**: Centralized JSON files in `src/resources/i18n/`.
  - `ar.json` (Arabic - RTL)
  - `fr.json` (French - LTR)
  - `en.json` (English - LTR)
- **Translation Manager**: A singleton `Translator` class to handle dynamic language switching.
- **Dynamic UI**: 
  - Signals to notify all windows of language changes.
  - Layout mirroring for RTL (Arabic support).
  - Locale-aware formatting for dates and currency (DZD).

## 3. Database & Models
- **Migration**: Convert SQLAlchemy models to standard SQLite-compatible schema.
- **Optimistic Locking**: Retain `version` column in `products` for multi-tab sales consistency.
- **New Tables**:
  - `audit_logs`: For tracking sensitive actions (deletions, price changes).
  - `sync_queue`: For potential future cloud synchronization.
  - `app_settings`: For storing language and theme preferences.

## 4. Key POS Features
- **Multi-Tab Sales**: Allow multiple active sales sessions in a single UI window.
- **Barcode Integration**:
  - Scanning: Direct input capture from hardware scanners.
  - Generation: `python-barcode` for printing labels.
- **Cash Management**: Strict opening/closing flows with audit trails.
- **Parcel Management**: Dedicated module for tracking deliveries and collections.

## 5. Security & Roles
- **Authentication**: Local hash-based password storage (Argon2 or bcrypt).
- **Authorization**: Hardcoded roles (`admin`, `cashier`) controlling UI visibility and action permissions.
- **Encrypted Storage**: Optional encryption for the SQLite database file using SQLCipher if required.

## 6. Implementation Phases

### Phase 1: Environment & Tooling
- Initialize PyQt6 project structure.
- Setup translation engine and basic resource files.
- Configure `pytest` for desktop-specific testing.

### Phase 2: Core Data Layer
- Implement SQLite models and migrations.
- Unit tests for data integrity and optimistic locking.

### Phase 3: Business Logic Migration
- Port services (`product_service`, `sale_service`, `finance_service`) to the desktop core.
- Ensure all logic is independent of any web framework.

### Phase 4: UI Development (Iterative)
1. **Login & Settings**: Basic auth and language selection.
2. **Sales Terminal**: Multi-tab interface, barcode support.
3. **Product & Inventory**: CRUD operations with search/filter.
4. **Admin Dashboard**: Analytics, cash reports, and audit logs.
5. **Parcel Management**: Tracking and validation UI.

### Phase 5: Testing & Validation
- Comprehensive test suite (Unit, Integration, E2E).
- Multi-language verification (all strings translated).
- Stress test multi-tab sales.

### Phase 6: Packaging & Deployment
- Use `PyInstaller` or `Nuitka` to create standalone executables for Windows/Linux.

## 7. Multi-Language Implementation Detail
Example `Translator` logic:
```python
class Translator:
    def __init__(self, lang="fr"):
        self.load_language(lang)
    
    def load_language(self, lang):
        with open(f"resources/i18n/{lang}.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
            
    def tr(self, key):
        # Nested key lookup: dashboard.title
        return self.get_nested(self.data, key)
```

---
**Status**: Awaiting confirmation to proceed to Phase 2.
