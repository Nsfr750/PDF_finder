"""
Documentation Dialog Module

This module provides a documentation viewer dialog for PDF Duplicate Finder.
It displays help documentation in multiple languages and handles navigation
between different sections of the documentation.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QPushButton, QWidget, QFrame, QMessageBox, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal as Signal, QSize, QSettings
from PyQt6.QtGui import QDesktopServices, QIcon

from script.simple_lang_manager import SimpleLanguageManager

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget as QWidgetType

# Set up logger
logger = logging.getLogger('PDFDuplicateFinder')

def _tr(key: str, default_text: str) -> str:
    """
    Helper function to translate text using the language manager.
    
    Args:
        key: Translation key
        default_text: Default text to use if translation is not found
        
    Returns:
        Translated string
    """
    try:
        return SimpleLanguageManager().tr(key, default_text)
    except Exception as e:
        logger.warning(f"Translation failed for key '{key}': {e}")
        return default_text

class DocsDialog(QDialog):
    """
    A dialog for displaying application documentation.
    
    This dialog displays help documentation in the user's preferred language
    and provides navigation between different sections of the documentation.
    
    Signals:
        language_changed: Emitted when the documentation language is changed.
                         The signal includes the new language code.
    """
    
    # Signals
    language_changed = Signal(str)  # New language code
    
    def __init__(self, parent: Optional[QWidgetType] = None, 
                 current_lang: str = 'en') -> None:
        """
        Initialize the documentation dialog.
        
        Args:
            parent: Parent widget. Defaults to None.
            current_lang: Current language code (e.g., 'en', 'it'). Defaults to 'en'.
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.current_lang = current_lang
        self.language_manager = SimpleLanguageManager()
        self.settings = QSettings("PDFDuplicateFinder", "Documentation")
        self.text_browser = None
        
        try:
            # Set up window properties
            self.setWindowTitle(_tr("docs.window_title", "Documentation"))
            self.setMinimumSize(900, 700)  # Slightly larger for better readability
            
            # Set window flags to be a proper dialog
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
            
            # Set application icon if available
            try:
                from script.resources import get_icon_path
                icon_path = get_icon_path('app_icon.png')
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
            except (ImportError, AttributeError) as e:
                logger.debug(f"Could not set window icon: {e}")
            
            # Set up UI
            self.init_ui()
            self.retranslate_ui()
            self.load_documentation()
            
            # Restore window geometry if available
            if self.settings.contains("geometry"):
                self.restoreGeometry(self.settings.value("geometry"))
            
            logger.debug("Documentation dialog initialized successfully")
            
        except Exception as e:
            error_msg = _tr("docs.error.initialization_failed_message", 
                          "Failed to initialize documentation. Please check the logs for details.")
            logger.critical(f"{error_msg}: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                _tr("Error", "Error"),
                error_msg
            )
            self.close()
    
    def _get_docs_directory(self) -> Path:
        """
        Get the path to the documentation directory.
        
        Returns:
            Path: Path to the documentation directory
            
        Raises:
            FileNotFoundError: If the documentation directory is not found
        """
        # Try different possible locations for the docs directory
        possible_paths = [
            Path(__file__).parent.parent / 'docs',  # In project root
            Path(__file__).parent / 'docs',         # In script directory
            Path('docs')                            # In current working directory
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path
                
        raise FileNotFoundError(
            f"Documentation directory not found. Tried: {[str(p) for p in possible_paths]}"
        )
    
    def init_ui(self) -> None:
        """
        Initialize the user interface.
        
        This method sets up all the UI components and their layout.
        It's called during the dialog's initialization.
        """
        try:
            # Create main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # Create text browser for documentation
            self.text_browser = QTextBrowser()
            self.text_browser.setOpenExternalLinks(True)
            self.text_browser.setOpenLinks(False)  # We'll handle link clicks manually
            self.text_browser.anchorClicked.connect(self._on_anchor_clicked)
            
            # Add text browser to main layout
            main_layout.addWidget(self.text_browser)
            
            # Create button box
            button_box = QHBoxLayout()
            button_box.addStretch()
            
            # Add language selection
            self.language_combo = QComboBox()
            self.language_combo.addItem("English", "en")
            self.language_combo.addItem("Italiano", "it")
            self.language_combo.currentIndexChanged.connect(self._on_language_changed)
            
            # Set current language
            index = self.language_combo.findData(self.current_lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            
            button_box.addWidget(QLabel(_tr("docs.language", "Language:")))
            button_box.addWidget(self.language_combo)
            button_box.addSpacing(20)
            
            # Add close button
            self.close_button = QPushButton(_tr("docs.close", "Close"))
            self.close_button.clicked.connect(self.accept)
            button_box.addWidget(self.close_button)
            
            # Add button box to main layout
            main_layout.addLayout(button_box)
            
            logger.debug("UI initialized successfully")
            
        except Exception as e:
            error_msg = self.tr("docs.ui_init_error", "Error initializing UI: {error}").format(error=str(e))
            logger.error(error_msg, exc_info=True)
            raise
    
    def retranslate_ui(self) -> None:
        """Update UI text with current translations."""
        self.setWindowTitle(_tr("docs.window_title", "Documentation"))
        self.close_button.setText(_tr("Close", "Close"))
    
    def _on_language_changed(self, index: int) -> None:
        """Handle language change event."""
        lang = self.language_combo.currentData()
        if lang != self.current_lang:
            self.change_language(lang)
    
    def change_language(self, lang_code: str) -> None:
        """
        Change the documentation language.
        
        Args:
            lang_code: Language code to change to (e.g., 'en', 'it')
        """
        if lang_code != self.current_lang:
            self.current_lang = lang_code
            self.load_documentation()
            self.retranslate_ui()
            self.language_changed.emit(lang_code)
    
    def _on_anchor_clicked(self, link: QUrl) -> None:
        """Handle clicks on links in the documentation."""
        if link.scheme() == "http" or link.scheme() == "https":
            # Open external links in default browser
            QDesktopServices.openUrl(link)
        else:
            # Handle internal links
            self.text_browser.setSource(link)
    
    def load_documentation(self) -> None:
        """Load the documentation content based on the current language."""
        try:
            if self.current_lang == 'it':
                content = self._get_italian_help()
            else:
                content = self._get_english_help()
            
            # Set HTML content with some basic styling
            css = """
            body { 
                font-family: Arial, sans-serif; 
                line-height: 1.6;
                margin: 20px;
                color: white;
            }
            h1 { color: #white; }
            h2 { color: #white; margin-top: 20px; }
            code { 
                background-color: #f5f5f5; 
                padding: 2px 5px; 
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            """
            
            styled_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>{css}</style>
            </head>
            <body>
                {content}
            </body>
            </html>
            """
            
            self.text_browser.setHtml(styled_content)
            logger.info(_tr("docs.init_success", "Documentation loaded successfully"))
            
        except Exception as e:
            error_msg = _tr("docs.error.loading_failed", "Failed to load documentation.")
            logger.error(f"{error_msg}: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                _tr("Error", "Error"),
                error_msg
            )
    
    def _get_english_help(self) -> str:
        """Return English help content."""
        return """
        <h1>PDF Duplicate Finder - Documentation</h1>
        
        <p>Welcome to the PDF Duplicate Finder documentation. This application helps you find and manage duplicate PDF files in your system.</p>
        
        <h2>Features</h2>
        <ul>
            <li>Scan directories for duplicate PDF files</li>
            <li>Compare files by content, metadata, or both</li>
            <li>Preview PDF files before taking action</li>
            <li>Easily manage and remove duplicate files</li>
            <li>Support for multiple languages</li>
        </ul>
        
        <h2>Getting Started</h2>
        <p>To start finding duplicate PDFs:</p>
        <ol>
            <li>Click on 'Add Directory' to select folders to scan</li>
            <li>Click 'Start Scan' to begin the duplicate search</li>
            <li>Review the results in the main window</li>
            <li>Use the right-click menu to manage duplicate files</li>
        </ol>
        
        <h2>Advanced Features</h2>
        <h3>Scan Options</h3>
        <p>Customize your scan with various options:</p>
        <ul>
            <li><strong>Compare by content</strong>: Compare actual file contents (slower but more accurate)</li>
            <li><strong>Compare by metadata</strong>: Compare file metadata like title, author, etc.</li>
            <li><strong>File size threshold</strong>: Set minimum file size for comparison</li>
        </ul>
        
        <h3>Preview Mode</h3>
        <p>Preview PDF files directly in the application to help identify duplicates.</p>
        
        <h2>Troubleshooting</h2>
        <p>If you encounter any issues:</p>
        <ul>
            <li>Check the log files in the application directory</li>
            <li>Make sure you have read permissions for the scanned directories</li>
            <li>Update to the latest version of the application</li>
        </ul>
        """
    
    def _get_italian_help(self) -> str:
        """Return Italian help content."""
        return """
        <h1>PDF Duplicate Finder - Documentazione</h1>
        
        <p>Benvenuti nella documentazione di PDF Duplicate Finder. Questa applicazione ti aiuta a trovare e gestire i file PDF duplicati nel tuo sistema.</p>
        
        <h2>Funzionalità</h2>
        <ul>
            <li>Scansiona le directory alla ricerca di file PDF duplicati</li>
            <li>Confronta i file per contenuto, metadati o entrambi</li>
            <li>Anteprima dei file PDF prima di intraprendere azioni</li>
            <li>Gestisci e rimuovi facilmente i file duplicati</li>
            <li>Supporto per più lingue</li>
        </ul>
        
        <h2>Per Iniziare</h2>
        <p>Per iniziare a trovare PDF duplicati:</p>
        <ol>
            <li>Fai clic su 'Aggiungi Directory' per selezionare le cartelle da scansionare</li>
            <li>Fai clic su 'Avvia Scansione' per iniziare la ricerca dei duplicati</li>
            <li>Rivedi i risultati nella finestra principale</li>
            <li>Usa il menu contestuale (tasto destro) per gestire i file duplicati</li>
        </ol>
        
        <h2>Funzionalità Avanzate</h2>
        <h3>Opzioni di Scansione</h3>
        <p>Personalizza la tua scansione con varie opzioni:</p>
        <ul>
            <li><strong>Confronta per contenuto</strong>: Confronta il contenuto effettivo dei PDF (più lento ma più accurato)</li>
            <li><strong>Confronta per metadati</strong>: Confronta i metadati dei file come titolo, autore, ecc.</li>
            <li><strong>Soglia dimensione file</strong>: Imposta la dimensione minima dei file da confrontare</li>
        </ul>
        
        <h3>Modalità Anteprima</h3>
        <p>Visualizza in anteprima i file PDF direttamente nell'applicazione per aiutare a identificare i duplicati.</p>
        
        <h2>Risoluzione dei Problemi</h2>
        <p>Se riscontri problemi:</p>
        <ul>
            <li>Controlla i file di log nella directory dell'applicazione</li>
            <li>Assicurati di avere i permessi di lettura per le directory scansionate</li>
            <li>Aggiorna all'ultima versione dell'applicazione</li>
        </ul>
        """
    
    def closeEvent(self, event) -> None:
        """Handle dialog close event."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()
        
    def tr(self, key: str, default_text: str = "") -> str:
        """
        Translate a string using the language manager.
        
        Args:
            key: The translation key
            default_text: Default text to return if translation fails
            
        Returns:
            str: The translated string or the default text if translation fails
        """
        try:
            return self.language_manager.tr(key, default_text)
        except Exception as e:
            logger.warning(f"Translation failed for key '{key}': {e}")
            return default_text if default_text else key
    
    def retranslate_ui(self) -> None:
        """
        Update the UI text based on the current language.
        
        This method should be called whenever the language is changed to update
        all user-visible strings.
        
        This method loads the appropriate docs text based on the current language
        and updates all UI elements accordingly.
        """
        try:
            if self.current_lang == 'it':
                docs_text = self._get_italian_docs()
            else:
                docs_text = self._get_english_docs()
                
            self.text_browser.setHtml(docs_text)
            logger.debug(self.tr(
                "docs.language_changed",
                "UI retranslated to {language}"
            ).format(language=self.current_lang))
            
        except Exception as e:
            logger.error(self.tr(
                "docs.translation_error",
                "Error retranslating UI: {error}"
            ).format(error=str(e)))
            # Fallback to English if translation fails
            help_text = self._get_english_help()
            self.text_browser.setHtml(help_text)
    
    def _get_italian_docs(self):
        """Return Italian text."""
        return self.tr(
            "docs.content.it",
            """
            <h1 id="pdf-duplicate-finder-guida-utente">PDF Duplicate Finder - Guida Utente</h1>
<h2 id="indice">Indice</h2>
<ol>
<li><a href="#introduzione">Introduzione</a></li>
<li><a href="#installazione">Installazione</a></li>
<li><a href="#panoramica-dellinterfaccia">Panoramica dell&#39;Interfaccia</a></li>
<li><a href="#ricerca-dei-duplicati">Ricerca dei Duplicati</a></li>
<li><a href="#gestione-dei-risultati">Gestione dei Risultati</a></li>
<li><a href="#utilizzo-del-visualizzatore-pdf">Utilizzo del Visualizzatore PDF</a></li>
<li><a href="#funzionalità-avanzate">Funzionalità Avanzate</a></li>
<li><a href="#risoluzione-dei-problemi">Risoluzione dei Problemi</a></li>
<li><a href="#domande-frequenti">Domande Frequenti</a></li>
</ol>
<h2 id="introduzione">Introduzione</h2>
<p>Benvenuto in PDF Duplicate Finder! Questa guida ti aiuterà a sfruttare al massimo le funzionalità dell&#39;applicazione per trovare e gestire i file PDF duplicati sul tuo sistema.</p>
<h2 id="installazione">Installazione</h2>
<h3 id="requisiti-di-sistema">Requisiti di Sistema</h3>
<ul>
<li>Windows 10/11, macOS 10.15+ o Linux</li>
<li>Python 3.8 o superiore</li>
<li>Minimo 4GB di RAM (8GB consigliati)</li>
<li>100MB di spazio libero su disco</li>
</ul>
<h3 id="installazione-passo-passo">Installazione Passo-Passo</h3>
<ol>
<li>Scarica l&#39;ultima versione da GitHub</li>
<li>Estrai l&#39;archivio nella cartella preferita</li>
<li>Apri un terminale/prompt dei comandi nella directory estratta</li>
<li>Esegui: <code>pip install -r requirements.txt</code></li>
<li>Avvia l&#39;applicazione: <code>python main.py</code></li>
</ol>
<h2 id="panoramica-dell-interfaccia">Panoramica dell&#39;Interfaccia</h2>
<h3 id="finestra-principale">Finestra Principale</h3>
<ul>
<li><strong>Barra dei Menu</strong>: Accesso a tutte le funzioni dell&#39;applicazione</li>
<li><strong>Barra degli Strumenti</strong>: Accesso rapido alle azioni comuni</li>
<li><strong>Elenco Directory</strong>: Mostra le cartelle in fase di scansione</li>
<li><strong>Pannello Risultati</strong>: Visualizza i duplicati trovati</li>
<li><strong>Pannello Anteprima</strong>: Mostra l&#39;anteprima dei file selezionati</li>
<li><strong>Barra di Stato</strong>: Mostra lo stato corrente e i progressi</li>
</ul>
<h3 id="navigazione">Navigazione</h3>
<ul>
<li>Usa il menu Visualizza per mostrare/nascondere i pannelli</li>
<li>I menu contestuali (tasto destro) offrono opzioni aggiuntive</li>
<li>Trascina e rilascia i file PDF direttamente nella finestra</li>
</ul>
<h2 id="ricerca-dei-duplicati">Ricerca dei Duplicati</h2>
<h3 id="scansione-di-base">Scansione di Base</h3>
<ol>
<li>Fai clic su &quot;Aggiungi Directory&quot; e seleziona una cartella da scansionare</li>
<li>Regola le impostazioni di scansione se necessario</li>
<li>Fai clic su &quot;Avvia Scansione&quot;</li>
<li>Visualizza i risultati nella finestra principale</li>
</ol>
<h3 id="opzioni-di-scansione-avanzate">Opzioni di Scansione Avanzate</h3>
<ul>
<li><strong>Confronto Contenuti</strong>: Confronta il contenuto effettivo dei PDF</li>
<li><strong>Confronto Metadati</strong>: Controlla le proprietà del documento</li>
<li><strong>Filtro Dimensione File</strong>: Ignora i file al di fuori di determinati intervalli di dimensione</li>
<li><strong>Filtro Intervallo Date</strong>: Concentrati sui file modificati in date specifiche</li>
</ul>
<h2 id="gestione-dei-risultati">Gestione dei Risultati</h2>
<h3 id="lavorare-con-i-duplicati">Lavorare con i Duplicati</h3>
<ul>
<li>Seleziona i file per visualizzare un confronto dettagliato</li>
<li>Usa le caselle di controllo per contrassegnare i file per le azioni</li>
<li>Usa il tasto destro del mouse per le opzioni del menu contestuale</li>
</ul>
<h3 id="azioni-disponibili">Azioni Disponibili</h3>
<ul>
<li><strong>Elimina</strong>: Rimuovi i file selezionati</li>
<li><strong>Sposta</strong>: Rilocalizza i file in una nuova posizione</li>
<li><strong>Apri</strong>: Visualizza i file nell&#39;applicazione predefinita</li>
<li><strong>Escludi</strong>: Aggiungi file/cartelle all&#39;elenco delle esclusioni</li>
</ul>
<h2 id="utilizzo-del-visualizzatore-pdf">Utilizzo del Visualizzatore PDF</h2>
<h3 id="navigazione">Navigazione</h3>
<ul>
<li>Usa i tasti freccia o i pulsanti a schermo per navigare tra le pagine</li>
<li>Inserisci il numero di pagina per passare direttamente a una pagina specifica</li>
<li>Usa i controlli di zoom per regolare la visualizzazione</li>
</ul>
<h3 id="funzionalit-">Funzionalità</h3>
<ul>
<li><strong>Ricerca</strong>: Trova testo all&#39;interno del documento</li>
<li><strong>Visualizzazione Anteprime</strong>: Naviga utilizzando le anteprime delle pagine</li>
<li><strong>Ruota</strong>: Ruota le pagine per una migliore visualizzazione</li>
<li><strong>Segnalibri</strong>: Salva e gestisci i segnalibri</li>
</ul>
<h2 id="funzionalit-avanzate">Funzionalità Avanzate</h2>
<h3 id="elaborazione-in-batch">Elaborazione in Batch</h3>
<ul>
<li>Elabora più file contemporaneamente</li>
<li>Crea sequenze di azioni personalizzate</li>
<li>Salva e carica profili di elaborazione</li>
</ul>
<h3 id="automazione">Automazione</h3>
<ul>
<li>Pianifica scansioni regolari</li>
<li>Imposta regole di pulizia automatica</li>
<li>Esporta i risultati della scansione in vari formati</li>
</ul>
<h2 id="risoluzione-dei-problemi">Risoluzione dei Problemi</h2>
<h3 id="problemi-comuni">Problemi Comuni</h3>
<ul>
<li><strong>Prestazioni Lente</strong>: Prova a scansionare directory più piccole o regola le impostazioni di confronto</li>
<li><strong>File Non Trovati</strong>: Controlla i permessi dei file e le esclusioni</li>
<li><strong>Blocchi dell&#39;Applicazione</strong>: Aggiorna all&#39;ultima versione e verifica i requisiti di sistema</li>
</ul>
<h3 id="file-di-log">File di Log</h3>
<ul>
<li>I log dell&#39;applicazione sono memorizzati in <code>logs/</code></li>
<li>Attiva la modalità debug per una registrazione dettagliata</li>
<li>Includi i log quando segnali problemi</li>
</ul>
<h2 id="domande-frequenti">Domande Frequenti</h2>
<h3 id="generali">Generali</h3>
<p><strong>D: I miei dati vengono inviati a server esterni?</strong>
R: No, tutta l&#39;elaborazione avviene localmente sul tuo computer.</p>
<p><strong>D: Quali tipi di file sono supportati?</strong>
R: Attualmente sono supportati solo i file PDF.</p>
<h3 id="tecniche">Tecniche</h3>
<p><strong>D: Come funziona il rilevamento dei duplicati?</strong>
R: Utilizziamo una combinazione di hashing dei file e analisi del contenuto per identificare i duplicati.</p>
<p><strong>D: Posso recuperare i file eliminati?</strong>
R: I file eliminati tramite l&#39;applicazione vengono spostati nel cestino di sistema e possono essere ripristinati da lì.</p>
<h3 id="supporto">Supporto</h3>
<p><strong>D: Come segnalo un bug?</strong>
R: Apri una segnalazione sul nostro repository GitHub con i passaggi dettagliati per riprodurre il problema.</p>
<p><strong>D: Dove posso richiedere una nuova funzionalità?</strong>
R: Le richieste di nuove funzionalità possono essere inviate tramite le issue di GitHub o il nostro forum della community.</p>
<hr>
<p><em>Ultimo aggiornamento: 20 Agosto 2025</em></p>
            """
        )
    
    def _get_english_docs(self):
        """Return English docs text."""
        return self.tr(
            "docs.content.en",
            """
            <h1 id="pdf-duplicate-finder-user-guide">PDF Duplicate Finder - User Guide</h1>
<h2 id="table-of-contents">Table of Contents</h2>
<ol>
<li><a href="#introduction">Introduction</a></li>
<li><a href="#installation">Installation</a></li>
<li><a href="#user-interface-overview">User Interface Overview</a></li>
<li><a href="#finding-duplicates">Finding Duplicates</a></li>
<li><a href="#managing-results">Managing Results</a></li>
<li><a href="#using-the-pdf-viewer">Using the PDF Viewer</a></li>
<li><a href="#advanced-features">Advanced Features</a></li>
<li><a href="#troubleshooting">Troubleshooting</a></li>
<li><a href="#frequently-asked-questions">FAQ</a></li>
</ol>
<h2 id="introduction">Introduction</h2>
<p>Welcome to PDF Duplicate Finder! This guide will help you make the most of the application&#39;s features to find and manage duplicate PDF files on your system.</p>
<h2 id="installation">Installation</h2>
<h3 id="system-requirements">System Requirements</h3>
<ul>
<li>Windows 10/11, macOS 10.15+, or Linux</li>
<li>Python 3.8 or higher</li>
<li>4GB RAM minimum (8GB recommended)</li>
<li>100MB free disk space</li>
</ul>
<h3 id="step-by-step-installation">Step-by-Step Installation</h3>
<ol>
<li>Download the latest release from GitHub</li>
<li>Extract the archive to your preferred location</li>
<li>Open a terminal/command prompt in the extracted directory</li>
<li>Run: <code>pip install -r requirements.txt</code></li>
<li>Launch the application: <code>python main.py</code></li>
</ol>
<h2 id="user-interface-overview">User Interface Overview</h2>
<h3 id="main-window">Main Window</h3>
<ul>
<li><strong>Menu Bar</strong>: Access to all application functions</li>
<li><strong>Toolbar</strong>: Quick access to common actions</li>
<li><strong>Directory List</strong>: Shows folders being scanned</li>
<li><strong>Results Panel</strong>: Displays found duplicates</li>
<li><strong>Preview Panel</strong>: Shows preview of selected files</li>
<li><strong>Status Bar</strong>: Shows current status and progress</li>
</ul>
<h3 id="navigation">Navigation</h3>
<ul>
<li>Use the View menu to toggle panels</li>
<li>Right-click context menus provide additional options</li>
<li>Drag and drop PDF files directly into the window</li>
</ul>
<h2 id="finding-duplicates">Finding Duplicates</h2>
<h3 id="basic-scan">Basic Scan</h3>
<ol>
<li>Click &quot;Add Directory&quot; and select a folder to scan</li>
<li>Adjust scan settings if needed</li>
<li>Click &quot;Start Scan&quot;</li>
<li>View results in the main window</li>
</ol>
<h3 id="advanced-scanning-options">Advanced Scanning Options</h3>
<ul>
<li><strong>Content Comparison</strong>: Compare actual PDF content</li>
<li><strong>Metadata Comparison</strong>: Check document properties</li>
<li><strong>File Size Filtering</strong>: Ignore files outside size ranges</li>
<li><strong>Date Range Filtering</strong>: Focus on files modified within specific dates</li>
</ul>
<h2 id="managing-results">Managing Results</h2>
<h3 id="working-with-duplicates">Working with Duplicates</h3>
<ul>
<li>Select files to view detailed comparison</li>
<li>Use checkboxes to mark files for actions</li>
<li>Right-click for context menu options</li>
</ul>
<h3 id="available-actions">Available Actions</h3>
<ul>
<li><strong>Delete</strong>: Remove selected files</li>
<li><strong>Move</strong>: Relocate files to a new location</li>
<li><strong>Open</strong>: View files in default application</li>
<li><strong>Exclude</strong>: Add files/folders to exclusion list</li>
</ul>
<h2 id="using-the-pdf-viewer">Using the PDF Viewer</h2>
<h3 id="navigation">Navigation</h3>
<ul>
<li>Use arrow keys or on-screen buttons to navigate pages</li>
<li>Enter page number to jump to specific page</li>
<li>Use zoom controls to adjust view</li>
</ul>
<h3 id="features">Features</h3>
<ul>
<li><strong>Search</strong>: Find text within the document</li>
<li><strong>Thumbnail View</strong>: Navigate using page thumbnails</li>
<li><strong>Rotate</strong>: Rotate pages for better viewing</li>
<li><strong>Bookmarks</strong>: Save and manage bookmarks</li>
</ul>
<h2 id="advanced-features">Advanced Features</h2>
<h3 id="batch-processing">Batch Processing</h3>
<ul>
<li>Process multiple files at once</li>
<li>Create custom action sequences</li>
<li>Save and load processing profiles</li>
</ul>
<h3 id="automation">Automation</h3>
<ul>
<li>Schedule regular scans</li>
<li>Set up automatic cleanup rules</li>
<li>Export scan results to various formats</li>
</ul>
<h2 id="troubleshooting">Troubleshooting</h2>
<h3 id="common-issues">Common Issues</h3>
<ul>
<li><strong>Slow Performance</strong>: Try scanning smaller directories or adjust comparison settings</li>
<li><strong>Files Not Found</strong>: Check file permissions and exclusions</li>
<li><strong>Crashes</strong>: Update to the latest version and check system requirements</li>
</ul>
<h3 id="log-files">Log Files</h3>
<ul>
<li>Application logs are stored in <code>logs/</code></li>
<li>Enable debug mode for detailed logging</li>
<li>Include logs when reporting issues</li>
</ul>
<h2 id="frequently-asked-questions">Frequently Asked Questions</h2>
<h3 id="general">General</h3>
<p><strong>Q: Is my data sent to any servers?</strong>
A: No, all processing happens locally on your computer.</p>
<p><strong>Q: What file types are supported?</strong>
A: Currently, only PDF files are supported.</p>
<h3 id="technical">Technical</h3>
<p><strong>Q: How does the duplicate detection work?</strong>
A: We use a combination of file hashing and content analysis to identify duplicates.</p>
<p><strong>Q: Can I recover deleted files?</strong>
A: Files deleted through the application are moved to the system recycle bin/trash and can be restored from there.</p>
<h3 id="support">Support</h3>
<p><strong>Q: How do I report a bug?</strong>
A: Please open an issue on our GitHub repository with detailed steps to reproduce.</p>
<p><strong>Q: Where can I request a new feature?</strong>
A: Feature requests can be submitted through GitHub issues or our community forum.</p>
<hr>
<p><em>Last updated: August 20, 2025</em></p>

            """
        )
    
    def on_language_changed(self, lang_code):
        """
        Handle language change event.
        
        Args:
            lang_code (str): New language code ('en' or 'it')
        """
        try:
            if lang_code != self.current_lang:
                self.current_lang = lang_code
                self.retranslate_ui()
                self.language_changed.emit(lang_code)
                
                # Update button states
                if lang_code == 'it':
                    self.it_button.setChecked(True)
                    self.en_button.setChecked(False)
                else:
                    self.en_button.setChecked(True)
                    self.it_button.setChecked(False)
                    
                logger.debug(self.tr(
                    "docs.language_switched",
                    "Language switched to {language}"
                ).format(language=lang_code))
                
        except Exception as e:
            logger.error(self.tr(
                "docs.language_switch_error",
                "Error switching language: {error}"
            ).format(error=str(e)))
    
    def open_link(self, url):
        """
        Open a link in the default web browser.
        
        Args:
            url: QUrl of the link to open
        """
        try:
            QDesktopServices.openUrl(url)
        except Exception as e:
            logger.error(self.tr(
                "docs.link_open_error",
                "Error opening link {url}: {error}"
            ).format(url=url.toString(), error=str(e)))
