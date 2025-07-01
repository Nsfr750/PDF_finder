import os
import sys

# Aggiungi la directory principale al percorso di Python
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import ttk
from lang.translations import TRANSLATIONS, t

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
        ttk.Button(lang_frame, text=t('spanish', 'es'), command=lambda: set_lang('es')).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_frame, text=t('portuguese', 'pt'), command=lambda: set_lang('pt')).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_frame, text=t('russian', 'ru'), command=lambda: set_lang('ru')).pack(side=tk.LEFT, padx=2)
        ttk.Button(lang_frame, text=t('arabic', 'ar'), command=lambda: set_lang('ar')).pack(side=tk.LEFT, padx=2)

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
            'en': """# PDF Duplicate Finder - User Guide

## Getting Started

1. **Select a folder** containing PDF files to scan for duplicates.
   - Use the 'Browse' button or drag and drop a folder
   - Recent folders are available under 'File > Recent Folders'

2. **Scan for duplicates**
   - Click 'Scan' to start the duplicate detection process
   - Progress will be shown in the status bar
   - Cancel the scan at any time with 'Cancel'

## Working with Results

- **Preview files** by selecting them in the list
  - View both images and text content
  - Navigate between pages with the arrow buttons

- **Manage duplicates**
  - Select files to keep or delete
  - Use 'Delete Selected' to remove unwanted duplicates
  - 'Undo Delete' (Ctrl+Z) to restore recently deleted files

## Features

- **Quick Compare Mode**
  - Toggle Quick Compare mode for faster scanning
  - Compares files by size only (faster but less accurate)
  - Toggle via the checkbox in the main window or in Settings
  - Perfect for initial scans of large collections

- **Multi-language Support**
  - Change language from View > Language
  - Supports English, Italian, Spanish, Portuguese, Russian, and Arabic

- **Themes**
  - Switch between light and dark themes
  - Theme preference is saved between sessions

- **Automatic Updates**
  - Automatically checks for updates on startup
  - Manual check via Help > Check for Updates

## Tips

- Use Quick Compare mode for initial scans of large collections
- For more accurate results, run a full scan (with Quick Compare off) on suspicious files
- Use keyboard shortcuts for faster navigation
- Check the status bar for progress and messages
- Report any issues on our GitHub repository

## How to Scan for Duplicates

1. Select a folder containing PDF files
2. Choose between Quick Compare (faster) or full comparison (more accurate)
3. Click 'Find Duplicates' to start the scanning process.
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
            'it': """# PDF Duplicate Finder - Guida utente

## Per iniziare

1. **Selezionare una cartella** contenente i file PDF da scansionare alla ricerca di duplicati.
   - Utilizzare il pulsante “Sfoglia” o trascinare e rilasciare una cartella.
   - Le cartelle recenti sono disponibili in “File > Cartelle recenti”.

2. **Cercare i duplicati**
   - Fare clic su “Scansiona” per avviare il processo di rilevamento dei duplicati.
   - L'avanzamento verrà visualizzato nella barra di stato.
   - È possibile annullare la scansione in qualsiasi momento con “Annulla”.

## Utilizzo dei risultati

- **Anteprima dei file** selezionandoli nell'elenco.
  - Visualizzazione di immagini e contenuto testuale.
  - Navigazione tra le pagine con i pulsanti freccia.

- **Gestione dei duplicati**
  - Seleziona i file da conservare o eliminare
  - Usa “Elimina selezionati” per rimuovere i duplicati indesiderati
  - “Annulla eliminazione” (Ctrl+Z) per ripristinare i file eliminati di recente

## Funzionalità

- **Modalità di confronto rapido**
  - Attiva/disattiva la modalità di confronto rapido per una scansione più veloce
  - Confronta i file solo in base alle dimensioni (più veloce ma meno accurato)
  - Attiva/disattiva tramite la casella di controllo nella finestra principale o in Impostazioni
  - Perfetta per le scansioni iniziali di raccolte di grandi dimensioni

