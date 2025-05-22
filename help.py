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

        # Help content (English and Italian)
        help_texts = {
            'en': """How to use PDF Duplicate Finder:\n\n1. Select a folder containing PDF files to scan for duplicates.\n2. Click 'Find Duplicates' to start the scanning process.\n3. The application will analyze the PDFs and display any duplicates found.\n4. For each set of duplicates:\n   - Select a file in the list to preview it\n   - Use the 'Delete Selected' button to remove unwanted duplicates\n   - Toggle between 'Image Preview' and 'Text Preview' to view different aspects of the PDF\n\nCustomization:\n- Change between Light and Dark themes from View > Theme menu\n- Theme preferences are saved between sessions\n- Adjust window size as needed - the interface is responsive\n\nTips:\n- The scanning process may take some time for large collections\n- Image-based comparison is more accurate but slower\n- Text-based comparison is faster but may miss visual duplicates\n- Always verify before deleting any files\n- Use horizontal scrollbar to view long file paths\n\nKeyboard Shortcuts:\n- Ctrl+O: Open folder\n- F5: Start new search\n- F1: Show this help\n- Ctrl+Q: Quit application\n- Delete: Remove selected files\n- Esc: Close preview\n\nFor additional support, please contact us through the 'About' section.""",
            'it': """Come usare Trova Duplicati PDF:\n\n1. Seleziona una cartella contenente file PDF da scansionare per i duplicati.\n2. Clicca su 'Trova Duplicati' per avviare la scansione.\n3. L'applicazione analizzerà i PDF e mostrerà eventuali duplicati trovati.\n4. Per ogni gruppo di duplicati:\n   - Seleziona un file nell'elenco per visualizzarlo in anteprima\n   - Usa il pulsante 'Elimina Selezionati' per rimuovere i duplicati indesiderati\n   - Passa tra 'Anteprima Immagine' e 'Anteprima Testo' per vedere diversi aspetti del PDF\n\nPersonalizzazione:\n- Cambia tra tema chiaro e scuro dal menu Visualizza > Tema\n- Le preferenze del tema vengono salvate tra le sessioni\n- Ridimensiona la finestra secondo necessità - l'interfaccia è reattiva\n\nSuggerimenti:\n- La scansione può richiedere tempo per grandi raccolte\n- Il confronto basato sulle immagini è più accurato ma più lento\n- Il confronto basato sul testo è più veloce ma può perdere duplicati visivi\n- Verifica sempre prima di eliminare i file\n- Usa la barra di scorrimento orizzontale per visualizzare percorsi lunghi\n\nScorciatoie da tastiera:\n- Ctrl+O: Apri cartella\n- F5: Nuova ricerca\n- F1: Mostra questo aiuto\n- Ctrl+Q: Chiudi applicazione\n- Canc: Rimuovi file selezionati\n- Esc: Chiudi anteprima\n\nPer ulteriore supporto, contattaci tramite la sezione 'Informazioni'."""
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
