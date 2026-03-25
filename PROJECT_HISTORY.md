
---
### UI/UX Improvements Phase

**Date:** 2026-03-25

- **🇬🇧 English:** Transformed the application into a professional, keyboard-first POS system. 
    - **Login:** Replaced manual username typing with a selection dropdown. Added **Enter** key support and auto-focus on the password field for a frictionless start.
    - **Data Integrity:** Converted all "Sold Items" and Cart tables to **Read-Only** to prevent accidental or malicious data modification.
    - **Sales Flow:** Implemented **Real-Time Search** in the sales terminal. Cashiers can now type and see results instantly, navigating with arrow keys and selecting with Enter.
    - **UX:** Increased button and input sizes for high-traffic usage. 
- **🇫🇷 French:** Transformation de l'application en un système POS professionnel axé sur le clavier.
    - **Connexion:** Remplacement de la saisie manuelle du nom d'utilisateur par une liste déroulante. Ajout du support de la touche **Entrée** et de l'auto-focus sur le champ mot de passe.
    - **Intégrité des données:** Passage de tous les tableaux de vente et du panier en mode **Lecture seule** pour éviter les modifications accidentelles.
    - **Flux de vente:** Implémentation de la **Recherche en temps réel**. Les caissiers peuvent désormais voir les résultats instantanément, naviguer avec les flèches et sélectionner avec Entrée.
- **🇩🇿 Arabic:** تحويل التطبيق إلى نظام نقطة بيع (POS) احترافي يعتمد على لوحة المفاتيح.
    - **تسجيل الدخول:** استبدال الكتابة اليدوية لاسم المستخدم بقائمة اختيار. إضافة دعم مفتاح **Enter** والتركيز التلقائي على حقل كلمة المرور.
    - **سلامة البيانات:** تحويل جميع جداول المبيعات وسلة التسوق إلى وضع **القراءة فقط** لمنع التعديل غير المصرح به.
    - **تدفق المبيعات:** تنفيذ **البحث في الوقت الفعلي**. يمكن للصرافين الآن رؤية النتائج فوراً، والتنقل باستخدام الأسهم والاختيار بمفتاح Enter.

---
### Day Resume Audit

**Date:** 2026-03-25

- **🇬🇧 English:** Performed a full project audit. Verified the core structure (models, services, UI). Identified and fixed a path resolution issue in `init_db.py` to allow standalone execution. Noted missing `argon2-cffi` dependency in the environment. Verified RBAC logic in the Dashboard.
- **🇫🇷 French:** Audit complet du projet effectué. Vérification de la structure de base (modèles, services, UI). Identification et correction d'un problème de résolution de chemin dans `init_db.py` pour permettre l'exécution autonome. Note de la dépendance `argon2-cffi` manquante dans l'environnement. Vérification de la logique RBAC dans le tableau de bord.
- **🇩🇿 Arabic:** تم إجراء تدقيق كامل للمشروع. التحقق من الهيكل الأساسي (النماذج، الخدمات، واجهة المستخدم). تحديد وإصلاح مشكلة مسار في `init_db.py` للسماح بالتشغيل المستقل. ملاحظة نقص مكتبة `argon2-cffi` في البيئة. التحقق من منطق التحكم في الوصول (RBAC) في لوحة التحكم.

---
### Step 10: Desktop POS Transformation - Enhancements & Seeding

**Date:** 2026-03-24

