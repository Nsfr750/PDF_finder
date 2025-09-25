"""
Japanese translations for PDF Duplicate Finder.
"""

# Translation data
TRANSLATIONS = {
    "ja": {
        # Main window
        "main_window.title": "PDF重複ファイルファインダー",
        "main_window.file": "ファイル",
        "main_window.edit": "編集",
        "main_window.view": "表示",
        "main_window.help": "ヘルプ",
        "main_window.settings": "設定",
        "main_window.exit": "終了",
        
        # Status bar
        "ui.status_ready": "準備完了",
        
        # Common
        "common.ok": "OK",
        "common.cancel": "キャンセル",
        "common.yes": "はい",
        "common.no": "いいえ",
        "common.close": "閉じる",
        "common.save": "保存",
        "common.apply": "適用",
        "common.open": "開く",
        "common.delete": "削除",
        "common.edit": "編集",
        "common.help": "ヘルプ",
        "common.about": "について",
        "common.preferences": "設定",
        "common.exit": "終了",
        "common.none": "なし",
        
        # Settings dialog
        "settings.title": "設定",
        "settings.general": "一般",
        "settings.appearance": "外観",
        "settings.language": "言語",
        "settings.save": "保存",
        "settings.cancel": "キャンセル",
        "settings.theme_system": "システム",
        "settings.theme_light": "ライト",
        "settings.theme_dark": "ダーク",
        "settings.check_updates": "起動時に更新を確認",
        "settings.auto_save": "設定を自動保存",
        "settings.pdf_rendering": "PDFレンダリング",
        
        # Menu items
        "file.open": "フォルダを開く...",
        "file.save_results": "結果を保存...",
        "file.load_results": "結果を読み込む...",
        "file.settings": "設定...",
        "file.exit": "終了",
        "edit.delete": "削除",
        "edit.select_all": "すべて選択",
        "view.view_log": "ログを表示...",
        "view.toolbar": "ツールバー",
        "view.statusbar": "ステータスバー",
        "help.about": "について",
        "help.sponsor": "支援",
        "help.check_updates": "更新を確認",
        
        # Toolbar tooltips
        "toolbar.open_folder": "スキャンするフォルダを開く",
        "toolbar.start_scan": "重複ファイルのスキャンを開始",
        "toolbar.stop_scan": "スキャンを停止",
        "toolbar.save_results": "スキャン結果を保存",
        "toolbar.load_results": "スキャン結果を読み込む",
        "toolbar.delete_selected": "選択したファイルを削除",
        "toolbar.delete_all": "すべての重複ファイルを削除",
        "toolbar.view_log": "ログを表示",
        "toolbar.settings": "設定",
        "toolbar.about": "について",
        
        # Progress dialog
        "progress.title": "PDFスキャン",
        "progress.scanning": "スキャン中...",
        "progress.files_processed": "処理済みファイル:",
        "progress.current_file": "現在のファイル:",
        "progress.duplicates_found": "見つかった重複:",
        "progress.cancel": "キャンセル",
        
        # Filter dialog
        "filter.title": "結果をフィルター",
        "filter.min_size": "最小サイズ (KB):",
        "filter.max_size": "最大サイズ (KB):",
        "filter.min_pages": "最小ページ数:",
        "filter.max_pages": "最大ページ数:",
        "filter.name_contains": "名前に含まれる:",
        "filter.apply": "適用",
        "filter.reset": "リセット",
        "filter.cancel": "キャンセル",
        
        # Settings dialog
        "settings_dialog.title": "設定",
        "settings_dialog.general_tab": "一般",
        "settings_dialog.appearance_tab": "外観",
        "settings_dialog.language_label": "言語:",
        "settings_dialog.theme_label": "テーマ:",
        "settings_dialog.check_updates": "起動時に更新を確認",
        "settings_dialog.auto_save": "設定を自動保存",
        "settings_dialog.pdf_backend": "PDFバックエンド:",
        "settings_dialog.test_backend": "バックエンドをテスト",
        "settings_dialog.save": "保存",
        "settings_dialog.cancel": "キャンセル",
        "settings_dialog.restart_required": "再起動が必要",
        "settings_dialog.restart_message": "言語の変更を適用するにはアプリケーションを再起動する必要があります。\n今すぐ再起動しますか？",
        "settings_dialog.language_changed": "言語が正常に変更されました",
        "settings_dialog.language_change_failed": "言語の変更に失敗しました",
        "settings_dialog.backend_ok": "OK",
        "settings_dialog.backend_missing": "存在しないか無効なパス",
        "settings_dialog.no_backends_tested": "テストされたバックエンドはありません",
        "settings_dialog.test_results_title": "バックエンドテスト結果",
        "settings_dialog.backend_status": "バックエンドの状態:",
        "settings_dialog.test_backends": "バックエンドをテスト",
        
        # Main application
        "main.welcome": "PDF重複ファイルファインダーへようこそ",
        "main.select_folder": "PDFファイルをスキャンするフォルダを選択してください",
        "main.scan_started": "スキャンを開始しました",
        "main.scan_completed": "スキャンが完了しました",
        "main.duplicates_found": "重複が見つかりました: {count}",
        "main.no_duplicates": "重複は見つかりませんでした",
        "main.files_deleted": "{count}個のファイルが正常に削除されました。",
        "main.confirm_delete": "選択した{count}個のファイルを削除してもよろしいですか？",
        "main.confirm_delete_title": "削除の確認",
        "main.file_in_use": "ファイルは使用中のため削除できません: {file}",
        "main.permission_denied": "削除時に権限が拒否されました: {file}",
        "main.group_processed": "グループ {current}/{total} を処理済み: {found}個の重複が見つかりました",
        "main.retranslate_error": "再翻訳コールバックエラー: {error}",
        "main.scanning_folder": "フォルダをスキャン中: {folder}",
        "main.no_pdfs_found": "選択したフォルダにPDFファイルが見つかりませんでした。",
        "main.duplicates_found_groups": "{count}個の潜在的な重複グループが見つかりました。",
        
        # Scanner
        "scanner.starting": "スキャンを開始中...",
        "scanner.scanning": "スキャン中...",
        "scanner.processing_file": "ファイルを処理中: {file}",
        "scanner.comparing": "ファイルを比較中...",
        "scanner.found_duplicates": "重複が見つかりました: {count}",
        "scanner.complete": "スキャン完了。{count}個の重複グループが見つかりました",
        "scanner.stopped": "スキャンが停止しました",
        "scanner.processing": "処理中 {current}/{total}: {file}",
        "scanner.stopping": "スキャンを停止中...",
        "scan.complete": "スキャン完了",
        
        # PDF Viewer
        "pdf_viewer.title": "PDFビューア",
        "pdf_viewer.open": "PDFを開く",
        "pdf_viewer.previous": "前へ",
        "pdf_viewer.next": "次へ",
        "pdf_viewer.zoom_in": "拡大",
        "pdf_viewer.zoom_out": "縮小",
        "pdf_viewer.zoom_fit": "フィット",
        "pdf_viewer.zoom_100": "100%",
        "pdf_viewer.rotate_left": "左に回転",
        "pdf_viewer.rotate_right": "右に回転",
        "pdf_viewer.file_filter": "PDFファイル (*.pdf)",
        "pdf_viewer.status.page_of": "ページ {current}/{total} | {width} x {height} | {zoom:.0%}",
        "pdf_viewer.page_number": "ページ {current}/{total}",
        "pdf_viewer.errors.open_error": "PDFを開くエラー",
        "pdf_viewer.errors.could_not_open": "{file}を開けませんでした: {error}",
        
        # Language manager
        "language_manager.default_language_info": "デフォルト言語: {language} ({code})",
        "language_manager.language_switch_success": "{language}に正常に変更しました",
        "language_manager.language_switch_failed": "{language}への変更に失敗しました: {error}",
        
        # Sponsor dialog
        "sponsor.title": "開発を支援",
        "sponsor.message": "PDF重複ファイルファインダーは無料のオープンソースソフトウェアです。\n\nこのアプリが気に入ったら、開発の支援をご検討ください。",
        "sponsor.github_sponsors": "GitHubスポンサー",
        "sponsor.patreon": "Patreon",
        "sponsor.paypal": "PayPal",
        "sponsor.monero": "Monero (XMR)",
        "sponsor.close": "閉じる",
        
        # Updates
        "updates.window_title": "ソフトウェア更新",
        "updates.current_version": "現在のバージョン:",
        "updates.latest_version": "最新バージョン:",
        "updates.checking": "更新を確認中...",
        "updates.release_notes": "<b>リリースノート:</b>",
        "updates.update_available": "更新が利用可能です！",
        "updates.no_update_available": "最新バージョンをお使いです。",
        "updates.download_update": "更新をダウンロード",
        "updates.later": "後で",
        "updates.error_checking": "更新の確認エラー: {error}",
        
        # Log viewer
        "log_viewer.title": "ログを表示",
        "log_viewer.open": "ログを開く",
        "log_viewer.save": "ログを保存",
        "log_viewer.clear": "ログをクリア",
        "log_viewer.refresh": "更新",
        "log_viewer.filter": "フィルター",
        "log_viewer.status.line_count": "{count}行",
        "log_viewer.status.last_updated": "最終更新: {time}",
        "log_viewer.errors.save_error": "ログファイルの保存エラー: {error}",
        "log_viewer.save_error": "ログファイルを保存できませんでした: {error}",
        
        # Theme settings
        "theme.system": "システム",
        "theme.light": "ライト",
        "theme.dark": "ダーク",
        "theme.auto": "自動",
        
        # Additional UI elements
        "Open Folder": "フォルダを開く",
        "Start Scan": "スキャン開始",
        "Stop Scan": "スキャン停止",
        "Save Results": "結果を保存",
        "Load Results": "結果を読み込む",
        "Delete Selected": "選択を削除",
        "Delete All Duplicates": "すべての重複を削除",
        "View Log": "ログを表示",
        "Settings": "設定",
        "About": "について",
        "Exit": "終了",
        
        # Dialogs
        "Select Folder": "フォルダを選択",
        "Save Results": "結果を保存",
        "Load Results": "結果を読み込む",
        "Confirm Delete": "削除の確認",
        "Are you sure you want to delete the selected files?": "選択したファイルを削除してもよろしいですか？",
        "Error": "エラー",
        "Information": "情報",
        "Warning": "警告",
        "Success": "成功",
        
        # File operations
        "File": "ファイル",
        "Edit": "編集",
        "View": "表示",
        "Help": "ヘルプ",
        "Select All": "すべて選択",
        "Open PDF Viewer": "PDFビューアを開く",
        "Export Results to CSV": "結果をCSVにエクスポート",
        "Export last scan results to a CSV file": "最後のスキャン結果をCSVファイルにエクスポート",
        "Exit": "終了",
        "Exit the application": "アプリケーションを終了",
        
        # Progress dialog translations
        "Files processed:": "処理済みファイル:",
        "Current file:": "現在のファイル:",
        "Duplicates found:": "見つかった重複:",
        
        # Log viewer translations
        "Failed to list log files: {}": "ログファイルの一覧表示に失敗しました: {}",
        "Log file not found: {path}": "ログファイルが見つかりません: {path}",
        "Failed to load log file: {}": "ログファイルの読み込みに失敗しました: {}",
        "No log file selected": "ログファイルが選択されていません",
        "File: {file} | Entries: {entries} | Size: {size}": "ファイル: {file} | エントリ: {entries} | サイズ: {size}",
        "Confirm Delete": "削除の確認",
        "Are you sure you want to delete the log file?\nThis will permanently delete: {}\nThis action cannot be undone.": "ログファイルを削除してもよろしいですか？\nこれは永久に削除されます: {}\nこの操作は元に戻せません。",
        "Success": "成功",
        "Log file has been deleted.": "ログファイルが削除されました。",
        "Failed to delete log file: {}": "ログファイルの削除に失敗しました: {}",
        "Showing {filtered} of {total} entries": "{total}件中{filtered}件を表示",
        "Failed to filter logs: {}": "ログのフィルタリングに失敗しました: {}",
        "Confirm Clear": "クリアの確認",
        "Are you sure you want to clear all logs? This cannot be undone.": "すべてのログをクリアしてもよろしいですか？これは元に戻せません。",
        "Failed to clear logs: {error}": "ログのクリアに失敗しました: {error}",
        "Error": "エラー",
        
        # Toolbar translation keys (added to fix toolbar translation issues)
        "Cache Manager": "キャッシュマネージャー",
        "Manage PDF hash cache settings and operations": "PDFハッシュキャッシュの設定と操作を管理",
        "Refresh Language": "言語を更新"
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