- **Supporto multilingue**
  - Cambia la lingua da Visualizza > Lingua
  - Supporta inglese, italiano, spagnolo, portoghese, russo e arabo

- **Temi**
  - Passa dal tema chiaro a quello scuro e viceversa
  - Le preferenze relative al tema vengono salvate tra una sessione e l'altra

- **Aggiornamenti automatici**
  - Verifica automaticamente la disponibilità di aggiornamenti all'avvio
  - Verifica manuale tramite Aiuto > Verifica aggiornamenti

## Suggerimenti

- Utilizza la modalità Confronto rapido per le scansioni iniziali di raccolte di grandi dimensioni
- Per risultati più accurati, esegui una scansione completa (con Confronto rapido disattivato) sui file sospetti
- Utilizza le scorciatoie da tastiera per una navigazione più veloce
- Controlla la barra di stato per lo stato di avanzamento e i messaggi
- Segnalare eventuali problemi sul nostro repository GitHub

## Come eseguire la scansione dei duplicati

1. Selezionare una cartella contenente file PDF
2. Scegliere tra Confronto rapido (più veloce) o confronto completo (più accurato)
3. Fare clic su “Trova duplicati” per avviare il processo di scansione.
3. L'applicazione analizzerà i PDF e visualizzerà eventuali duplicati trovati.
4. Per ogni serie di duplicati:
   - Seleziona un file nell'elenco per visualizzarne l'anteprima
   - Utilizza il pulsante “Elimina selezionati” per rimuovere i duplicati indesiderati
   - Passa da “Anteprima immagine” ad “Anteprima testo” per visualizzare diversi aspetti del PDF

Personalizzazione:
- Passa dal tema chiaro a quello scuro dal menu Visualizza > Tema
- Passa da una lingua all'altra dal menu Visualizza > Lingua
- Le preferenze relative al tema e alla lingua vengono salvate tra una sessione e l'altra
- Regola le dimensioni della finestra in base alle tue esigenze: l'interfaccia è reattiva

Suggerimenti:
- Il processo di scansione potrebbe richiedere del tempo per raccolte di grandi dimensioni
- Il confronto basato sulle immagini è più accurato ma più lento
- Il confronto basato sul testo è più veloce ma potrebbe non rilevare i duplicati visivi
- Verifica sempre prima di eliminare qualsiasi file
- Utilizza la barra di scorrimento orizzontale per visualizzare i percorsi dei file lunghi
- Accedi alle cartelle utilizzate di recente dal menu File

Scorciatoie da tastiera:
- Ctrl+O: Apri cartella
- F5: Avvia nuova ricerca
- F1: Mostra questa guida
- Ctrl+Q: Esci dall'applicazione
- Cancella: Rimuovi i file selezionati
- Esc: Chiudi anteprima
- Ctrl+Z: Annulla ultima eliminazione
- Da Ctrl+1 a Ctrl+9: Apri cartella recente

Per ulteriore assistenza, contattaci tramite la sezione “Informazioni”.""",
'es': """# PDF Duplicate Finder - Guía del usuario

## Introducción

1. **Seleccione una carpeta** que contenga archivos PDF para buscar duplicados.
   - Utilice el botón «Examinar» o arrastre y suelte una carpeta.
   - Las carpetas recientes están disponibles en «Archivo > Carpetas recientes».

2. **Busque duplicados**
   - Haga clic en «Escanear» para iniciar el proceso de detección de duplicados.
   - El progreso se mostrará en la barra de estado.
   - Cancele el escaneo en cualquier momento con «Cancelar».

## Trabajar con los resultados

- **Previsualice los archivos** seleccionándolos en la lista.
  - Vea tanto las imágenes como el contenido de texto.
  - Navegue entre las páginas con los botones de flecha.

- **Gestione los duplicados**
  - Seleccione los archivos que desea conservar o eliminar.
  - Utilice «Eliminar seleccionados» para eliminar los duplicados no deseados.
  - «Deshacer eliminación» (Ctrl+Z) para restaurar los archivos eliminados recientemente.

## Características

