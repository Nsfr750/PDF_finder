@ECHO OFF
@ECHO ~ PDF Finder ~
@x:
@cd "x:/GitHub/PDF_Finder"
@python -m nuitka ^
--onefile ^
--output-dir=X:/Installazioni ^
--output-filename=PDF-Finder.exe ^
--windows-icon-from-ico=x:/GitHub/PDF_Finder/images/icon.ico ^
--plugin-enable=pyside6 ^
--follow-imports ^
--show-progress ^
--windows-company-name=Tuxxle ^
--copyright="(c)2025 by Nsfr750" ^
--windows-product-name="PDF Finder" ^
--windows-product-version=2.7.1 ^
--windows-file-version=2.7.1 ^
--mingw64 ^
x:/GitHub/PDF_Finder/main.py
@pause
