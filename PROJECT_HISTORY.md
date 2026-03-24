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
