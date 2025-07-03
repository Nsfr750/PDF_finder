@ECHO OFF
@REM PDF Finder 
@x:
@cd "x:/GitHub/PDF_Finder"
@ECHO
@python -m nuitka ^
--onefile ^
--output-dir=x:/GitHub/PDF_Finder ^
--output-filename=PDF-Finder.exe ^
--windows-icon-from-ico=x:/GitHub/PDF_Finder/images/icon.ico ^
--plugin-enable=pyside6 ^
--follow-imports ^
--show-progress ^
--windows-company-name=Tuxxle ^
--copyright="(c)2025 by Nsfr750" ^
--windows-product-name=PDF-Finder.exe ^
--windows-product-version=2.7.0 ^
--windows-file-version=2.7.0 ^
x:/GitHub/PDF_Finder/main.py
@pause
