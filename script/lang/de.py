"""
German translations for PDF Duplicate Finder.
"""

# Translation data
TRANSLATIONS = {
    "de": {
        # Main window
        "main_window.title": "PDF Duplicate Finder",
        "main_window.file": "Datei",
        "main_window.edit": "Bearbeiten",
        "main_window.view": "Ansicht",
        "main_window.help": "Hilfe",
        "main_window.settings": "Einstellungen",
        "main_window.exit": "Beenden",
        
        # Status bar
        "ui.status_ready": "Bereit",
        
        # Common
        "common.ok": "OK",
        "common.cancel": "Abbrechen",
        "common.yes": "Ja",
        "common.no": "Nein",
        "common.close": "Schließen",
        "common.save": "Speichern",
        "common.apply": "Anwenden",
        "common.open": "Öffnen",
        "common.delete": "Löschen",
        "common.edit": "Bearbeiten",
        "common.help": "Hilfe",
        "common.about": "Über",
        "common.preferences": "Einstellungen",
        "common.exit": "Beenden",
        "common.none": "Keine",
        
        # Settings dialog
        "settings.title": "Einstellungen",
        "settings.general": "Allgemein",
        "settings.appearance": "Erscheinungsbild",
        "settings.language": "Sprache",
        "settings.save": "Speichern",
        "settings.cancel": "Abbrechen",
        "settings.theme_system": "System",
        "settings.theme_light": "Hell",
        "settings.theme_dark": "Dunkel",
        "settings.check_updates": "Beim Start nach Updates suchen",
        "settings.auto_save": "Einstellungen automatisch speichern",
        "settings.pdf_rendering": "PDF-Darstellung",
        
        # Menu items
        "file.open": "Ordner öffnen...",
        "file.save_results": "Ergebnisse speichern...",
        "file.load_results": "Ergebnisse laden...",
        "file.settings": "Einstellungen...",
        "file.exit": "Beenden",
        "edit.delete": "Löschen",
        "edit.select_all": "Alle auswählen",
        "view.view_log": "Protokoll anzeigen...",
        "view.toolbar": "Symbolleiste",
        "view.statusbar": "Statusleiste",
        "help.about": "Über",
        "help.sponsor": "Sponsor",
        "help.check_updates": "Nach Updates suchen",
        
        # Toolbar tooltips
        "toolbar.open_folder": "Ordner zum Scannen öffnen",
        "toolbar.start_scan": "Scan nach Duplikaten starten",
        "toolbar.stop_scan": "Scan stoppen",
        "toolbar.save_results": "Scan-Ergebnisse speichern",
        "toolbar.load_results": "Scan-Ergebnisse laden",
        "toolbar.delete_selected": "Ausgewählte Dateien löschen",
        "toolbar.delete_all": "Alle Duplikate löschen",
        "toolbar.view_log": "Protokoll anzeigen",
        "toolbar.settings": "Einstellungen",
        "toolbar.about": "Über",
        
        # Progress dialog
        "progress.title": "PDF-Scan",
        "progress.scanning": "Scannen...",
        "progress.files_processed": "Verarbeitete Dateien:",
        "progress.current_file": "Aktuelle Datei:",
        "progress.duplicates_found": "Gefundene Duplikate:",
        "progress.cancel": "Abbrechen",
        
        # Filter dialog
        "filter.title": "Ergebnisse filtern",
        "filter.min_size": "Minimale Größe (KB):",
        "filter.max_size": "Maximale Größe (KB):",
        "filter.min_pages": "Minimale Seitenanzahl:",
        "filter.max_pages": "Maximale Seitenanzahl:",
        "filter.name_contains": "Name enthält:",
        "filter.apply": "Anwenden",
        "filter.reset": "Zurücksetzen",
        "filter.cancel": "Abbrechen",
        
        # Settings dialog
        "settings_dialog.title": "Einstellungen",
        "settings_dialog.general_tab": "Allgemein",
        "settings_dialog.appearance_tab": "Erscheinungsbild",
        "settings_dialog.language_label": "Sprache:",
        "settings_dialog.theme_label": "Design:",
        "settings_dialog.check_updates": "Beim Start nach Updates suchen",
        "settings_dialog.auto_save": "Einstellungen automatisch speichern",
        "settings_dialog.pdf_backend": "PDF-Backend:",
        "settings_dialog.test_backend": "Backend testen",
        "settings_dialog.save": "Speichern",
        "settings_dialog.cancel": "Abbrechen",
        "settings_dialog.restart_required": "Neustart erforderlich",
        "settings_dialog.restart_message": "Die Anwendung muss neu gestartet werden, um die Sprachänderungen anzuwenden.\nJetzt neu starten?",
        "settings_dialog.language_changed": "Sprache erfolgreich geändert",
        "settings_dialog.language_change_failed": "Sprachänderung fehlgeschlagen",
        "settings_dialog.backend_ok": "OK",
        "settings_dialog.backend_missing": "Fehlend oder ungültiger Pfad",
        "settings_dialog.no_backends_tested": "Keine Backends getestet",
        "settings_dialog.test_results_title": "Backend-Testergebnisse",
        "settings_dialog.backend_status": "Backend-Status:",
        "settings_dialog.test_backends": "Backends testen",
        
        # Main application
        "main.welcome": "Willkommen bei PDF Duplicate Finder",
        "main.select_folder": "Wählen Sie einen Ordner zum Scannen von PDF-Dateien",
        "main.scan_started": "Scan gestartet",
        "main.scan_completed": "Scan abgeschlossen",
        "main.duplicates_found": "Gefundene Duplikate: {count}",
        "main.no_duplicates": "Keine Duplikate gefunden",
        "main.files_deleted": "{count} Dateien erfolgreich gelöscht.",
        "main.confirm_delete": "Möchten Sie wirklich {count} ausgewählte Dateien löschen?",
        "main.confirm_delete_title": "Löschung bestätigen",
        "main.file_in_use": "Datei wird verwendet und kann nicht gelöscht werden: {file}",
        "main.permission_denied": "Zugriff verweigert beim Löschen von: {file}",
        "main.group_processed": "Gruppe {current}/{total} verarbeitet: {found} Duplikate gefunden",
        "main.retranslate_error": "Fehler im Retranslate-Callback: {error}",
        "main.scanning_folder": "Scannen des Ordners: {folder}",
        "main.no_pdfs_found": "Keine PDF-Dateien im ausgewählten Ordner gefunden.",
        "main.duplicates_found_groups": "{count} potenzielle Duplikatgruppen gefunden.",
        
        # Scanner
        "scanner.starting": "Scan wird gestartet...",
        "scanner.scanning": "Scannen...",
        "scanner.processing_file": "Verarbeite Datei: {file}",
        "scanner.comparing": "Vergleiche Dateien...",
        "scanner.found_duplicates": "Duplikate gefunden: {count}",
        "scanner.complete": "Scan abgeschlossen. {count} Duplikatgruppen gefunden",
        "scanner.stopped": "Scan gestoppt",
        "scanner.processing": "Verarbeitung {current} von {total}: {file}",
        "scanner.stopping": "Scan wird gestoppt...",
        "scan.complete": "Scan abgeschlossen",
        
        # PDF Viewer
        "pdf_viewer.title": "PDF-Anzeige",
        "pdf_viewer.open": "PDF öffnen",
        "pdf_viewer.previous": "Zurück",
        "pdf_viewer.next": "Weiter",
        "pdf_viewer.zoom_in": "Vergrößern",
        "pdf_viewer.zoom_out": "Verkleinern",
        "pdf_viewer.zoom_fit": "Anpassen",
        "pdf_viewer.zoom_100": "100%",
        "pdf_viewer.rotate_left": "Nach links drehen",
        "pdf_viewer.rotate_right": "Nach rechts drehen",
        "pdf_viewer.file_filter": "PDF-Dateien (*.pdf)",
        "pdf_viewer.status.page_of": "Seite {current} von {total} | {width} x {height} | {zoom:.0%}",
        "pdf_viewer.page_number": "Seite {current} von {total}",
        "pdf_viewer.errors.open_error": "Fehler beim Öffnen der PDF",
        "pdf_viewer.errors.could_not_open": "Konnte {file} nicht öffnen: {error}",
        
        # Language manager
        "language_manager.default_language_info": "Standardsprache: {language} ({code})",
        "language_manager.language_switch_success": "Erfolgreich zu {language} gewechselt",
        "language_manager.language_switch_failed": "Wechsel zu {language} fehlgeschlagen: {error}",
        
        # Sponsor dialog
        "sponsor.title": "Entwicklung unterstützen",
        "sponsor.message": "PDF Duplicate Finder ist eine kostenlose Open-Source-Software.\n\nWenn Ihnen diese Anwendung gefällt, unterstützen Sie bitte die Entwicklung.",
        "sponsor.github_sponsors": "GitHub Sponsors",
        "sponsor.patreon": "Patreon",
        "sponsor.paypal": "PayPal",
        "sponsor.monero": "Monero (XMR)",
        "sponsor.close": "Schließen",
        
        # Updates
        "updates.window_title": "Software-Update",
        "updates.current_version": "Aktuelle Version:",
        "updates.latest_version": "Neueste Version:",
        "updates.checking": "Nach Updates suchen...",
        "updates.release_notes": "<b>Versionshinweise:</b>",
        "updates.update_available": "Update verfügbar!",
        "updates.no_update_available": "Sie haben die neueste Version.",
        "updates.download_update": "Update herunterladen",
        "updates.later": "Später",
        "updates.error_checking": "Fehler bei der Update-Suche: {error}",
        
        # Log viewer
        "log_viewer.title": "Protokoll anzeigen",
        "log_viewer.open": "Protokoll öffnen",
        "log_viewer.save": "Protokoll speichern",
        "log_viewer.clear": "Protokoll löschen",
        "log_viewer.refresh": "Aktualisieren",
        "log_viewer.filter": "Filter",
        "log_viewer.status.line_count": "{count} Zeilen",
        "log_viewer.status.last_updated": "Letzte Aktualisierung: {time}",
        "log_viewer.errors.save_error": "Fehler beim Speichern der Protokolldatei: {error}",
        "log_viewer.save_error": "Konnte Protokolldatei nicht speichern: {error}",
        
        # Theme settings
        "theme.system": "System",
        "theme.light": "Hell",
        "theme.dark": "Dunkel",
        "theme.auto": "Automatisch",
        
        # Additional UI elements
        "Open Folder": "Ordner öffnen",
        "Start Scan": "Scan starten",
        "Stop Scan": "Scan stoppen",
        "Save Results": "Ergebnisse speichern",
        "Load Results": "Ergebnisse laden",
        "Delete Selected": "Ausgewählte löschen",
        "Delete All Duplicates": "Alle Duplikate löschen",
        "View Log": "Protokoll anzeigen",
        "Settings": "Einstellungen",
        "About": "Über",
        "Exit": "Beenden",
        
        # Dialogs
        "Select Folder": "Ordner auswählen",
        "Save Results": "Ergebnisse speichern",
        "Load Results": "Ergebnisse laden",
        "Confirm Delete": "Löschung bestätigen",
        "Are you sure you want to delete the selected files?": "Möchten Sie wirklich die ausgewählten Dateien löschen?",
        "Error": "Fehler",
        "Information": "Information",
        "Warning": "Warnung",
        "Success": "Erfolg",
        
        # File operations
        "File": "Datei",
        "Edit": "Bearbeiten",
        "View": "Ansicht",
        "Help": "Hilfe",
        "Select All": "Alle auswählen",
        "Open PDF Viewer": "PDF-Anzeige öffnen",
        "Export Results to CSV": "Ergebnisse als CSV exportieren",
        "Export last scan results to a CSV file": "Letzte Scan-Ergebnisse als CSV-Datei exportieren",
        "Exit": "Beenden",
        "Exit the application": "Anwendung beenden",
        
        # Progress dialog translations
        "Files processed:": "Verarbeitete Dateien:",
        "Current file:": "Aktuelle Datei:",
        "Duplicates found:": "Gefundene Duplikate:",
        
        # Log viewer translations
        "Failed to list log files: {}": "Protokolldateien konnten nicht aufgelistet werden: {}",
        "Log file not found: {path}": "Protokolldatei nicht gefunden: {path}",
        "Failed to load log file: {}": "Protokolldatei konnte nicht geladen werden: {}",
        "No log file selected": "Keine Protokolldatei ausgewählt",
        "File: {file} | Entries: {entries} | Size: {size}": "Datei: {file} | Einträge: {entries} | Größe: {size}",
        "Confirm Delete": "Löschung bestätigen",
        "Are you sure you want to delete the log file?\nThis will permanently delete: {}\nThis action cannot be undone.": "Möchten Sie wirklich die Protokolldatei löschen?\nDies wird dauerhaft löschen: {}\nDiese Aktion kann nicht rückgängig gemacht werden.",
        "Success": "Erfolg",
        "Log file has been deleted.": "Protokolldatei wurde gelöscht.",
        "Failed to delete log file: {}": "Protokolldatei konnte nicht gelöscht werden: {}",
        "Showing {filtered} of {total} entries": "Zeige {filtered} von {total} Einträgen",
        "Failed to filter logs: {}": "Protokolle konnten nicht gefiltert werden: {}",
        "Confirm Clear": "Löschen bestätigen",
        "Are you sure you want to clear all logs? This cannot be undone.": "Möchten Sie wirklich alle Protokolle löschen? Dies kann nicht rückgängig gemacht werden.",
        "Failed to clear logs: {error}": "Protokolle konnten nicht gelöscht werden: {error}",
        "Error": "Fehler",
        
        # Toolbar translation keys (added to fix toolbar translation issues)
        "Cache Manager": "Cache-Manager",
        "Manage PDF hash cache settings and operations": "PDF-Hash-Cache-Einstellungen und -Operationen verwalten",
        "Refresh Language": "Sprache aktualisieren"
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
