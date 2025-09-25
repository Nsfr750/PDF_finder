"""
Portuguese translations for PDF Duplicate Finder.
"""

# Translation data
TRANSLATIONS = {
    "pt": {
        # Main window
        "main_window.title": "PDF Duplicate Finder",
        "main_window.file": "Arquivo",
        "main_window.edit": "Editar",
        "main_window.view": "Exibir",
        "main_window.help": "Ajuda",
        "main_window.settings": "Configurações",
        "main_window.exit": "Sair",
        
        # Status bar
        "ui.status_ready": "Pronto",
        
        # Common
        "common.ok": "OK",
        "common.cancel": "Cancelar",
        "common.yes": "Sim",
        "common.no": "Não",
        "common.close": "Fechar",
        "common.save": "Salvar",
        "common.apply": "Aplicar",
        "common.open": "Abrir",
        "common.delete": "Excluir",
        "common.edit": "Editar",
        "common.help": "Ajuda",
        "common.about": "Sobre",
        "common.preferences": "Preferências",
        "common.exit": "Sair",
        "common.none": "Nenhum",
        
        # Settings dialog
        "settings.title": "Configurações",
        "settings.general": "Geral",
        "settings.appearance": "Aparência",
        "settings.language": "Idioma",
        "settings.save": "Salvar",
        "settings.cancel": "Cancelar",
        "settings.theme_system": "Sistema",
        "settings.theme_light": "Claro",
        "settings.theme_dark": "Escuro",
        "settings.check_updates": "Verificar atualizações ao iniciar",
        "settings.auto_save": "Salvar configurações automaticamente",
        "settings.pdf_rendering": "Renderização PDF",
        
        # Menu items
        "file.open": "Abrir pasta...",
        "file.save_results": "Salvar resultados...",
        "file.load_results": "Carregar resultados...",
        "file.settings": "Configurações...",
        "file.exit": "Sair",
        "edit.delete": "Excluir",
        "edit.select_all": "Selecionar tudo",
        "view.view_log": "Ver log...",
        "view.toolbar": "Barra de ferramentas",
        "view.statusbar": "Barra de status",
        "help.about": "Sobre",
        "help.sponsor": "Apoiar",
        "help.check_updates": "Verificar atualizações",
        
        # Toolbar tooltips
        "toolbar.open_folder": "Abrir pasta para escaneamento",
        "toolbar.start_scan": "Iniciar escaneamento de duplicatas",
        "toolbar.stop_scan": "Parar escaneamento",
        "toolbar.save_results": "Salvar resultados do escaneamento",
        "toolbar.load_results": "Carregar resultados do escaneamento",
        "toolbar.delete_selected": "Excluir arquivos selecionados",
        "toolbar.delete_all": "Excluir todas as duplicatas",
        "toolbar.view_log": "Ver log",
        "toolbar.settings": "Configurações",
        "toolbar.about": "Sobre",
        
        # Progress dialog
        "progress.title": "Escaneamento PDF",
        "progress.scanning": "Escaneando...",
        "progress.files_processed": "Arquivos processados:",
        "progress.current_file": "Arquivo atual:",
        "progress.duplicates_found": "Duplicatas encontradas:",
        "progress.cancel": "Cancelar",
        
        # Filter dialog
        "filter.title": "Filtrar resultados",
        "filter.min_size": "Tamanho mínimo (KB):",
        "filter.max_size": "Tamanho máximo (KB):",
        "filter.min_pages": "Número mínimo de páginas:",
        "filter.max_pages": "Número máximo de páginas:",
        "filter.name_contains": "Nome contém:",
        "filter.apply": "Aplicar",
        "filter.reset": "Redefinir",
        "filter.cancel": "Cancelar",
        
        # Settings dialog
        "settings_dialog.title": "Configurações",
        "settings_dialog.general_tab": "Geral",
        "settings_dialog.appearance_tab": "Aparência",
        "settings_dialog.language_label": "Idioma:",
        "settings_dialog.theme_label": "Tema:",
        "settings_dialog.check_updates": "Verificar atualizações ao iniciar",
        "settings_dialog.auto_save": "Salvar configurações automaticamente",
        "settings_dialog.pdf_backend": "Backend PDF:",
        "settings_dialog.test_backend": "Testar backend",
        "settings_dialog.save": "Salvar",
        "settings_dialog.cancel": "Cancelar",
        "settings_dialog.restart_required": "Reinicialização necessária",
        "settings_dialog.restart_message": "O aplicativo precisa ser reiniciado para aplicar as alterações de idioma.\nReiniciar agora?",
        "settings_dialog.language_changed": "Idioma alterado com sucesso",
        "settings_dialog.language_change_failed": "Falha ao alterar idioma",
        "settings_dialog.backend_ok": "OK",
        "settings_dialog.backend_missing": "Ausente ou caminho inválido",
        "settings_dialog.no_backends_tested": "Nenhum backend testado",
        "settings_dialog.test_results_title": "Resultados do teste de backends",
        "settings_dialog.backend_status": "Status do backend:",
        "settings_dialog.test_backends": "Testar backends",
        
        # Main application
        "main.welcome": "Bem-vindo ao PDF Duplicate Finder",
        "main.select_folder": "Selecione uma pasta para escanear arquivos PDF",
        "main.scan_started": "Escaneamento iniciado",
        "main.scan_completed": "Escaneamento concluído",
        "main.duplicates_found": "Duplicatas encontradas: {count}",
        "main.no_duplicates": "Nenhuma duplicata encontrada",
        "main.files_deleted": "{count} arquivos excluídos com sucesso.",
        "main.confirm_delete": "Tem certeza de que deseja excluir {count} arquivos selecionados?",
        "main.confirm_delete_title": "Confirmar exclusão",
        "main.file_in_use": "Arquivo está em uso e não pode ser excluído: {file}",
        "main.permission_denied": "Permissão negada ao tentar excluir: {file}",
        "main.group_processed": "Grupo {current}/{total} processado: {found} duplicatas encontradas",
        "main.retranslate_error": "Erro no callback retranslate: {error}",
        "main.scanning_folder": "Escaneando pasta: {folder}",
        "main.no_pdfs_found": "Nenhum arquivo PDF encontrado na pasta selecionada.",
        "main.duplicates_found_groups": "{count} grupos potenciais de duplicatas encontrados.",
        
        # Scanner
        "scanner.starting": "Iniciando escaneamento...",
        "scanner.scanning": "Escaneando...",
        "scanner.processing_file": "Processando arquivo: {file}",
        "scanner.comparing": "Comparando arquivos...",
        "scanner.found_duplicates": "Duplicatas encontradas: {count}",
        "scanner.complete": "Escaneamento concluído. {count} grupos de duplicatas encontrados",
        "scanner.stopped": "Escaneamento parado",
        "scanner.processing": "Processando {current} de {total}: {file}",
        "scanner.stopping": "Parando escaneamento...",
        "scan.complete": "Escaneamento concluído",
        
        # PDF Viewer
        "pdf_viewer.title": "Visualizador PDF",
        "pdf_viewer.open": "Abrir PDF",
        "pdf_viewer.previous": "Anterior",
        "pdf_viewer.next": "Próximo",
        "pdf_viewer.zoom_in": "Ampliar",
        "pdf_viewer.zoom_out": "Reduzir",
        "pdf_viewer.zoom_fit": "Ajustar",
        "pdf_viewer.zoom_100": "100%",
        "pdf_viewer.rotate_left": "Girar à esquerda",
        "pdf_viewer.rotate_right": "Girar à direita",
        "pdf_viewer.file_filter": "Arquivos PDF (*.pdf)",
        "pdf_viewer.status.page_of": "Página {current} de {total} | {width} x {height} | {zoom:.0%}",
        "pdf_viewer.page_number": "Página {current} de {total}",
        "pdf_viewer.errors.open_error": "Erro ao abrir PDF",
        "pdf_viewer.errors.could_not_open": "Não foi possível abrir {file}: {error}",
        
        # Language manager
        "language_manager.default_language_info": "Idioma padrão: {language} ({code})",
        "language_manager.language_switch_success": "Alterado para {language} com sucesso",
        "language_manager.language_switch_failed": "Falha ao alterar para {language}: {error}",
        
        # Sponsor dialog
        "sponsor.title": "Apoiar o desenvolvimento",
        "sponsor.message": "PDF Duplicate Finder é um software gratuito e de código aberto.\n\nSe você gosta deste aplicativo, por favor, considere apoiar seu desenvolvimento.",
        "sponsor.github_sponsors": "GitHub Sponsors",
        "sponsor.patreon": "Patreon",
        "sponsor.paypal": "PayPal",
        "sponsor.monero": "Monero (XMR)",
        "sponsor.close": "Fechar",
        
        # Updates
        "updates.window_title": "Atualização do software",
        "updates.current_version": "Versão atual:",
        "updates.latest_version": "Versão mais recente:",
        "updates.checking": "Verificando atualizações...",
        "updates.release_notes": "<b>Notas de lançamento:</b>",
        "updates.update_available": "Atualização disponível!",
        "updates.no_update_available": "Você tem a versão mais recente.",
        "updates.download_update": "Baixar atualização",
        "updates.later": "Mais tarde",
        "updates.error_checking": "Erro ao verificar atualizações: {error}",
        
        # Log viewer
        "log_viewer.title": "Ver log",
        "log_viewer.open": "Abrir log",
        "log_viewer.save": "Salvar log",
        "log_viewer.clear": "Limpar log",
        "log_viewer.refresh": "Atualizar",
        "log_viewer.filter": "Filtro",
        "log_viewer.status.line_count": "{count} linhas",
        "log_viewer.status.last_updated": "Última atualização: {time}",
        "log_viewer.errors.save_error": "Erro ao salvar arquivo de log: {error}",
        "log_viewer.save_error": "Não foi possível salvar arquivo de log: {error}",
        
        # Theme settings
        "theme.system": "Sistema",
        "theme.light": "Claro",
        "theme.dark": "Escuro",
        "theme.auto": "Automático",
        
        # Additional UI elements
        "Open Folder": "Abrir pasta",
        "Start Scan": "Iniciar escaneamento",
        "Stop Scan": "Parar escaneamento",
        "Save Results": "Salvar resultados",
        "Load Results": "Carregar resultados",
        "Delete Selected": "Excluir selecionados",
        "Delete All Duplicates": "Excluir todas as duplicatas",
        "View Log": "Ver log",
        "Settings": "Configurações",
        "About": "Sobre",
        "Exit": "Sair",
        
        # Dialogs
        "Select Folder": "Selecionar pasta",
        "Save Results": "Salvar resultados",
        "Load Results": "Carregar resultados",
        "Confirm Delete": "Confirmar exclusão",
        "Are you sure you want to delete the selected files?": "Tem certeza de que deseja excluir os arquivos selecionados?",
        "Error": "Erro",
        "Information": "Informação",
        "Warning": "Aviso",
        "Success": "Sucesso",
        
        # File operations
        "File": "Arquivo",
        "Edit": "Editar",
        "View": "Exibir",
        "Help": "Ajuda",
        "Select All": "Selecionar tudo",
        "Open PDF Viewer": "Abrir visualizador PDF",
        "Export Results to CSV": "Exportar resultados para CSV",
        "Export last scan results to a CSV file": "Exportar últimos resultados de escaneamento para um arquivo CSV",
        "Exit": "Sair",
        "Exit the application": "Sair do aplicativo",
        
        # Progress dialog translations
        "Files processed:": "Arquivos processados:",
        "Current file:": "Arquivo atual:",
        "Duplicates found:": "Duplicatas encontradas:",
        
        # Log viewer translations
        "Failed to list log files: {}": "Falha ao listar arquivos de log: {}",
        "Log file not found: {path}": "Arquivo de log não encontrado: {path}",
        "Failed to load log file: {}": "Falha ao carregar arquivo de log: {}",
        "No log file selected": "Nenhum arquivo de log selecionado",
        "File: {file} | Entries: {entries} | Size: {size}": "Arquivo: {file} | Entradas: {entries} | Tamanho: {size}",
        "Confirm Delete": "Confirmar exclusão",
        "Are you sure you want to delete the log file?\nThis will permanently delete: {}\nThis action cannot be undone.": "Tem certeza de que deseja excluir o arquivo de log?\nIsso excluirá permanentemente: {}\nEsta ação não pode ser desfeita.",
        "Success": "Sucesso",
        "Log file has been deleted.": "Arquivo de log foi excluído.",
        "Failed to delete log file: {}": "Falha ao excluir arquivo de log: {}",
        "Showing {filtered} of {total} entries": "Mostrando {filtered} de {total} entradas",
        "Failed to filter logs: {}": "Falha ao filtrar logs: {}",
        "Confirm Clear": "Confirmar limpeza",
        "Are you sure you want to clear all logs? This cannot be undone.": "Tem certeza de que deseja limpar todos os logs? Isso não pode ser desfeito.",
        "Failed to clear logs: {error}": "Falha ao limpar logs: {error}",
        "Error": "Erro",
        
        # Toolbar translation keys (added to fix toolbar translation issues)
        "Cache Manager": "Gerenciador de Cache",
        "Manage PDF hash cache settings and operations": "Gerenciar configurações e operações do cache de hash PDF",
        "Refresh Language": "Atualizar Idioma"
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