- **Modo de comparación rápida**
  - Active el modo de comparación rápida para un escaneo más rápido.
  - Compara los archivos solo por tamaño (más rápido pero menos preciso).
  - Actívelo mediante la casilla de verificación de la ventana principal o en Configuración
  - Perfecto para escaneos iniciales de colecciones grandes

- **Soporte multilingüe**
  - Cambie el idioma en Ver > Idioma
  - Admite inglés, italiano, español, portugués, ruso y árabe

- **Temas**
  - Cambie entre temas claros y oscuros
  - La preferencia de tema se guarda entre sesiones

- **Actualizaciones automáticas**
  - Comprueba automáticamente si hay actualizaciones al iniciar
  - Comprobación manual a través de Ayuda > Buscar actualizaciones

## Consejos

- Utilice el modo Comparación rápida para los escaneos iniciales de colecciones grandes
- Para obtener resultados más precisos, ejecute un escaneo completo (con la Comparación rápida desactivada) en los archivos sospechosos
- Utilice los atajos de teclado para una navegación más rápida
- Compruebe la barra de estado para ver el progreso y los mensajes
- Informe de cualquier problema en nuestro repositorio GitHub

## Cómo buscar duplicados

1. Seleccione una carpeta que contenga archivos PDF
2. Elija entre Comparación rápida (más rápida) o Comparación completa (más precisa)
3. Haga clic en «Buscar duplicados» para iniciar el proceso de análisis.
3. La aplicación analizará los PDF y mostrará los duplicados encontrados.
4. Para cada conjunto de duplicados:
   - Seleccione un archivo de la lista para obtener una vista previa.
   - Utilice el botón «Eliminar seleccionados» para eliminar los duplicados no deseados.
   - Alterne entre «Vista previa de imagen» y «Vista previa de texto» para ver diferentes aspectos del PDF.

Personalización:
- Cambie entre los temas claro y oscuro en el menú Ver > Tema.
- Cambie entre varios idiomas en el menú Ver > Idioma.
- Las preferencias de tema e idioma se guardan entre sesiones.
- Ajuste el tamaño de la ventana según sea necesario: la interfaz es responsiva.

Consejos:
- El proceso de escaneo puede tardar algún tiempo en colecciones grandes.
- La comparación basada en imágenes es más precisa, pero más lenta.
- La comparación basada en texto es más rápida, pero puede pasar por alto duplicados visuales.
- Verifique siempre antes de eliminar cualquier archivo.
- Utilice la barra de desplazamiento horizontal para ver rutas de archivo largas.
- Acceda a las carpetas utilizadas recientemente desde el menú Archivo.

Atajos de teclado:
- Ctrl+O: Abrir carpeta
- F5: Iniciar nueva búsqueda
- F1: Mostrar esta ayuda
- Ctrl+Q: Salir de la aplicación
- Suprimir: Eliminar los archivos seleccionados
- Esc: Cerrar vista previa
- Ctrl+Z: Deshacer la última eliminación
- Ctrl+1 a Ctrl+9: Abrir carpeta reciente

Para obtener asistencia adicional, póngase en contacto con nosotros a través de la sección «Acerca de».""",

'pt': """# PDF Duplicate Finder - Guia do utilizador

## Introdução

1. **Selecione uma pasta** que contenha ficheiros PDF para procurar duplicados.
   - Use o botão «Procurar» ou arraste e solte uma pasta.
   - As pastas recentes estão disponíveis em «Ficheiro > Pastas recentes».

2. **Procure duplicados**
   - Clique em «Verificar» para iniciar o processo de deteção de duplicados
   - O progresso será mostrado na barra de estado
   - Cancele a verificação a qualquer momento com «Cancelar»

## Trabalhar com os resultados

- **Visualize os ficheiros** selecionando-os na lista
  - Veja imagens e conteúdo de texto
  - Navegue entre as páginas com os botões de seta

- **Gerencie duplicados**
  - Selecione os ficheiros a manter ou eliminar
  - Utilize «Eliminar selecionados» para remover duplicados indesejados
  - «Desfazer eliminação» (Ctrl+Z) para restaurar ficheiros eliminados recentemente

