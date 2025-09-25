"""
Spanish translations for PDF Duplicate Finder.
"""

# Translation data
TRANSLATIONS = {
    "es": {
        # Main window
        "main_window.title": "PDF Duplicate Finder",
        "main_window.file": "Archivo",
        "main_window.edit": "Editar",
        "main_window.view": "Ver",
        "main_window.help": "Ayuda",
        "main_window.settings": "Configuración",
        "main_window.exit": "Salir",
        
        # Status bar
        "ui.status_ready": "Listo",
        
        # Common
        "common.ok": "OK",
        "common.cancel": "Cancelar",
        "common.yes": "Sí",
        "common.no": "No",
        "common.close": "Cerrar",
        "common.save": "Guardar",
        "common.apply": "Aplicar",
        "common.open": "Abrir",
        "common.delete": "Eliminar",
        "common.edit": "Editar",
        "common.help": "Ayuda",
        "common.about": "Acerca de",
        "common.preferences": "Preferencias",
        "common.exit": "Salir",
        "common.none": "Ninguno",
        
        # Settings dialog
        "settings.title": "Configuración",
        "settings.general": "General",
        "settings.appearance": "Apariencia",
        "settings.language": "Idioma",
        "settings.save": "Guardar",
        "settings.cancel": "Cancelar",
        "settings.theme_system": "Sistema",
        "settings.theme_light": "Claro",
        "settings.theme_dark": "Oscuro",
        "settings.check_updates": "Verificar actualizaciones al inicio",
        "settings.auto_save": "Guardar configuración automáticamente",
        "settings.pdf_rendering": "Renderizado PDF",
        
        # Menu items
        "file.open": "Abrir carpeta...",
        "file.save_results": "Guardar resultados...",
        "file.load_results": "Cargar resultados...",
        "file.settings": "Configuración...",
        "file.exit": "Salir",
        "edit.delete": "Eliminar",
        "edit.select_all": "Seleccionar todo",
        "view.view_log": "Ver registro...",
        "view.toolbar": "Barra de herramientas",
        "view.statusbar": "Barra de estado",
        "help.about": "Acerca de",
        "help.sponsor": "Patrocinar",
        "help.check_updates": "Verificar actualizaciones",
        
        # Toolbar tooltips
        "toolbar.open_folder": "Abrir carpeta para escaneo",
        "toolbar.start_scan": "Iniciar escaneo de duplicados",
        "toolbar.stop_scan": "Detener escaneo",
        "toolbar.save_results": "Guardar resultados del escaneo",
        "toolbar.load_results": "Cargar resultados del escaneo",
        "toolbar.delete_selected": "Eliminar archivos seleccionados",
        "toolbar.delete_all": "Eliminar todos los duplicados",
        "toolbar.view_log": "Ver registro",
        "toolbar.settings": "Configuración",
        "toolbar.about": "Acerca de",
        
        # Progress dialog
        "progress.title": "Escaneo PDF",
        "progress.scanning": "Escaneando...",
        "progress.files_processed": "Archivos procesados:",
        "progress.current_file": "Archivo actual:",
        "progress.duplicates_found": "Duplicados encontrados:",
        "progress.cancel": "Cancelar",
        
        # Filter dialog
        "filter.title": "Filtrar resultados",
        "filter.min_size": "Tamaño mínimo (KB):",
        "filter.max_size": "Tamaño máximo (KB):",
        "filter.min_pages": "Número mínimo de páginas:",
        "filter.max_pages": "Número máximo de páginas:",
        "filter.name_contains": "Nombre contiene:",
        "filter.apply": "Aplicar",
        "filter.reset": "Restablecer",
        "filter.cancel": "Cancelar",
        
        # Settings dialog
        "settings_dialog.title": "Configuración",
        "settings_dialog.general_tab": "General",
        "settings_dialog.appearance_tab": "Apariencia",
        "settings_dialog.language_label": "Idioma:",
        "settings_dialog.theme_label": "Tema:",
        "settings_dialog.check_updates": "Verificar actualizaciones al inicio",
        "settings_dialog.auto_save": "Guardar configuración automáticamente",
        "settings_dialog.pdf_backend": "Backend PDF:",
        "settings_dialog.test_backend": "Probar backend",
        "settings_dialog.save": "Guardar",
        "settings_dialog.cancel": "Cancelar",
        "settings_dialog.restart_required": "Reinicio necesario",
        "settings_dialog.restart_message": "La aplicación necesita reiniciarse para aplicar los cambios de idioma.\n¿Reiniciar ahora?",
        "settings_dialog.language_changed": "Idioma cambiado exitosamente",
        "settings_dialog.language_change_failed": "Error al cambiar idioma",
        "settings_dialog.backend_ok": "OK",
        "settings_dialog.backend_missing": "Ausente o ruta inválida",
        "settings_dialog.no_backends_tested": "Ningún backend probado",
        "settings_dialog.test_results_title": "Resultados de prueba de backends",
        "settings_dialog.backend_status": "Estado del backend:",
        "settings_dialog.test_backends": "Probar backends",
        
        # Main application
        "main.welcome": "Bienvenido a PDF Duplicate Finder",
        "main.select_folder": "Seleccione una carpeta para escanear archivos PDF",
        "main.scan_started": "Escaneo iniciado",
        "main.scan_completed": "Escaneo completado",
        "main.duplicates_found": "Duplicados encontrados: {count}",
        "main.no_duplicates": "No se encontraron duplicados",
        "main.files_deleted": "{count} archivos eliminados exitosamente.",
        "main.confirm_delete": "¿Está seguro de que desea eliminar {count} archivos seleccionados?",
        "main.confirm_delete_title": "Confirmar eliminación",
        "main.file_in_use": "El archivo está en uso y no puede ser eliminado: {file}",
        "main.permission_denied": "Permiso denegado al intentar eliminar: {file}",
        "main.group_processed": "Grupo {current}/{total} procesado: {found} duplicados encontrados",
        "main.retranslate_error": "Error en callback retranslate: {error}",
        "main.scanning_folder": "Escaneando carpeta: {folder}",
        "main.no_pdfs_found": "No se encontraron archivos PDF en la carpeta seleccionada.",
        "main.duplicates_found_groups": "{count} grupos potenciales de duplicados encontrados.",
        
        # Scanner
        "scanner.starting": "Iniciando escaneo...",
        "scanner.scanning": "Escaneando...",
        "scanner.processing_file": "Procesando archivo: {file}",
        "scanner.comparing": "Comparando archivos...",
        "scanner.found_duplicates": "Duplicados encontrados: {count}",
        "scanner.complete": "Escaneo completado. {count} grupos de duplicados encontrados",
        "scanner.stopped": "Escaneo detenido",
        "scanner.processing": "Procesando {current} de {total}: {file}",
        "scanner.stopping": "Deteniendo escaneo...",
        "scan.complete": "Escaneo completado",
        
        # PDF Viewer
        "pdf_viewer.title": "Visor PDF",
        "pdf_viewer.open": "Abrir PDF",
        "pdf_viewer.previous": "Anterior",
        "pdf_viewer.next": "Siguiente",
        "pdf_viewer.zoom_in": "Acercar",
        "pdf_viewer.zoom_out": "Alejar",
        "pdf_viewer.zoom_fit": "Ajustar",
        "pdf_viewer.zoom_100": "100%",
        "pdf_viewer.rotate_left": "Girar a la izquierda",
        "pdf_viewer.rotate_right": "Girar a la derecha",
        "pdf_viewer.file_filter": "Archivos PDF (*.pdf)",
        "pdf_viewer.status.page_of": "Página {current} de {total} | {width} x {height} | {zoom:.0%}",
        "pdf_viewer.page_number": "Página {current} de {total}",
        "pdf_viewer.errors.open_error": "Error al abrir PDF",
        "pdf_viewer.errors.could_not_open": "No se pudo abrir {file}: {error}",
        
        # Language manager
        "language_manager.default_language_info": "Idioma predeterminado: {language} ({code})",
        "language_manager.language_switch_success": "Cambiado a {language} exitosamente",
        "language_manager.language_switch_failed": "Error al cambiar a {language}: {error}",
        
        # Sponsor dialog
        "sponsor.title": "Patrocinar el desarrollo",
        "sponsor.message": "PDF Duplicate Finder es un software gratuito y de código abierto.\n\nSi te gusta esta aplicación, por favor considera apoyar su desarrollo.",
        "sponsor.github_sponsors": "GitHub Sponsors",
        "sponsor.patreon": "Patreon",
        "sponsor.paypal": "PayPal",
        "sponsor.monero": "Monero (XMR)",
        "sponsor.close": "Cerrar",
        
        # Updates
        "updates.window_title": "Actualización de software",
        "updates.current_version": "Versión actual:",
        "updates.latest_version": "Versión más reciente:",
        "updates.checking": "Verificando actualizaciones...",
        "updates.release_notes": "<b>Notas de lanzamiento:</b>",
        "updates.update_available": "¡Actualización disponible!",
        "updates.no_update_available": "Tienes la versión más reciente.",
        "updates.download_update": "Descargar actualización",
        "updates.later": "Más tarde",
        "updates.error_checking": "Error al verificar actualizaciones: {error}",
        
        # Log viewer
        "log_viewer.title": "Ver registro",
        "log_viewer.open": "Abrir registro",
        "log_viewer.save": "Guardar registro",
        "log_viewer.clear": "Limpiar registro",
        "log_viewer.refresh": "Actualizar",
        "log_viewer.filter": "Filtro",
        "log_viewer.status.line_count": "{count} líneas",
        "log_viewer.status.last_updated": "Última actualización: {time}",
        "log_viewer.errors.save_error": "Error al guardar archivo de registro: {error}",
        "log_viewer.save_error": "No se pudo guardar archivo de registro: {error}",
        
        # Theme settings
        "theme.system": "Sistema",
        "theme.light": "Claro",
        "theme.dark": "Oscuro",
        "theme.auto": "Automático",
        
        # Additional UI elements
        "Open Folder": "Abrir carpeta",
        "Start Scan": "Iniciar escaneo",
        "Stop Scan": "Detener escaneo",
        "Save Results": "Guardar resultados",
        "Load Results": "Cargar resultados",
        "Delete Selected": "Eliminar seleccionados",
        "Delete All Duplicates": "Eliminar todos los duplicados",
        "View Log": "Ver registro",
        "Settings": "Configuración",
        "About": "Acerca de",
        "Exit": "Salir",
        
        # Dialogs
        "Select Folder": "Seleccionar carpeta",
        "Save Results": "Guardar resultados",
        "Load Results": "Cargar resultados",
        "Confirm Delete": "Confirmar eliminación",
        "Are you sure you want to delete the selected files?": "¿Está seguro de que desea eliminar los archivos seleccionados?",
        "Error": "Error",
        "Information": "Información",
        "Warning": "Advertencia",
        "Success": "Éxito",
        
        # File operations
        "File": "Archivo",
        "Edit": "Editar",
        "View": "Ver",
        "Help": "Ayuda",
        "Select All": "Seleccionar todo",
        "Open PDF Viewer": "Abrir visor PDF",
        "Export Results to CSV": "Exportar resultados a CSV",
        "Export last scan results to a CSV file": "Exportar últimos resultados de escaneo a un archivo CSV",
        "Exit": "Salir",
        "Exit the application": "Salir de la aplicación",
        
        # Progress dialog translations
        "Files processed:": "Archivos procesados:",
        "Current file:": "Archivo actual:",
        "Duplicates found:": "Duplicados encontrados:",
        
        # Log viewer translations
        "Failed to list log files: {}": "Error al listar archivos de registro: {}",
        "Log file not found: {path}": "Archivo de registro no encontrado: {path}",
        "Failed to load log file: {}": "Error al cargar archivo de registro: {}",
        "No log file selected": "Ningún archivo de registro seleccionado",
        "File: {file} | Entries: {entries} | Size: {size}": "Archivo: {file} | Entradas: {entries} | Tamaño: {size}",
        "Confirm Delete": "Confirmar eliminación",
        "Are you sure you want to delete the log file?\nThis will permanently delete: {}\nThis action cannot be undone.": "¿Está seguro de que desea eliminar el archivo de registro?\nEsto eliminará permanentemente: {}\nEsta acción no se puede deshacer.",
        "Success": "Éxito",
        "Log file has been deleted.": "El archivo de registro ha sido eliminado.",
        "Failed to delete log file: {}": "Error al eliminar archivo de registro: {}",
        "Showing {filtered} of {total} entries": "Mostrando {filtered} de {total} entradas",
        "Failed to filter logs: {}": "Error al filtrar registros: {}",
        "Confirm Clear": "Confirmar limpieza",
        "Are you sure you want to clear all logs? This cannot be undone.": "¿Está seguro de que desea limpiar todos los registros? Esto no se puede deshacer.",
        "Failed to clear logs: {error}": "Error al limpiar registros: {error}",
        "Error": "Error",
        
        # Toolbar translation keys (added to fix toolbar translation issues)
        "Cache Manager": "Gestor de Caché",
        "Manage PDF hash cache settings and operations": "Gestionar configuración y operaciones de caché de hash PDF",
        "Refresh Language": "Actualizar Idioma"
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
