"""
Ukrainian translations for PDF Duplicate Finder.
"""

# Translation data
TRANSLATIONS = {
    "ua": {
    # Main window
    "main_window.title": "PDF Duplicate Finder",
    "main_window.file": "Файл",
    "main_window.edit": "Редагування",
    "main_window.view": "Вигляд",
    "main_window.help": "Довідка",
    "main_window.settings": "Налаштування",
    "main_window.exit": "Вихід",
    
    # Status bar
    "ui.status_ready": "Готовий",
    
    # Common
    "common.ok": "ОК",
    "common.cancel": "Скасувати",
    "common.yes": "Так",
    "common.no": "Ні",
    "common.close": "Закрити",
    "common.save": "Зберегти",
    "common.apply": "Застосувати",
    "common.open": "Відкрити",
    "common.delete": "Видалити",
    "common.edit": "Редагувати",
    "common.help": "Довідка",
    "common.about": "Про програму",
    "common.preferences": "Параметри",
    "common.exit": "Вихід",
    "common.none": "Немає",
    
    # Settings dialog
    "settings.title": "Налаштування",
    "settings.general": "Загальні",
    "settings.appearance": "Зовнішній вигляд",
    "settings.language": "Мова",
    "settings.save": "Зберегти",
    "settings.cancel": "Скасувати",
    "settings.theme_system": "Система",
    "settings.theme_light": "Світла",
    "settings.theme_dark": "Темна",
    "settings.check_updates": "Перевіряти оновлення при запуску",
    "settings.auto_save": "Автозбереження налаштувань",
    "settings.pdf_rendering": "Відображення PDF",
    
    # Menu items
    "file.open": "Відкрити папку...",
    "file.save_results": "Зберегти результати...",
    "file.load_results": "Завантажити результати...",
    "file.settings": "Налаштування...",
    "file.exit": "Вихід",
    "edit.delete": "Видалити",
    "edit.select_all": "Виділити все",
    "view.view_log": "Переглянути журнал...",
    "view.toolbar": "Панель інструментів",
    "view.statusbar": "Рядок стану",
    "help.about": "Про програму",
    "help.sponsor": "Підтримати",
    "help.check_updates": "Перевірити оновлення",
    
    # Toolbar tooltips
    "toolbar.open_folder": "Відкрити папку для сканування",
    "toolbar.start_scan": "Почати сканування на дублікати",
    "toolbar.stop_scan": "Зупинити сканування",
    "toolbar.save_results": "Зберегти результати сканування",
    "toolbar.load_results": "Завантажити результати сканування",
    "toolbar.delete_selected": "Видалити вибрані файли",
    "toolbar.delete_all": "Видалити всі дублікати",
    "toolbar.view_log": "Переглянути журнал",
    "toolbar.settings": "Налаштування",
    "toolbar.about": "Про програму",
    
    # Progress dialog
    "progress.title": "Сканування PDF",
    "progress.scanning": "Сканування...",
    "progress.files_processed": "Оброблено файлів:",
    "progress.current_file": "Поточний файл:",
    "progress.duplicates_found": "Знайдено дублікатів:",
    "progress.cancel": "Скасувати",
    
    # Filter dialog
    "filter.title": "Фільтр результатів",
    "filter.min_size": "Мінімальний розмір (КБ):",
    "filter.max_size": "Максимальний розмір (КБ):",
    "filter.min_pages": "Мінімальна кількість сторінок:",
    "filter.max_pages": "Максимальна кількість сторінок:",
    "filter.name_contains": "Назва містить:",
    "filter.apply": "Застосувати",
    "filter.reset": "Скинути",
    "filter.cancel": "Скасувати",
    
    # Settings dialog
    "settings_dialog.title": "Налаштування",
    "settings_dialog.general_tab": "Загальні",
    "settings_dialog.appearance_tab": "Зовнішній вигляд",
    "settings_dialog.language_label": "Мова:",
    "settings_dialog.theme_label": "Тема:",
    "settings_dialog.check_updates": "Перевіряти оновлення при запуску",
    "settings_dialog.auto_save": "Автозбереження налаштувань",
    "settings_dialog.pdf_backend": "Рушій PDF:",
    "settings_dialog.test_backend": "Тестувати рушій",
    "settings_dialog.save": "Зберегти",
    "settings_dialog.cancel": "Скасувати",
    "settings_dialog.restart_required": "Потрібен перезапуск",
    "settings_dialog.restart_message": "Програму потрібно перезапустити для застосування змін мови.\nПерезапустити зараз?",
    "settings_dialog.language_changed": "Мову успішно змінено",
    "settings_dialog.language_change_failed": "Не вдалося змінити мову",
    "settings_dialog.backend_ok": "ОК",
    "settings_dialog.backend_missing": "Відсутній або невірний шлях",
    "settings_dialog.no_backends_tested": "Рушії не протестовані",
    "settings_dialog.test_results_title": "Результати тестування рушіїв",
    "settings_dialog.backend_status": "Статус рушія:",
    "settings_dialog.test_backends": "Тестувати рушії",
    
    # Main application
    "main.welcome": "Ласкаво просимо до PDF Duplicate Finder",
    "main.select_folder": "Виберіть папку для сканування PDF-файлів",
    "main.scan_started": "Сканування розпочато",
    "main.scan_completed": "Сканування завершено",
    "main.duplicates_found": "Знайдено дублікатів: {count}",
    "main.no_duplicates": "Дублікати не знайдено",
    "main.files_deleted": "{count} файлів успішно видалено.",
    "main.confirm_delete": "Ви впевнені, що хочете видалити {count} вибраних файлів?",
    "main.confirm_delete_title": "Підтвердження видалення",
    "main.file_in_use": "Файл використовується і не може бути видалений: {file}",
    "main.permission_denied": "Відмовлено в доступі при спробі видалення: {file}",
    "main.group_processed": "Оброблено групу {current}/{total}: знайдено {found} дублікатів",
    "main.retranslate_error": "Помилка в callback retranslate: {error}",
    "main.scanning_folder": "Сканування папки: {folder}",
    "main.no_pdfs_found": "PDF-файли не знайдено у вибраній папці.",
    "main.duplicates_found_groups": "Знайдено {count} потенційних груп дублікатів.",
    
    # Scanner
    "scanner.starting": "Запуск сканування...",
    "scanner.scanning": "Сканування...",
    "scanner.processing_file": "Обробка файлу: {file}",
    "scanner.comparing": "Порівняння файлів...",
    "scanner.found_duplicates": "Знайдено дублікати: {count}",
    "scanner.complete": "Сканування завершено. Знайдено {count} груп дублікатів",
    "scanner.stopped": "Сканування зупинено",
    "scanner.processing": "Обробка {current} з {total}: {file}",
    "scanner.stopping": "Зупинка сканування...",
    "scan.complete": "Сканування завершено",
    
    # PDF Viewer
    "pdf_viewer.title": "Перегляд PDF",
    "pdf_viewer.open": "Відкрити PDF",
    "pdf_viewer.previous": "Попередня",
    "pdf_viewer.next": "Наступна",
    "pdf_viewer.zoom_in": "Збільшити",
    "pdf_viewer.zoom_out": "Зменшити",
    "pdf_viewer.zoom_fit": "Підігнати за розміром",
    "pdf_viewer.zoom_100": "100%",
    "pdf_viewer.rotate_left": "Повернути ліворуч",
    "pdf_viewer.rotate_right": "Повернути праворуч",
    "pdf_viewer.file_filter": "PDF-файли (*.pdf)",
    "pdf_viewer.status.page_of": "Сторінка {current} з {total} | {width} x {height} | {zoom:.0%}",
    "pdf_viewer.page_number": "Сторінка {current} з {total}",
    "pdf_viewer.errors.open_error": "Помилка відкриття PDF",
    "pdf_viewer.errors.could_not_open": "Не вдалося відкрити {file}: {error}",
    
    # Language manager
    "language_manager.default_language_info": "Мова за замовчуванням: {language} ({code})",
    "language_manager.language_switch_success": "Успішно переключено на {language}",
    "language_manager.language_switch_failed": "Не вдалося переключитися на {language}: {error}",
    
    # Sponsor dialog
    "sponsor.title": "Підтримати розробку",
    "sponsor.message": "PDF Duplicate Finder - це безкоштовне програмне забезпечення з відкритим вихідним кодом.\n\nЯкщо вам подобається ця програма, будь ласка, розгляньте можливість підтримки її розробки.",
    "sponsor.github_sponsors": "GitHub Sponsors",
    "sponsor.patreon": "Patreon",
    "sponsor.paypal": "PayPal",
    "sponsor.monero": "Monero (XMR)",
    "sponsor.close": "Закрити",
    
    # Updates
    "updates.window_title": "Оновлення програмного забезпечення",
    "updates.current_version": "Поточна версія:",
    "updates.latest_version": "Остання версія:",
    "updates.checking": "Перевірка оновлень...",
    "updates.release_notes": "<b>Примітки до випуску:</b>",
    "updates.update_available": "Доступне оновлення!",
    "updates.no_update_available": "У вас встановлена остання версія.",
    "updates.download_update": "Завантажити оновлення",
    "updates.later": "Пізніше",
    "updates.error_checking": "Помилка при перевірці оновлень: {error}",
    
    # Log viewer
    "log_viewer.title": "Перегляд журналу",
    "log_viewer.open": "Відкрити журнал",
    "log_viewer.save": "Зберегти журнал",
    "log_viewer.clear": "Очистити журнал",
    "log_viewer.refresh": "Оновити",
    "log_viewer.filter": "Фільтр",
    "log_viewer.status.line_count": "{count} рядків",
    "log_viewer.status.last_updated": "Останнє оновлення: {time}",
    "log_viewer.errors.save_error": "Помилка при збереженні файлу журналу: {error}",
    "log_viewer.save_error": "Не вдалося зберегти файл журналу: {error}",
    
    # Theme settings
    "theme.system": "Системна",
    "theme.light": "Світла",
    "theme.dark": "Темна",
    "theme.auto": "Автоматична",
    
    # Additional UI elements
    "Open Folder": "Відкрити папку",
    "Start Scan": "Почати сканування",
    "Stop Scan": "Зупинити сканування",
    "Save Results": "Зберегти результати",
    "Load Results": "Завантажити результати",
    "Delete Selected": "Видалити вибрані",
    "Delete All Duplicates": "Видалити всі дублікати",
    "View Log": "Переглянути журнал",
    "Settings": "Налаштування",
    "About": "Про програму",
    "Exit": "Вихід",
    
    # Dialogs
    "Select Folder": "Вибрати папку",
    "Save Results": "Зберегти результати",
    "Load Results": "Завантажити результати",
    "Confirm Delete": "Підтвердити видалення",
    "Are you sure you want to delete the selected files?": "Ви впевнені, що хочете видалити вибрані файли?",
    "Error": "Помилка",
    "Information": "Інформація",
    "Warning": "Попередження",
    "Success": "Успіх",
    
    # File operations
    "File": "Файл",
    "Edit": "Редагування",
    "View": "Вигляд",
    "Help": "Довідка",
    "Select All": "Виділити все",
    "Open PDF Viewer": "Відкрити перегляд PDF",
    "Export Results to CSV": "Експортувати результати в CSV",
    "Export last scan results to a CSV file": "Експортувати останні результати сканування в CSV-файл",
    "Exit": "Вихід",
    "Exit the application": "Вийти з програми",
    
    # Progress dialog translations
    "Files processed:": "Оброблено файлів:",
    "Current file:": "Поточний файл:",
    "Duplicates found:": "Знайдено дублікатів:",
    
    # Log viewer translations
    "Failed to list log files: {}": "Не вдалося перелічити файли журналу: {}",
    "Log file not found: {path}": "Файл журналу не знайдено: {path}",
    "Failed to load log file: {}": "Не вдалося завантажити файл журналу: {}",
    "No log file selected": "Файл журналу не вибрано",
    "File: {file} | Entries: {entries} | Size: {size}": "Файл: {file} | Записи: {entries} | Розмір: {size}",
    "Confirm Delete": "Підтвердити видалення",
    "Are you sure you want to delete the log file?\nThis will permanently delete: {}\nThis action cannot be undone.": "Ви впевнені, що хочете видалити файл журналу?\nЦе призведе до безповоротного видалення: {}\nЦю дію не можна скасувати.",
    "Success": "Успіх",
    "Log file has been deleted.": "Файл журналу видалено.",
    "Failed to delete log file: {}": "Не вдалося видалити файл журналу: {}",
    "Showing {filtered} of {total} entries": "Показано {filtered} з {total} записів",
    "Failed to filter logs: {}": "Не вдалося відфільтрувати журнали: {}",
    "Confirm Clear": "Підтвердити очищення",
    "Are you sure you want to clear all logs? This cannot be undone.": "Ви впевнені, що хочете очистити всі журнали? Цю дію не можна скасувати.",
    "Failed to clear logs: {error}": "Не вдалося очистити журнали: {error}",
    "Error": "Помилка",
    
    # Toolbar translation keys (added to fix toolbar translation issues)
    "Cache Manager": "Менеджер кешу",
    "Manage PDF hash cache settings and operations": "Керування налаштуваннями та операціями кешу хешів PDF",
    "Refresh Language": "Оновити мову"
}
}

# Available languages
AVAILABLE_LANGUAGES = {
    "en": "English",
    "it": "Italiano",
    "ru": "Русский",
    "ua": "Українська",
    "de": "Deutsch",
    "fr": "Français",
    "pt": "Português",
    "es": "Español",
    "ja": "日本語",
    "zh": "中文",
    "ar": "العربية",
    "he": "עברית",
}