- **🇬🇧 English:** Enhanced the Dashboard with a persistent language switcher and Role-Based Access Control (RBAC) to hide Admin/Finance from cashiers. Created a `seed_data.py` script that populates the system with 30 days of realistic sales, products, and a test cashier account (`caissier` / `caissier123`). Updated the Windows run script to automate data seeding.
- **🇫🇷 French:** Amélioration du tableau de bord avec un sélecteur de langue persistant et un contrôle d'accès basé sur les rôles (RBAC) pour masquer les modules Admin/Finance aux caissiers. Création d'un script `seed_data.py` qui alimente le système avec 30 jours de ventes réalistes, de produits et un compte caissier de test (`caissier` / `caissier123`). Mise à jour du script de lancement Windows pour automatiser le peuplement des données.
- **🇩🇿 Arabic:** تحسين لوحة التحكم باستخدام مفتاح تبديل لغة ثابت والتحكم في الوصول القائم على الأدوار (RBAC) لإخفاء وحدتي الإدارة والمالية عن الصرافين. تم إنشاء نص `seed_data.py` الذي يملأ النظام بـ 30 يومًا من المبيعات والمنتجات الواقعية وحساب صراف تجريبي (`caissier` / `caissier123`). تم تحديث نص التشغيل الخاص بـ Windows لأتمتة بذر البيانات.

---
### Step 10: Desktop POS Transformation - Phase 5 (Finance Management)

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented the Finance Management module featuring real-time cash balance tracking, register open/close workflows, and withdrawal management with audit trails. Integrated a detailed financial transaction history table. The UI is fully localized and supports RTL layout for Arabic.
- **🇫🇷 French:** Implémentation du module de gestion financière avec suivi du solde de caisse en temps réel, flux d'ouverture/fermeture de caisse et gestion des retraits avec pistes d'audit. Intégration d'un tableau détaillé de l'historique des transactions financières. L'interface est entièrement localisée et supporte la mise en page RTL pour l'arabe.
- **🇩🇿 Arabic:** تم تنفيذ وحدة إدارة المالية التي تتميز بتتبع الرصيد النقدي في الوقت الفعلي، وسير عمل فتح/إغلاق الصندوق، وإدارة السحوبات مع سجلات التدقيق. تم دمج جدول مفصل لتاريخ المعاملات المالية. الواجهة معربة بالكامل وتدعم تخطيط RTL للغة العربية.

---
### Step 10: Desktop POS Transformation - Phase 5 (Parcel Management)

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented the Parcel Management module with real-time status tracking and financial collection integration. Users can now monitor delivery progress and record collected amounts directly from the dashboard. The interface is fully localized and supports dynamic layout mirroring for Arabic.
- **🇫🇷 French:** Implémentation du module de gestion des colis avec suivi du statut en temps réel et intégration de la collecte financière. Les utilisateurs peuvent désormais suivre la progression des livraisons et enregistrer les montants collectés directement depuis le tableau de bord. L'interface est entièrement localisée et supporte le miroir dynamique de mise en page pour l'arabe.
- **🇩🇿 Arabic:** تم تنفيذ وحدة إدارة الطرود مع تتبع الحالة في الوقت الفعلي ودمج تحصيل الأموال. يمكن للمستخدمين الآن مراقبة تقدم التسليم وتسجيل المبالغ المحصلة مباشرة من لوحة التحكم. الواجهة معربة بالكامل وتدعم عكس التخطيط الديناميكي للغة العربية.

---
### Step 10: Desktop POS Transformation - Phase 5 (Product Management)

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented the Product Management module with full CRUD capabilities. Added a searchable product table and an intuitive dialog for adding/editing inventory items. Integrated category selection and stock tracking with the backend services. The UI is fully localized and supports RTL layout for Arabic.
- **🇫🇷 French:** Implémentation du module de gestion des produits avec des capacités CRUD complètes. Ajout d'un tableau de produits consultable et d'un dialogue intuitif pour l'ajout/modification d'articles d'inventaire. Intégration de la sélection de catégorie et du suivi des stocks avec les services backend. L'interface est entièrement localisée et supporte la mise en page RTL pour l'arabe.
- **🇩🇿 Arabic:** تم تنفيذ وحدة إدارة المنتجات مع إمكانيات CRUD كاملة. تمت إضافة جدول منتجات قابل للبحث وحوار بديهي لإضافة/تعديل عناصر المخزون. تم دمج اختيار الفئات وتتبع المخزون مع خدمات الواجهة الخلفية. واجهة المستخدم معربة بالكامل وتدعم تخطيط RTL للغة العربية.

