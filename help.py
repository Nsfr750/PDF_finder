import tkinter as tk
from tkinter import ttk
from translations import TRANSLATIONS, t

class HelpWindow:
    @staticmethod
    def show_help(root, lang='en'):
        help_dialog = tk.Toplevel(root)
        help_dialog.title(f"{t('app_title', lang)} - {t('help_menu', lang)}")
        help_dialog.geometry('600x500')
        help_dialog.transient(root)
        help_dialog.grab_set()

        # Store language in dialog for dynamic switching
        help_dialog.lang = lang

        # Main container with padding
        main_frame = ttk.Frame(help_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Language selection buttons
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(lang_frame, text=t('language_menu', lang)).pack(side=tk.LEFT, padx=(0, 10))
        def set_lang(new_lang):
            help_dialog.destroy()
            HelpWindow.show_help(root, lang=new_lang)
        ttk.Button(lang_frame, text=t('english', 'en'), command=lambda: set_lang('en')).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_frame, text=t('italian', 'it'), command=lambda: set_lang('it')).pack(side=tk.LEFT, padx=2)

        # Title
        title = ttk.Label(main_frame, text=f"{t('app_title', lang)} - {t('help_menu', lang)}", font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 20))

        # Create a text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, padx=10, pady=10)
        scrollbar.config(command=text.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Help content for all supported languages
        help_texts = {
            'en': """How to use PDF Duplicate Finder:

1. Select a folder containing PDF files to scan for duplicates.
2. Click 'Find Duplicates' to start the scanning process.
3. The application will analyze the PDFs and display any duplicates found.
4. For each set of duplicates:
   - Select a file in the list to preview it
   - Use the 'Delete Selected' button to remove unwanted duplicates
   - Toggle between 'Image Preview' and 'Text Preview' to view different aspects of the PDF

Customization:
- Change between Light and Dark themes from View > Theme menu
- Switch between multiple languages from View > Language menu
- Theme and language preferences are saved between sessions
- Adjust window size as needed - the interface is responsive

Tips:
- The scanning process may take some time for large collections
- Image-based comparison is more accurate but slower
- Text-based comparison is faster but may miss visual duplicates
- Always verify before deleting any files
- Use horizontal scrollbar to view long file paths
- Access recently used folders from the File menu

Keyboard Shortcuts:
- Ctrl+O: Open folder
- F5: Start new search
- F1: Show this help
- Ctrl+Q: Quit application
- Delete: Remove selected files
- Esc: Close preview
- Ctrl+Z: Undo last delete
- Ctrl+1 to Ctrl+9: Open recent folder

For additional support, please contact us through the 'About' section.""",
            'it': """Come usare Trova Duplicati PDF:

1. Seleziona una cartella contenente file PDF da scansionare per i duplicati.
2. Clicca su 'Trova Duplicati' per avviare la scansione.
3. L'applicazione analizzerà i PDF e mostrerà eventuali duplicati trovati.
4. Per ogni gruppo di duplicati:
   - Seleziona un file nell'elenco per visualizzarlo in anteprima
   - Usa il pulsante 'Elimina Selezionati' per rimuovere i duplicati indesiderati
   - Passa tra 'Anteprima Immagine' e 'Anteprima Testo' per vedere diversi aspetti del PDF

Personalizzazione:
- Cambia tra tema chiaro e scuro dal menu Visualizza > Tema
- Cambia lingua dal menu Visualizza > Lingua
- Le preferenze del tema e della lingua vengono salvate tra le sessioni
- Ridimensiona la finestra secondo necessità - l'interfaccia è reattiva

Suggerimenti:
- La scansione può richiedere tempo per grandi raccolte
- Il confronto basato sulle immagini è più accurato ma più lento
- Il confronto basato sul testo è più veloce ma può perdere duplicati visivi
- Verifica sempre prima di eliminare i file
- Usa la barra di scorrimento orizzontale per visualizzare percorsi lunghi
- Accedi alle cartelle recenti dal menu File

Scorciatoie da tastiera:
- Ctrl+O: Apri cartella
- F5: Nuova ricerca
- F1: Mostra questo aiuto
- Ctrl+Q: Chiudi applicazione
- Canc: Rimuovi file selezionati
- Esc: Chiudi anteprima
- Ctrl+Z: Annulla ultima eliminazione
- Ctrl+1 a Ctrl+9: Apri cartella recente

Per ulteriore supporto, contattaci tramite la sezione 'Informazioni'."""
        }
        text.insert(tk.END, help_texts.get(lang, help_texts['en']))
        text.config(state=tk.DISABLED)  # Make it read-only

        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        close_btn = ttk.Button(button_frame, text=t('close', lang), command=help_dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

        # Center the window
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = (help_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (height // 2)
        help_dialog.geometry(f'{width}x{height}+{x}+{y}')