## Funcionalidades

- **Modo de comparação rápida**
  - Ative o modo de comparação rápida para uma verificação mais rápida
  - Compara ficheiros apenas pelo tamanho (mais rápido, mas menos preciso)
  - Alterne através da caixa de seleção na janela principal ou em Configurações
  - Perfeito para digitalizações iniciais de grandes coleções

- **Suporte a vários idiomas**
  - Altere o idioma em Exibir > Idioma
  - Suporta inglês, italiano, espanhol, português, russo e árabe

- **Temas**
  - Alterne entre temas claros e escuros
  - A preferência de tema é salva entre as sessões

- **Atualizações automáticas**
  - Verifica automaticamente se há atualizações ao iniciar
  - Verificação manual em Ajuda > Verificar atualizações

## Dicas

- Use o modo Comparação rápida para varreduras iniciais de grandes coleções
- Para resultados mais precisos, execute uma varredura completa (com a Comparação rápida desativada) em ficheiros suspeitos
- Use atalhos de teclado para uma navegação mais rápida
- Verifique a barra de status para ver o progresso e as mensagens
- Relate quaisquer problemas no nosso repositório GitHub

## Como procurar duplicados

1. Selecione uma pasta que contenha ficheiros PDF
2. Escolha entre Comparação rápida (mais rápida) ou comparação completa (mais precisa)
3. Clique em «Encontrar duplicados» para iniciar o processo de verificação.
3. A aplicação analisará os PDFs e exibirá quaisquer duplicados encontrados.
4. Para cada conjunto de duplicatas:
   - Selecione um ficheiro na lista para visualizá-lo
   - Use o botão «Eliminar selecionados» para remover duplicatas indesejadas
   - Alterne entre «Visualização de imagem» e «Visualização de texto» para ver diferentes aspetos do PDF

Personalização:
- Alterne entre os temas Claro e Escuro no menu Ver > Tema
- Alterne entre vários idiomas no menu Ver > Idioma
- As preferências de tema e idioma são guardadas entre sessões
- Ajuste o tamanho da janela conforme necessário - a interface é responsiva

Dicas:
- O processo de digitalização pode demorar algum tempo para coleções grandes
- A comparação baseada em imagens é mais precisa, mas mais lenta
- A comparação baseada em texto é mais rápida, mas pode deixar passar duplicatas visuais
- Verifique sempre antes de eliminar quaisquer ficheiros
- Use a barra de rolagem horizontal para visualizar caminhos de ficheiros longos
- Aceda às pastas usadas recentemente no menu Ficheiro

Atalhos do teclado:
- Ctrl+O: Abrir pasta
- F5: Iniciar nova pesquisa
- F1: Mostrar esta ajuda
- Ctrl+Q: Sair da aplicação
- Delete: Remover ficheiros selecionados
- Esc: Fechar pré-visualização
- Ctrl+Z: Desfazer última eliminação
- Ctrl+1 a Ctrl+9: Abrir pasta recente

Para obter suporte adicional, contacte-nos através da secção «Sobre».""",

'ru': """# PDF Duplicate Finder — Руководство пользователя

## Начало работы

1. **Выберите папку**, содержащую PDF-файлы, которые необходимо проверить на наличие дубликатов.
   - Используйте кнопку «Обзор» или перетащите папку.
   - Недавние папки доступны в меню «Файл > Недавние папки».

2. **Проверьте наличие дубликатов**
   - Нажмите «Сканировать», чтобы начать процесс обнаружения дубликатов.
   - Прогресс будет отображаться в строке состояния.
   - Сканирование можно отменить в любой момент с помощью кнопки «Отмена».

## Работа с результатами

- **Просмотрите файлы**, выбрав их в списке.
  - Просматривайте как изображения, так и текстовое содержимое.
  - Перемещайтесь между страницами с помощью кнопок со стрелками.

