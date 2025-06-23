# translations.py
# English and Italian translations for PDF Duplicate Finder

TRANSLATIONS = {
    'en': {
        'app_title': 'PDF Duplicate Finder',
        'theme_menu': 'Theme',
        'light_theme': 'Light Theme',
        'dark_theme': 'Dark Theme',
        'view_menu': 'View',
        'help_menu': 'Help',
        'about_menu': 'About',
        'sponsor_menu': 'Sponsor',
        'check_updates': 'Check for Updates',
        'browse': 'Browse',
        'find_duplicates': 'Find Duplicates',
        'delete_selected': 'Delete Selected',
        'image_preview': 'Image Preview',
        'text_preview': 'Text Preview',
        'select_folder': 'Select a Folder',
        'warning': 'Warning',
        'info': 'Info',
        'error': 'Error',
        'no_files_selected': 'No files selected for deletion.',
        'files_deleted': 'Selected files have been deleted.',
        'please_select_folder': 'Please select a folder to scan.',
        'no_pdfs_found': 'No PDF files found in the selected folder.',
        'no_duplicates_found': 'No duplicate PDFs found.',
        'duplicates_found': 'Found {count} duplicate files.',
        'initializing_scan': 'Initializing scan...',
        'cancelling_search': 'Cancelling search...',
        'close': 'Close',
        'language_menu': 'Language',
        'english': 'English',
        'italian': 'Italian',
    },
    'it': {
        'app_title': 'PDF Duplicate Finder',
        'theme_menu': 'Tema',
        'light_theme': 'Tema Chiaro',
        'dark_theme': 'Tema Scuro',
        'view_menu': 'Visualizza',
        'help_menu': 'Aiuto',
        'about_menu': 'Informazioni',
        'sponsor_menu': 'Sponsorizza',
        'check_updates': 'Controlla Aggiornamenti',
        'browse': 'Sfoglia',
        'find_duplicates': 'Trova Duplicati',
        'delete_selected': 'Elimina Selezionati',
        'image_preview': 'Anteprima Immagine',
        'text_preview': 'Anteprima Testo',
        'select_folder': 'Seleziona una Cartella',
        'warning': 'Attenzione',
        'info': 'Info',
        'error': 'Errore',
        'no_files_selected': 'Nessun file selezionato per l’eliminazione.',
        'files_deleted': 'I file selezionati sono stati eliminati.',
        'please_select_folder': 'Seleziona una cartella da scansionare.',
        'no_pdfs_found': 'Nessun file PDF trovato nella cartella selezionata.',
        'no_duplicates_found': 'Nessun duplicato PDF trovato.',
        'duplicates_found': 'Trovati {count} file duplicati.',
        'initializing_scan': 'Inizializzazione scansione...',
        'cancelling_search': 'Annullamento scansione...',
        'close': 'Chiudi',
        'language_menu': 'Lingua',
        'english': 'Inglese',
        'italian': 'Italiano',
    }
}

# Helper to get translation for a key

def t(key, lang='it', **kwargs):
    text = TRANSLATIONS.get(lang, TRANSLATIONS['it']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