---
### Step 10: Desktop POS Transformation - Phase 5 (Sales Terminal)

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented a sophisticated multi-tab Sales Terminal within the main dashboard. Features include barcode scanning integration, real-time stock and price calculation, and a localized checkout process. The UI automatically adjusts to RTL layout for Arabic and updates all labels dynamically upon language switching.
- **🇫🇷 French:** Implémentation d'un terminal de vente multi-onglets sophistiqué dans le tableau de bord principal. Les fonctionnalités incluent l'intégration de la lecture de codes-barres, le calcul en temps réel des stocks et des prix, et un processus d'encaissement localisé. L'interface s'ajuste automatiquement à la mise en page RTL pour l'arabe et met à jour dynamiquement tous les libellés lors du changement de langue.
- **🇩🇿 Arabic:** تم تنفيذ محطة مبيعات متطورة متعددة علامات التبويب داخل لوحة التحكم الرئيسية. تشمل الميزات دمج مسح الرمز الشريطي (barcode)، وحساب المخزون والأسعار في الوقت الفعلي، وعملية دفع معربة. تتكيف واجهة المستخدم تلقائيًا مع تخطيط RTL للغة العربية وتحدث جميع التسميات ديناميكيًا عند تبديل اللغة.

---
### Step 10: Desktop POS Transformation - Phase 5 (UI Initial)

**Date:** 2026-03-24

- **🇬🇧 English:** Designed and implemented the first set of UI windows (`LoginWindow`, `DashboardWindow`). Established a modern CSS-based styling system with native support for Right-to-Left (RTL) mirroring and dynamic language switching. Integrated `AuthService` for secure user login. Verified UI behavior and localization through automated `pytest-qt` tests in offscreen mode.
- **🇫🇷 French:** Conception et implémentation du premier ensemble de fenêtres d'interface (`LoginWindow`, `DashboardWindow`). Établissement d'un système de style moderne basé sur CSS avec support natif du miroir Droite-à-Gauche (RTL) et du basculement dynamique de langue. Intégration d'`AuthService` pour une connexion utilisateur sécurisée. Vérification du comportement de l'interface et de la localisation via des tests automatisés `pytest-qt` en mode offscreen.
- **🇩🇿 Arabic:** تصميم وتنفيذ المجموعة الأولى من نوافذ واجهة المستخدم (`LoginWindow` و `DashboardWindow`). تأسيس نظام تنسيق حديث يعتمد على CSS مع دعم أصلي لعكس التخطيط من اليمين إلى اليسار (RTL) والتبديل الديناميكي للغة. تم دمج `AuthService` لتسجيل دخول المستخدم بشكل آمن. تم التحقق من سلوك واجهة المستخدم والترجمة من خلال اختبارات `pytest-qt` المؤتمتة في وضع عدم الاتصال (offscreen).

---
### Step 10: Desktop POS Transformation - Phase 4

**Date:** 2026-03-24

- **🇬🇧 English:** Migrated and implemented core business logic services (`ProductService`, `SaleService`, `FinanceService`, `ParcelService`). Each service is designed for offline operation with full audit logging and integrated optimistic locking to ensure data consistency. Successfully verified the complete sale-to-cash integration flow through comprehensive integration tests.
- **🇫🇷 French:** Migration et implémentation des services de logique métier (`ProductService`, `SaleService`, `FinanceService`, `ParcelService`). Chaque service est conçu pour un fonctionnement hors ligne avec une journalisation d'audit complète et un verrouillage optimiste intégré pour garantir la cohérence des données. Vérification réussie du flux d'intégration complet vente-caisse via des tests d'intégration exhaustifs.
- **🇩🇿 Arabic:** تم ترحيل وتنفيذ خدمات منطق الأعمال الأساسية (`ProductService` و `SaleService` و `FinanceService` و `ParcelService`). تم تصميم كل خدمة للعمل في وضع عدم الاتصال مع تسجيل تدقيق كامل وقفل متفائل متكامل لضمان اتساق البيانات. تم التحقق بنجاح من تدفق التكامل الكامل من البيع إلى النقد من خلال اختبارات تكامل شاملة.