- **Управляйте дубликатами**
  - Выберите файлы, которые нужно сохранить или удалить.
  - Используйте «Удалить выбранные», чтобы удалить ненужные дубликаты.
  - «Отменить удаление» (Ctrl+Z) для восстановления недавно удаленных файлов.

## Особенности

- **Режим быстрого сравнения**
  - Включите режим быстрого сравнения для более быстрого сканирования.
  - Сравнивает файлы только по размеру (быстрее, но менее точно).
  - Включение/выключение с помощью флажка в главном окне или в настройках
  - Идеально подходит для первоначального сканирования больших коллекций

- **Многоязычная поддержка**
  - Изменение языка в меню «Вид» > «Язык»
  - Поддержка английского, итальянского, испанского, португальского, русского и арабского языков

- **Темы**
  - Переключение между светлой и темной темами
  - Настройки темы сохраняются между сеансами

- **Автоматические обновления**
  - Автоматически проверяет наличие обновлений при запуске
  - Ручная проверка через «Справка» > «Проверить наличие обновлений»

## Советы

- Используйте режим «Быстрое сравнение» для первоначального сканирования больших коллекций
- Для получения более точных результатов запустите полное сканирование (с отключенным «Быстрым сравнением») подозрительных файлов
- Используйте горячие клавиши для более быстрой навигации
- Проверяйте статусную строку для прогресса и сообщений
- Сообщайте о любых проблемах в нашем репозитории GitHub

## Как сканировать дубликаты

1. Выберите папку, содержащую PDF-файлы
2. Выберите между быстрым сравнением (быстрее) или полным сравнением (более точно)
3. Нажмите «Найти дубликаты», чтобы начать процесс сканирования.
3. Приложение проанализирует PDF-файлы и отобразит все найденные дубликаты.
4. Для каждого набора дубликатов:
   - Выберите файл в списке, чтобы просмотреть его
   - Используйте кнопку «Удалить выбранные», чтобы удалить ненужные дубликаты
   - Переключайтесь между «Предварительным просмотром изображения» и «Предварительным просмотром текста», чтобы просматривать разные аспекты PDF-файла

Настройка:
- Переключайтесь между светлой и темной темами в меню «Вид» > «Тема»
- Переключайтесь между несколькими языками в меню «Вид» > «Язык»
- Настройки темы и языка сохраняются между сеансами.
- Настройте размер окна по необходимости — интерфейс адаптивный.

Советы:
- Процесс сканирования может занять некоторое время для больших коллекций.
- Сравнение на основе изображений более точное, но более медленное.
- Сравнение на основе текста быстрее, но может пропустить визуальные дубликаты.
- Всегда проверяйте перед удалением файлов.
- Используйте горизонтальную полосу прокрутки для просмотра длинных путей к файлам.
- Доступ к недавно использованным папкам из меню «Файл».

Сочетания клавиш:
- Ctrl+O: открыть папку
- F5: начать новый поиск
- F1: показать эту справку
- Ctrl+Q: выйти из приложения
- Delete: удалить выбранные файлы
- Esc: закрыть предварительный просмотр
- Ctrl+Z: отменить последнее удаление
- Ctrl+1 до Ctrl+9: открыть недавнюю папку

Для получения дополнительной поддержки свяжитесь с нами через раздел «О программе».""",
'ar': """# PDF Duplicate Finder - دليل المستخدم

## البدء

1. **حدد مجلدًا** يحتوي على ملفات PDF لفحصها بحثًا عن التكرارات.
   - استخدم زر ”تصفح“ أو اسحب المجلد وأفلته
   - المجلدات الحديثة متاحة ضمن ”ملف > المجلدات الحديثة“

2. **فحص التكرارات**
   - انقر فوق ”فحص“ لبدء عملية الكشف عن التكرارات
   - سيتم عرض التقدم في شريط الحالة
   - قم بإلغاء الفحص في أي وقت باستخدام ”إلغاء“

## التعامل مع النتائج

- **معاينة الملفات** عن طريق تحديدها في القائمة
  - عرض كل من الصور ومحتوى النص
  - التنقل بين الصفحات باستخدام أزرار الأسهم

