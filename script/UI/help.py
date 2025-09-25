"""
Help Dialog Module

This module provides a help dialog for the PDF Duplicate Finder application.
It includes support for multiple languages and a clean, modern interface.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, 
                             QPushButton, QWidget, QFrame)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal as Signal, QSize
from PyQt6.QtGui import QDesktopServices
import os

# Import application logger
import logging

# Import language manager
from ..lang.lang_manager import SimpleLanguageManager

logger = logging.getLogger('PDFDuplicateFinder')

def _tr(key, default_text):
    """Helper function to translate text using the language manager."""
    return SimpleLanguageManager().tr(key, default_text)

class HelpDialog(QDialog):
    # Signal to notify language change
    language_changed = Signal(str)
    
    def __init__(self, parent=None, current_lang='en'):
        """
        Initialize the help dialog.
        
        Args:
            parent: Parent widget
            current_lang (str): Current language code (default: 'en')
        """
        super().__init__(parent)
        self.current_lang = current_lang
        self.language_manager = SimpleLanguageManager()
        self.setMinimumSize(800, 600)
        self.setWindowTitle(self.tr("help.window_title", "Help"))
        
        try:
            # Set up UI
            self.init_ui()
            self.retranslate_ui()
            logger.debug(self.tr(
                "help.init_success",
                "Help dialog initialized successfully"
            ))
        except Exception as e:
            logger.error(self.tr(
                "help.init_error",
                "Error initializing help dialog: {error}"
            ).format(error=str(e)))
            raise
    
    def tr(self, key, default_text):
        """Translate text using the language manager."""
        return self.language_manager.tr(key, default_text)
    
    def init_ui(self):
        """Initialize the user interface components."""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
        
            # Language selection with styled buttons
            lang_widget = QWidget()
            lang_layout = QHBoxLayout(lang_widget)
            lang_layout.setContentsMargins(0, 0, 0, 10)
        
            # Create a frame to contain the buttons
            button_frame = QFrame()
            button_frame.setFrameShape(QFrame.Shape.StyledPanel)
            button_frame.setStyleSheet("""
                QFrame {
                    border-radius: 4px;
                    padding: 20px;
                }
            """)
            
            # Create a vertical layout for the two rows
            button_layout = QVBoxLayout(button_frame)
            button_layout.setContentsMargins(15, 15, 15, 15)
            button_layout.setSpacing(15)  # More space between rows
            
            # Create two horizontal layouts for the two rows
            first_row_layout = QHBoxLayout()
            first_row_layout.setSpacing(20)  # More space between buttons
            
            second_row_layout = QHBoxLayout()
            second_row_layout.setSpacing(20)  # More space between buttons
        
            # Style for language buttons
            button_style = """
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:checked {
                    background-color: #005a9e;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """
            
            # Language data with flag emojis - same as in menu.py
            languages = [
                ('English', 'en', '🇬🇧'),
                ('Italiano', 'it', '🇮🇹'),
                ('Russian', 'ru', '🇷🇺'),
                ('Ukrainian', 'ua', '🇺🇦'),
                ('German', 'de', '🇩🇪'),
                ('French', 'fr', '🇫🇷'),
                ('Portuguese', 'pt', '🇵🇹'),
                ('Spanish', 'es', '🇪🇸'),
                ('Japanese', 'ja', '🇯🇵'),
                ('Chinese', 'zh', '🇨🇳'),
                ('Arabic', 'ar', '🇦🇪'),
                ('Hebrew', 'he', '🇮🇱'),
            ]
            
            # Create language buttons
            self.lang_buttons = {}
            for i, (name, code, flag) in enumerate(languages):
                button = QPushButton(f"{flag} {name}")
                button.setCheckable(True)
                button.setStyleSheet(button_style)
                button.clicked.connect(lambda checked, c=code: self.on_language_changed(c))
                self.lang_buttons[code] = button
                
                # Add buttons to first row (first 6 languages) or second row (remaining 6 languages)
                if i < 6:
                    first_row_layout.addWidget(button)
                else:
                    second_row_layout.addWidget(button)
            
            # Add stretch to center the buttons in each row
            first_row_layout.addStretch()
            second_row_layout.addStretch()
            
            # Add the two rows to the main button layout
            button_layout.addLayout(first_row_layout)
            button_layout.addLayout(second_row_layout)
            
            # Set current language
            for code, button in self.lang_buttons.items():
                if code == self.current_lang:
                    button.setChecked(True)
                else:
                    button.setChecked(False)
            
            # Add to main layout
            lang_layout.addStretch()
            lang_layout.addWidget(button_frame)
            
            # Text browser for help content
            self.text_browser = QTextBrowser()
            self.text_browser.setOpenExternalLinks(True)
            self.text_browser.anchorClicked.connect(self.open_link)
            
            # Close button
            self.close_btn = QPushButton(self.tr("common.close", "Close"))
            self.close_btn.clicked.connect(self.accept)
            
            # Style the close button with red background and white text
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            
            # Add widgets to layout
            layout.addWidget(lang_widget)
            layout.addWidget(self.text_browser, 1)
            layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)
            
        except Exception as e:
            logger.error(self.tr(
                "help.ui_init_error",
                "Error initializing UI: {error}"
            ).format(error=str(e)))
            raise
    
    def retranslate_ui(self):
        """
        Update the UI with the current language.
        
        This method loads the appropriate help text based on the current language
        and updates all UI elements accordingly.
        """
        try:
            # Get help text based on current language
            help_text = self._get_help_text(self.current_lang)
            
            self.text_browser.setHtml(help_text)
            logger.debug(self.tr(
                "help.language_changed",
                "UI retranslated to {language}"
            ).format(language=self.current_lang))
            
        except Exception as e:
            logger.error(self.tr(
                "help.translation_error",
                "Error retranslating UI: {error}"
            ).format(error=str(e)))
            # Fallback to English if translation fails
            try:
                fallback_text = self._get_help_text('en')
                self.text_browser.setHtml(fallback_text)
            except Exception as fallback_error:
                logger.error(f"Fallback to English also failed: {fallback_error}")
                self.text_browser.setHtml("<h1>Error</h1><p>Could not load help content.</p>")
    
    def _get_help_text(self, lang_code):
        """
        Get help text for the specified language.
        
        Args:
            lang_code (str): Language code (e.g., 'en', 'it', 'ru', etc.)
            
        Returns:
            str: HTML help text for the specified language
        """
        help_methods = {
            'en': self._get_english_help,
            'it': self._get_italian_help,
            'ru': self._get_russian_help,
            'ua': self._get_ukrainian_help,
            'de': self._get_german_help,
            'fr': self._get_french_help,
            'pt': self._get_portuguese_help,
            'es': self._get_spanish_help,
            'ja': self._get_japanese_help,
            'zh': self._get_chinese_help,
            'ar': self._get_arabic_help,
            'he': self._get_hebrew_help,
        }
        
        method = help_methods.get(lang_code, self._get_english_help)
        return method()
    
    def _get_italian_help(self):
        """Return Italian help text."""
        return self.tr(
            "help.content.it",
            """
            <h1>PDF Duplicate Finder - Aiuto</h1>
            
            <h2>Introduzione</h2>
            <p>PDF Duplicate Finder ti aiuta a trovare e gestire i file PDF duplicati sul tuo computer.</p>
            
            <h2>Come Usare il programma</h2>
            <ol>
                <li>Clicca su <b>Scansiona Cartella</b> per selezionare una directory da analizzare</li>
                <li>Esamina i gruppi di duplicati trovati</li>
                <li>Usa i pulsanti di navigazione per spostarti tra i gruppi e i file</li>
                <li>Seleziona i file e usa <b>Mantieni</b> o <b>Elimina</b> per gestire i duplicati</li>
            </ol>
            
            <h2>Nuove Funzionalità</h2>
            
            <h3>Confronto Testuale</h3>
            <p>L'applicazione ora confronta i PDF sia per contenuto che per testo. Questo aiuta a identificare i duplicati anche quando i file hanno piccole differenze visive ma contengono lo stesso testo.</p>
            <p>Regola la soglia di somiglianza del testo nelle impostazioni per controllare quanto simili devono essere i file per essere considerati duplicati.</p>
            
            <h3>Filtri Avanzati</h3>
            <p>Utilizza i filtri per restringere la ricerca:</p>
            <ul>
                <li><b>Dimensione File:</b> Filtra per dimensione minima e massima</li>
                <li><b>Data Modifica:</b> Trova file modificati in un intervallo di date specifico</li>
                <li><b>Modello Nome:</b> Cerca file che corrispondono a un modello specifico (supporta caratteri jolly)</li>
            </ul>
            
            <h3>Suggerimenti per le Prestazioni</h3>
            <ul>
                <li>Usa i filtri per ridurre il numero di file da confrontare</li>
                <li>Regola la soglia di somiglianza in base alle tue esigenze</li>
                <li>Per grandi raccolte, considera di eseguire la scansione in lotti più piccoli</li>
            </ul>
            
            <h2>Scorciatoie da Tastiera</h2>
            <ul>
                <li><b>Ctrl+O</b>: Apri cartella da scansionare</li>
                <li><b>Ctrl+Q</b>: Esci dall'applicazione</li>
                <li><b>F1</b>: Mostra questo aiuto</li>
            </ul>
            """
        )
    
    def _get_english_help(self):
        """Return English help text."""
        return self.tr(
            "help.content.en",
            """
            <h1>PDF Duplicate Finder - Help</h1>
            
            <h2>Introduction</h2>
            <p>PDF Duplicate Finder helps you find and manage duplicate PDF files on your computer.</p>
            
            <h2>How to Use</h2>
            <ol>
                <li>Click <b>Scan Folder</b> to select a directory to analyze</li>
                <li>Review the duplicate groups found</li>
                <li>Use the navigation buttons to move between groups and files</li>
                <li>Select files and use <b>Keep</b> or <b>Delete</b> to manage duplicates</li>
            </ol>
            
            <h2>New Features</h2>
            
            <h3>Text Comparison</h3>
            <p>The application now compares PDFs by both content and text. This helps identify duplicates even when the files have minor visual differences but contain the same text.</p>
            <p>Adjust the text similarity threshold in the settings to control how similar the text needs to be for files to be considered duplicates.</p>
            
            <h3>Advanced Filtering</h3>
            <p>Use filters to narrow down your search:</p>
            <ul>
                <li><b>File Size:</b> Filter by minimum and maximum file size</li>
                <li><b>Date Modified:</b> Find files modified within a specific date range</li>
                <li><b>Name Pattern:</b> Search for files matching a specific name pattern (supports wildcards)</li>
            </ul>
            
            <h3>Performance Tips</h3>
            <ul>
                <li>Use filters to reduce the number of files being compared</li>
                <li>Adjust the similarity threshold based on your needs</li>
                <li>For large collections, consider scanning in smaller batches</li>
            </ul>
            
            <h2>Keyboard Shortcuts</h2>
            <ul>
                <li><b>Ctrl+O</b>: Open folder to scan</li>
                <li><b>Ctrl+Q</b>: Quit application</li>
                <li><b>F1</b>: Show this help</li>
            </ul>
            """
        )
    
    def on_language_changed(self, lang_code):
        """
        Handle language change event.
        
        Args:
            lang_code (str): New language code
        """
        try:
            if lang_code != self.current_lang:
                self.current_lang = lang_code
                self.retranslate_ui()
                self.language_changed.emit(lang_code)
                
                # Update button states
                for code, button in self.lang_buttons.items():
                    if code == lang_code:
                        button.setChecked(True)
                    else:
                        button.setChecked(False)
                    
                logger.debug(self.tr(
                    "help.language_switched",
                    "Language switched to {language}"
                ).format(language=lang_code))
                
        except Exception as e:
            logger.error(self.tr(
                "help.language_switch_error",
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
                "help.link_open_error",
                "Error opening link {url}: {error}"
            ).format(url=url.toString(), error=str(e)))

    def _get_russian_help(self):
        """Return Russian help text."""
        return self.tr(
            "help.russian_content",
            """<h1>Справка - PDF Duplicate Finder</h1>
            
            <h2>Обзор</h2>
            <p>PDF Duplicate Finder - это приложение для поиска дубликатов PDF-файлов на вашем компьютере. Оно анализирует содержимое PDF-файлов для поиска точных и похожих дубликатов.</p>
            
            <h2>Основные функции</h2>
            <ul>
                <li><b>Поиск дубликатов</b>: Сканируйте папки для поиска дубликатов PDF-файлов</li>
                <li><b>Анализ содержимого</b>: Сравнивайте содержимое PDF-файлов для точного определения дубликатов</li>
                <li><b>Поддержка кэша</b>: Используйте кэш для ускорения повторных сканирований</li>
                <li><b>Мультиязычный интерфейс</b>: Поддержка нескольких языков</li>
            </ul>
            
            <h2>Как использовать</h2>
            <ol>
                <li>Нажмите "Открыть папку" для выбора папки для сканирования</li>
                <li>Приложение просканирует папку и найдет дубликаты PDF-файлов</li>
                <li>Просмотрите результаты в списке дубликатов</li>
                <li>Используйте контекстное меню для управления файлами</li>
            </ol>
            
            <h2>Горячие клавиши</h2>
            <ul>
                <li><b>Ctrl+O</b>: Открыть папку для сканирования</li>
                <li><b>Ctrl+Q</b>: Выйти из приложения</li>
                <li><b>F1</b>: Показать эту справку</li>
            </ul>
            """
        )

    def _get_ukrainian_help(self):
        """Return Ukrainian help text."""
        return self.tr(
            "help.ukrainian_content",
            """<h1>Довідка - PDF Duplicate Finder</h1>
            
            <h2>Огляд</h2>
            <p>PDF Duplicate Finder - це додаток для пошуку дублікатів PDF-файлів на вашому комп'ютері. Він аналізує вміст PDF-файлів для пошуку точних та схожих дублікатів.</p>
            
            <h2>Основні функції</h2>
            <ul>
                <li><b>Пошук дублікатів</b>: Скануйте папки для пошуку дублікатів PDF-файлів</li>
                <li><b>Аналіз вмісту</b>: Порівнюйте вміст PDF-файлів для точного визначення дублікатів</li>
                <li><b>Підтримка кешу</b>: Використовуйте кеш для прискорення повторних сканувань</li>
                <li><b>Багатомовний інтерфейс</b>: Підтримка кількох мов</li>
            </ul>
            
            <h2>Як використовувати</h2>
            <ol>
                <li>Натисніть "Відкрити папку" для вибору папки для сканування</li>
                <li>Додаток просканує папку і знайде дублікати PDF-файлів</li>
                <li>Перегляньте результати у списку дублікатів</li>
                <li>Використовуйте контекстне меню для керування файлами</li>
            </ol>
            
            <h2>Гарячі клавіші</h2>
            <ul>
                <li><b>Ctrl+O</b>: Відкрити папку для сканування</li>
                <li><b>Ctrl+Q</b>: Вийти з додатка</li>
                <li><b>F1</b>: Показати цю довідку</li>
            </ul>
            """
        )

    def _get_german_help(self):
        """Return German help text."""
        return self.tr(
            "help.german_content",
            """<h1>Hilfe - PDF Duplicate Finder</h1>
            
            <h2>Übersicht</h2>
            <p>PDF Duplicate Finder ist eine Anwendung zum Suchen von doppelten PDF-Dateien auf Ihrem Computer. Sie analysiert den Inhalt von PDF-Dateien, um exakte und ähnliche Duplikate zu finden.</p>
            
            <h2>Hauptfunktionen</h2>
            <ul>
                <li><b>Duplikatsuche</b>: Scannen Sie Ordner nach doppelten PDF-Dateien</li>
                <li><b>Inhaltsanalyse</b>: Vergleichen Sie den Inhalt von PDF-Dateien zur genauen Duplikaterkennung</li>
                <li><b>Cache-Unterstützung</b>: Verwenden Sie Cache zur Beschleunigung wiederholter Scans</li>
                <li><b>Mehrsprachige Benutzeroberfläche</b>: Unterstützung für mehrere Sprachen</li>
            </ul>
            
            <h2>Verwendung</h2>
            <ol>
                <li>Klicken Sie auf "Ordner öffnen" um einen Ordner zum Scannen auszuwählen</li>
                <li>Die Anwendung scannt den Ordner und findet doppelte PDF-Dateien</li>
                <li>Zeigen Sie die Ergebnisse in der Duplikatliste an</li>
                <li>Verwenden Sie das Kontextmenü zur Dateiverwaltung</li>
            </ol>
            
            <h2>Tastenkürzel</h2>
            <ul>
                <li><b>Strg+O</b>: Ordner zum Scannen öffnen</li>
                <li><b>Strg+Q</b>: Anwendung beenden</li>
                <li><b>F1</b>: Diese Hilfe anzeigen</li>
            </ul>
            """
        )

    def _get_french_help(self):
        """Return French help text."""
        return self.tr(
            "help.french_content",
            """<h1>Aide - PDF Duplicate Finder</h1>
            
            <h2>Aperçu</h2>
            <p>PDF Duplicate Finder est une application pour rechercher des fichiers PDF en double sur votre ordinateur. Elle analyse le contenu des fichiers PDF pour trouver des doublons exacts et similaires.</p>
            
            <h2>Fonctionnalités principales</h2>
            <ul>
                <li><b>Recherche de doublons</b>: Scannez des dossiers pour trouver des fichiers PDF en double</li>
                <li><b>Analyse du contenu</b>: Comparez le contenu des fichiers PDF pour une détection précise des doublons</li>
                <li><b>Support de cache</b>: Utilisez le cache pour accélérer les analyses répétées</li>
                <li><b>Interface multilingue</b>: Support pour plusieurs langues</li>
            </ul>
            
            <h2>Comment utiliser</h2>
            <ol>
                <li>Cliquez sur "Ouvrir le dossier" pour sélectionner un dossier à analyser</li>
                <li>L'application analysera le dossier et trouvera les fichiers PDF en double</li>
                <li>Affichez les résultats dans la liste des doublons</li>
                <li>Utilisez le menu contextuel pour gérer les fichiers</li>
            </ol>
            
            <h2>Raccourcis clavier</h2>
            <ul>
                <li><b>Ctrl+O</b>: Ouvrir un dossier à analyser</li>
                <li><b>Ctrl+Q</b>: Quitter l'application</li>
                <li><b>F1</b>: Afficher cette aide</li>
            </ul>
            """
        )

    def _get_portuguese_help(self):
        """Return Portuguese help text."""
        return self.tr(
            "help.portuguese_content",
            """<h1>Ajuda - PDF Duplicate Finder</h1>
            
            <h2>Visão geral</h2>
            <p>PDF Duplicate Finder é um aplicativo para encontrar arquivos PDF duplicados no seu computador. Ele analisa o conteúdo de arquivos PDF para encontrar duplicatas exatas e semelhantes.</p>
            
            <h2>Principais recursos</h2>
            <ul>
                <li><b>Busca de duplicatas</b>: Escaneie pastas para encontrar arquivos PDF duplicados</li>
                <li><b>Análise de conteúdo</b>: Compare o conteúdo de arquivos PDF para detecção precisa de duplicatas</li>
                <li><b>Suporte a cache</b>: Use cache para acelerar varreduras repetidas</li>
                <li><b>Interface multilíngue</b>: Suporte para vários idiomas</li>
            </ul>
            
            <h2>Como usar</h2>
            <ol>
                <li>Clique em "Abrir pasta" para selecionar uma pasta para escanear</li>
                <li>O aplicativo escaneará a pasta e encontrará arquivos PDF duplicados</li>
                <li>Veja os resultados na lista de duplicatas</li>
                <li>Use o menu de contexto para gerenciar arquivos</li>
            </ol>
            
            <h2>Atalhos de teclado</h2>
            <ul>
                <li><b>Ctrl+O</b>: Abrir pasta para escanear</li>
                <li><b>Ctrl+Q</b>: Sair do aplicativo</li>
                <li><b>F1</b>: Mostrar esta ajuda</li>
            </ul>
            """
        )

    def _get_spanish_help(self):
        """Return Spanish help text."""
        return self.tr(
            "help.spanish_content",
            """<h1>Ayuda - PDF Duplicate Finder</h1>
            
            <h2>Resumen</h2>
            <p>PDF Duplicate Finder es una aplicación para encontrar archivos PDF duplicados en su computadora. Analiza el contenido de los archivos PDF para encontrar duplicados exactos y similares.</p>
            
            <h2>Características principales</h2>
            <ul>
                <li><b>Búsqueda de duplicados</b>: Escanee carpetas para encontrar archivos PDF duplicados</li>
                <li><b>Análisis de contenido</b>: Compare el contenido de archivos PDF para detección precisa de duplicados</li>
                <li><b>Soporte de caché</b>: Use caché para acelerar escaneos repetidos</li>
                <li><b>Interfaz multilingüe</b>: Soporte para múltiples idiomas</li>
            </ul>
            
            <h2>Cómo usar</h2>
            <ol>
                <li>Haga clic en "Abrir carpeta" para seleccionar una carpeta para escanear</li>
                <li>La aplicación escaneará la carpeta y encontrará archivos PDF duplicados</li>
                <li>Vea los resultados en la lista de duplicados</li>
                <li>Use el menú contextual para administrar archivos</li>
            </ol>
            
            <h2>Atajos de teclado</h2>
            <ul>
                <li><b>Ctrl+O</b>: Abrir carpeta para escanear</li>
                <li><b>Ctrl+Q</b>: Salir de la aplicación</li>
                <li><b>F1</b>: Mostrar esta ayuda</li>
            </ul>
            """
        )

    def _get_japanese_help(self):
        """Return Japanese help text."""
        return self.tr(
            "help.japanese_content",
            """<h1>ヘルプ - PDF Duplicate Finder</h1>
            
            <h2>概要</h2>
            <p>PDF Duplicate Finderは、コンピューター上の重複PDFファイルを見つけるアプリケーションです。PDFファイルの内容を分析して、完全な重複ファイルと類似した重複ファイルを見つけます。</p>
            
            <h2>主な機能</h2>
            <ul>
                <li><b>重複ファイル検索</b>: フォルダをスキャンして重複PDFファイルを見つける</li>
                <li><b>内容分析</b>: PDFファイルの内容を比較して正確な重複検出を行う</li>
                <li><b>キャッシュサポート</b>: キャッシュを使用して繰り返しスキャンを高速化</li>
                <li><b>多言語インターフェース</b>: 複数の言語をサポート</li>
            </ul>
            
            <h2>使用方法</h2>
            <ol>
                <li>「フォルダを開く」をクリックしてスキャンするフォルダを選択</li>
                <li>アプリケーションがフォルダをスキャンし、重複PDFファイルを見つけます</li>
                <li>重複ファイルリストで結果を表示</li>
                <li>コンテキストメニューを使用してファイルを管理</li>
            </ol>
            
            <h2>キーボードショートカット</h2>
            <ul>
                <li><b>Ctrl+O</b>: スキャンするフォルダを開く</li>
                <li><b>Ctrl+Q</b>: アプリケーションを終了</li>
                <li><b>F1</b>: このヘルプを表示</li>
            </ul>
            """
        )

    def _get_chinese_help(self):
        """Return Chinese help text."""
        return self.tr(
            "help.chinese_content",
            """<h1>帮助 - PDF Duplicate Finder</h1>
            
            <h2>概述</h2>
            <p>PDF Duplicate Finder 是一个用于在您的计算机上查找重复PDF文件的应用程序。它分析PDF文件的内容以查找完全相同和相似的重复文件。</p>
            
            <h2>主要功能</h2>
            <ul>
                <li><b>重复文件查找</b>: 扫描文件夹以查找重复的PDF文件</li>
                <li><b>内容分析</b>: 比较PDF文件的内容以进行精确的重复检测</li>
                <li><b>缓存支持</b>: 使用缓存来加速重复扫描</li>
                <li><b>多语言界面</b>: 支持多种语言</li>
            </ul>
            
            <h2>如何使用</h2>
            <ol>
                <li>点击"打开文件夹"选择要扫描的文件夹</li>
                <li>应用程序将扫描文件夹并找到重复的PDF文件</li>
                <li>在重复文件列表中查看结果</li>
                <li>使用上下文菜单管理文件</li>
            </ol>
            
            <h2>键盘快捷键</h2>
            <ul>
                <li><b>Ctrl+O</b>: 打开文件夹进行扫描</li>
                <li><b>Ctrl+Q</b>: 退出应用程序</li>
                <li><b>F1</b>: 显示此帮助</li>
            </ul>
            """
        )

    def _get_arabic_help(self):
        """Return Arabic help text."""
        return self.tr(
            "help.arabic_content",
            """<h1>مساعدة - PDF Duplicate Finder</h1>
            
            <h2>نظرة عامة</h2>
            <p>PDF Duplicate Finder هو تطبيق للعثور على ملفات PDF المكررة على جهاز الكمبيوتر الخاص بك. يقوم بتحليل محتوى ملفات PDF للعثور على الملفات المكررة المتطابقة والمشابهة.</p>
            
            <h2>الوظائف الرئيسية</h2>
            <ul>
                <li><b>البحث عن الملفات المكررة</b>: قم بفحص المجلدات للعثور على ملفات PDF المكررة</li>
                <li><b>تحليل المحتوى</b>: قارن محتوى ملفات PDF للكشف الدقيق عن الملفات المكررة</li>
                <li><b>دعم التخزين المؤقت</b>: استخدم التخزين المؤقت لتسريع الفحوصات المتكررة</li>
                <li><b>واجهة متعددة اللغات</b>: دعم لغات متعددة</li>
            </ul>
            
            <h2>كيفة الاستخدام</h2>
            <ol>
                <li>انقر على "فتح مجلد" لتحديد مجلد للفحص</li>
                <li>سيقوم التطبيق بفحص المجلد والعثور على ملفات PDF المكررة</li>
                <li>اعرض النتائج في قائمة الملفات المكررة</li>
                <li>استخدم القائمة السياقية لإدارة الملفات</li>
            </ol>
            
            <h2>اختصارات لوحة المفاتيح</h2>
            <ul>
                <li><b>Ctrl+O</b>: فتح مجلد للفحص</li>
                <li><b>Ctrl+Q</b>: خروج من التطبيق</li>
                <li><b>F1</b>: إظهار هذه المساعدة</li>
            </ul>
            """
        )

    def _get_hebrew_help(self):
        """Return Hebrew help text."""
        return self.tr(
            "help.hebrew_content",
            """<h1>עזרה - PDF Duplicate Finder</h1>
            
            <h2>סקירה כללית</h2>
            <p>PDF Duplicate Finder היא יישום למציאת קבצי PDF כפולים במחשב שלך. היא מנתחת את התוכן של קבצי PDF כדי למצוא קבצים כפולים זהים ודומים.</p>
            
            <h2>תכונות עיקריות</h2>
            <ul>
                <li><b>חיפוש קבצים כפולים</b>: סרוק תיקיות כדי למצוא קבצי PDF כפולים</li>
                <li><b>ניתוח תוכן</b>: השווה את התוכן של קבצי PDF לזיהוי מדויק של קבצים כפולים</li>
                <li><b>תמיכה במטמון</b>: השתמש במטמון כדי להאיץ סריקות חוזרות</li>
                <li><b>ממשק רב-לשוני</b>: תמיכה במספר שפות</li>
            </ul>
            
            <h2>איך להשתמש</h2>
            <ol>
                <li>לחץ על "פתח תיקייה" כדי לבחור תיקייה לסריקה</li>
                <li>היישום יסרוק את התיקייה וימצא קבצי PDF כפולים</li>
                <li>צפה בתוצאות ברשימת הקבצים הכפולים</li>
                <li>השתמש בתפריט ההקשר כדי לנהל קבצים</li>
            </ol>
            
            <h2>קיצורי מקלדת</h2>
            <ul>
                <li><b>Ctrl+O</b>: פתח תיקייה לסריקה</li>
                <li><b>Ctrl+Q</b>: צא מהיישום</li>
                <li><b>F1</b>: הצג עזרה זו</li>
            </ul>
            """
        )