---
### Step 10: Desktop POS Transformation - Phase 3

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented the full SQLite database schema using SQLAlchemy. Included optimistic locking via a `version` column to handle multi-tab sales consistency. Added dedicated tables for `audit_logs`, `sync_queue`, and financial tracking (`cash_registers`, `withdrawals`). Verified model integrity and concurrency handling with automated unit tests.
- **🇫🇷 French:** Implémentation du schéma complet de la base de données SQLite avec SQLAlchemy. Inclusion du verrouillage optimiste via une colonne `version` pour gérer la cohérence des ventes multi-onglets. Ajout de tables dédiées pour `audit_logs`, `sync_queue`, et le suivi financier (`cash_registers`, `withdrawals`). Vérification de l'intégrité des modèles et de la gestion de la concurrence avec des tests unitaires automatisés.
- **🇩🇿 Arabic:** تم تنفيذ مخطط قاعدة بيانات SQLite بالكامل باستخدام SQLAlchemy. يتضمن ذلك القفل المتفائل عبر عمود `version` لضمان اتساق المبيعات في علامات تبويب متعددة. تمت إضافة جداول مخصصة لـ `audit_logs` و `sync_queue` والتتبع المالي (`cash_registers` و `withdrawals`). تم التحقق من سلامة النماذج ومعالجة التزامن من خلال اختبارات الوحدة المؤتمتة.

---
### Step 10: Desktop POS Transformation - Phase 1 & 2

**Date:** 2026-03-24

- **🇬🇧 English:** Initialized the desktop application environment using PyQt6. Established a local-first architecture with SQLite3. Implemented a centralized `Translator` manager for dynamic switching between Arabic, French, and English, including full Right-to-Left (RTL) support for the Arabic interface.
- **🇫🇷 French:** Initialisation de l'environnement de l'application bureau avec PyQt6. Établissement d'une architecture locale-first avec SQLite3. Implémentation d'un gestionnaire `Translator` centralisé pour le basculement dynamique entre l'arabe, le français et l'anglais, incluant le support complet du mode droite-à-gauche (RTL) pour l'interface arabe.
- **🇩🇿 Arabic:** تم البدء في تهيئة بيئة تطبيق سطح المكتب باستخدام PyQt6. تأسيس بنية تعتمد على التخزين المحلي أولاً باستخدام SQLite3. تم تنفيذ مدير ترجمة (`Translator`) مركزي للتبديل الديناميكي بين اللغات العربية والفرنسية والإنجليزية، مع دعم كامل للتخطيط من اليمين إلى اليسار (RTL) للواجهة العربية.
# 🇬🇧 Project History | 🇫🇷 Historique du Projet | 🇩🇿 تاريخ المشروع

This file tracks the major development steps of the Gestion Commerce system.
Ce fichier suit les principales étapes de développement du système Gestion Commerce.
هذا الملف يتتبع خطوات التطوير الرئيسية لنظام Gestion Commerce.

---
### Step 9.5: Internationalization (i18n) - Phase 6: Error Normalization

**Date:** 2026-03-24

- **🇬🇧 English:** Refactored backend services and API routes to return structured error codes (e.g., `AUTH_INVALID_CREDENTIALS`) instead of plain text messages. Updated frontend error handling (specifically in `LoginPage`) to map these codes to user-friendly, translatable messages using `react-i18next`. This ensures errors are displayed consistently in the user's selected language.
- **🇫🇷 French:** Refonte des services backend et des routes d'API pour retourner des codes d'erreur structurés (ex: `AUTH_INVALID_CREDENTIALS`) au lieu de messages textuels bruts. Mise à jour de la gestion des erreurs côté frontend (spécifiquement dans `LoginPage`) pour mapper ces codes à des messages traduisibles et conviviaux via `react-i18next`. Cela garantit que les erreurs sont affichées de manière cohérente dans la langue sélectionnée par l'utilisateur.
- **🇩🇿 Arabic:** إعادة هيكلة خدمات الواجهة الخلفية ومسارات API لإرجاع رموز أخطاء منظمة (مثل `AUTH_INVALID_CREDENTIALS`) بدلاً من رسائل نصية بسيطة. تم تحديث معالجة الأخطاء في الواجهة الأمامية (خاصة في `LoginPage`) لربط هذه الرموز برسائل سهلة الاستخدام وقابلة للترجمة باستخدام `react-i18next`. هذا يضمن عرض الأخطاء بشكل متسق بلغة المستخدم المحددة.