- **إدارة التكرارات**
  - حدد الملفات التي تريد الاحتفاظ بها أو حذفها
  - استخدم ”حذف المحدد“ لإزالة التكرارات غير المرغوب فيها
  - ”تراجع عن الحذف“ (Ctrl+Z) لاستعادة الملفات المحذوفة مؤخرًا

## الميزات

- **وضع المقارنة السريعة**
  - قم بتبديل وضع المقارنة السريعة لمسح أسرع
  - يقارن الملفات حسب الحجم فقط (أسرع ولكن أقل دقة)
  - قم بالتبديل عبر مربع الاختيار في النافذة الرئيسية أو في الإعدادات
  - مثالي للمسح الأولي للمجموعات الكبيرة

- **دعم متعدد اللغات**
  - قم بتغيير اللغة من عرض > اللغة
  - يدعم الإنجليزية والإيطالية والإسبانية والبرتغالية والروسية والعربية

- **السمات**
  - قم بالتبديل بين السمات الفاتحة والداكنة
  - يتم حفظ تفضيلات السمة بين الجلسات

- **التحديثات التلقائية**
  - يتحقق تلقائيًا من وجود تحديثات عند بدء التشغيل
  - التحقق اليدوي عبر المساعدة > التحقق من وجود تحديثات

## نصائح

- استخدم وضع المقارنة السريعة للمسح الأولي للمجموعات الكبيرة
- للحصول على نتائج أكثر دقة، قم بإجراء مسح كامل (مع إيقاف تشغيل المقارنة السريعة) على الملفات المشبوهة
- استخدم اختصارات لوحة المفاتيح للتنقل بشكل أسرع
- تحقق من شريط الحالة لمعرفة التقدم والرسائل
- أبلغ عن أي مشكلات على مستودع GitHub الخاص بنا

## كيفية البحث عن التكرارات

1. حدد مجلدًا يحتوي على ملفات PDF
2. اختر بين المقارنة السريعة (أسرع) أو المقارنة الكاملة (أكثر دقة)
3. انقر فوق ”البحث عن التكرارات“ لبدء عملية الفحص.
3. سيقوم التطبيق بتحليل ملفات PDF وعرض أي تكرارات تم العثور عليها.
4. لكل مجموعة من التكرارات:
   - حدد ملفًا في القائمة لمعاينته
   - استخدم الزر ”حذف المحدد“ لإزالة التكرارات غير المرغوب فيها
   - قم بالتبديل بين ”معاينة الصورة“ و”معاينة النص“ لعرض جوانب مختلفة من ملف PDF

التخصيص:
- قم بالتبديل بين السمات الفاتحة والداكنة من قائمة عرض > سمة
- قم بالتبديل بين لغات متعددة من قائمة عرض > لغة
- يتم حفظ تفضيلات السمة واللغة بين الجلسات
- اضبط حجم النافذة حسب الحاجة - الواجهة سريعة الاستجابة

نصائح:
- قد تستغرق عملية المسح بعض الوقت للمجموعات الكبيرة
- المقارنة القائمة على الصور أكثر دقة ولكنها أبطأ
- المقارنة القائمة على النص أسرع ولكنها قد تفوت التكرارات المرئية
- تحقق دائمًا قبل حذف أي ملفات
- استخدم شريط التمرير الأفقي لعرض مسارات الملفات الطويلة
- قم بالوصول إلى المجلدات المستخدمة مؤخرًا من قائمة ”ملف“

اختصارات لوحة المفاتيح:
- Ctrl+O: فتح مجلد
- F5: بدء بحث جديد
- F1: عرض هذه المساعدة
- Ctrl+Q: إنهاء التطبيق
- حذف: إزالة الملفات المحددة
- Esc: إغلاق المعاينة
- Ctrl+Z: التراجع عن آخر حذف
- Ctrl+1 إلى Ctrl+9: فتح المجلد الأخير

للحصول على دعم إضافي، يرجى الاتصال بنا من خلال قسم ”حول“.""",
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