---

### Step 9.5: Internationalization (i18n) - Phase 4 & 5

**Date:** 2026-03-24

- **🇬🇧 English:** Implemented a persistent language switcher component. The selected language is saved to `localStorage` for a consistent user experience. Added foundational support for Right-to-Left (RTL) layout by dynamically setting `dir="rtl"` on the HTML element when Arabic is selected.
- **🇫🇷 French:** Implémentation d'un sélecteur de langue persistant. La langue sélectionnée est sauvegardée dans le `localStorage` pour une expérience utilisateur cohérente. Ajout du support fondamental pour la mise en page de droite à gauche (RTL) en définissant dynamiquement `dir="rtl"` sur l'élément HTML lorsque l'arabe est sélectionné.
- **🇩🇿 Arabic:** تم تنفيذ مكون تبديل لغة ثابت. يتم حفظ اللغة المختارة في `localStorage` لتوفير تجربة مستخدم متسقة. تمت إضافة الدعم الأساسي للتخطيط من اليمين إلى اليسار (RTL) عن طريق تعيين `dir="rtl"` ديناميكيًا على عنصر HTML عند تحديد اللغة العربية.

---

### Step 9.5: Internationalization (i18n) - Phase 2 & 3

**Date:** 2026-03-24

- **🇬🇧 English:** All hardcoded text from UI components (`LoginPage`, `DashboardPage`) has been extracted and replaced with a structured key system (e.g., `login.title`). The JSON locale files have been populated with these keys. This decouples text from the code, making the app fully translatable and easier to maintain.
- **🇫🇷 French:** Tout le texte en dur des composants d'interface (`LoginPage`, `DashboardPage`) a été extrait et remplacé par un système de clés structurées (ex: `login.title`). Les fichiers de locales JSON ont été peuplés avec ces clés. Cela découple le texte du code, rendant l'application entièrement traduisible et plus facile à maintenir.
- **🇩🇿 Arabic:** تم استخراج كل النصوص الثابتة من مكونات واجهة المستخدم (`LoginPage`, `DashboardPage`) واستبدالها بنظام مفاتيح منظم (مثال: `login.title`). تم ملء ملفات اللغات JSON بهذه المفاتيح. هذا يفصل النص عن الكود، مما يجعل التطبيق قابلاً للترجمة بالكامل وأسهل في الصيانة.

---

### Step 9.5: Internationalization (i18n) - Phase 1

**Date:** 2026-03-24

- **🇬🇧 English:** Established the foundational architecture for multi-language support using `react-i18next`. Installed all necessary dependencies, configured the i18n provider, and set up the directory structure for French (`fr`) and Arabic (`ar`) locales. The application is now ready for text extraction.
- **🇫🇷 French:** Mise en place de l'architecture fondamentale pour le support multilingue avec `react-i18next`. Installation des dépendances nécessaires, configuration du fournisseur i18n et mise en place de la structure de répertoires pour les locales français (`fr`) et arabe (`ar`). L'application est maintenant prête pour l'extraction du texte.
- **🇩🇿 Arabic:** تم تأسيس البنية الأساسية لدعم تعدد اللغات باستخدام `react-i18next`. تم تثبيت جميع التبعيات الضرورية، وتهيئة مزود i18n، وإعداد هيكل المجلدات للغات الفرنسية (`fr`) والعربية (`ar`). التطبيق الآن جاهز لاستخراج النصوص.

---
