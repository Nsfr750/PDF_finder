; NSIS Installer Script for PDF_Finder ${VERSION}
; Auto-generated with enhanced features for PDF management

; Include Modern UI and other required libraries
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "WordFunc.nsh"
!include "WinVer.nsh"
!include "nsDialogs.nsh"
!include "Sections.nsh"

; --------------------------------
; Version Information
; --------------------------------
!define MAJOR_VERSION "2"
!define MINOR_VERSION "7"
!define PATCH_VERSION "3"
!define BUILD_NUMBER "0"
!define RELEASE_YEAR "2025"
!define VERSION "${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}.${BUILD_NUMBER}"
!define APPNAME "PDF_Finder"
!define PUBLISHER "Nsfr750"
!define COMPANY "Nsfr750"
!define WEBSITE "https://github.com/Nsfr750/PDF_Finder"
!define UPDATE_URL "${WEBSITE}/releases/latest"
!define HELP_URL "${WEBSITE}/wiki"
!define SUPPORT_EMAIL "nsfr750@yandex.com"

; --------------------------------
; Installer Attributes
; --------------------------------
Name "${APPNAME}"

; Create output directory if it doesn't exist
!ifdef OUTDIR
  !system 'if not exist "${OUTDIR}" mkdir "${OUTDIR}"'
!endif

OutFile "dist\${APPNAME}-v${VERSION}-Setup.exe"

; Ensure the dist directory exists
!system 'if not exist "dist" mkdir "dist"'
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show
BrandingText "${APPNAME} v${VERSION}"

; --------------------------------
; Version Info for the installer
; --------------------------------
VIProductVersion "${VERSION}"
VIAddVersionKey "ProductName" "${APPNAME}"
VIAddVersionKey "CompanyName" "${COMPANY}"
VIAddVersionKey "LegalCopyright" "© 2023 ${PUBLISHER}"
VIAddVersionKey "FileDescription" "${APPNAME} Installer"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "ProductVersion" "${VERSION}"

; --------------------------------
; Interface Settings
; --------------------------------
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Header\orange.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "${NSISDIR}\Contrib\Graphics\Header\orange-uninstall.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange.bmp"
!define MUI_WELCOMEFINISHPAGE_UNBITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange-uninstall"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\orange.bmp"
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_UNFINISHPAGE_NOAUTOCLOSE

; --------------------------------
; Pages
; --------------------------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

; Custom page to confirm installation
Page custom PageReinstall PageLeaveReinstall

; Include nsDialogs for custom pages
!include "nsDialogs.nsh"

; Variables are now defined at the top of the file with other variables

!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_RUN "$INSTDIR\${APPNAME}.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Run ${APPNAME} now"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchApplication"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View README"
!define MUI_FINISHPAGE_LINK "${WEBSITE}"
!define MUI_FINISHPAGE_LINK_LOCATION "${WEBSITE}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; --------------------------------
; Languages
; --------------------------------
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Italian"

; --------------------------------
; Variables
; --------------------------------
Var ReinstallUninstallString
Var CreateDesktopSC
Var AssocImages

; --------------------------------
; Installer Sections
; --------------------------------
Section "!${APPNAME}" SecMain
  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Add the main executable
  SetOutPath "$INSTDIR"
  File "..\\dist\\${APPNAME}.exe"
  
  ; Add required files
  SetOutPath "$INSTDIR"
  File "..\\README.md"
  File "..\\LICENSE"
  File "..\\CHANGELOG.md"
  File "..\\TO_DO.md"
  
  ; Add any additional files from the dist directory
  SetOutPath "$INSTDIR\\logs"
  File /nonfatal /r "..\\dist\\logs\\*.*"
  
  ; Create required directories
  CreateDirectory "$INSTDIR\assets"
  CreateDirectory "$INSTDIR\docs"
  CreateDirectory "$INSTDIR\locales"
  
  ; Copy assets and other resources if they exist
  IfFileExists "..\assets" 0 +3
    SetOutPath "$INSTDIR\assets"
    File /nonfatal /r "..\assets\*.*"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add uninstall information to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\${APPNAME}.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${WEBSITE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELP_URL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATE_URL}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
  
  ; Calculate and set installation size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
  
  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create desktop shortcut if selected
  ${If} $CreateDesktopSC == 1
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"
  ${EndIf}
  
  ; Write registry keys for Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "UninstallString" '"$INSTDIR\Uninstall.exe" /currentuser'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "DisplayIcon" "$INSTDIR\${APPNAME}.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "URLInfoAbout" "${WEBSITE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "HelpLink" "${HELP_URL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "URLUpdateInfo" "${UPDATE_URL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                   "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                   "NoRepair" 1
  
  ; Calculate installation size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                   "EstimatedSize" "$0"
  
  ; Create uninstaller for the current user
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "DisplayName" "${APPNAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                 "UninstallString" '"$INSTDIR\Uninstall.exe" /currentuser'
  
  ; Set file associations if selected
  ${If} $AssocImages == 1
    ; PDF Association
    WriteRegStr HKCR ".pdf\OpenWithProgids" "${APPNAME}.pdf" ""
    WriteRegStr HKCR "${APPNAME}.pdf" "" "PDF Document"
    WriteRegStr HKCR "${APPNAME}.pdf\DefaultIcon" "" "$INSTDIR\${APPNAME}.exe,0"
    WriteRegStr HKCR "${APPNAME}.pdf\shell\open\command" "" '"$INSTDIR\${APPNAME}.exe" "%1"'
    
    ; Optional: Make PDF_Finder the default PDF viewer
    ; Uncomment the following lines to set as default PDF viewer
    ; WriteRegStr HKCR ".pdf" "" "${APPNAME}.pdf"
    ; WriteRegStr HKCR "Applications\${APPNAME}.exe" "" ""
    ; WriteRegStr HKCR "Applications\${APPNAME}.exe\shell\open\command" "" '"$INSTDIR\${APPNAME}.exe" "%1"'
    
    ; Image associations
    WriteRegStr HKCR ".jpg\OpenWithProgids" "${APPNAME}.jpg" ""
    WriteRegStr HKCR "${APPNAME}.jpg" "" "${APPNAME} Image"
    WriteRegStr HKCR "${APPNAME}.jpg\DefaultIcon" "" "$INSTDIR\${APPNAME}.exe,0"
    WriteRegStr HKCR "${APPNAME}.jpg\shell\open\command" "" '"$INSTDIR\${APPNAME}.exe" "%1"'
    
    ; Other image formats
    WriteRegStr HKCR ".jpeg\OpenWithProgids" "${APPNAME}.jpeg" ""
    WriteRegStr HKCR ".png\OpenWithProgids" "${APPNAME}.png" ""
    WriteRegStr HKCR ".bmp\OpenWithProgids" "${APPNAME}.bmp" ""
    WriteRegStr HKCR ".gif\OpenWithProgids" "${APPNAME}.gif" ""
    WriteRegStr HKCR ".tiff\OpenWithProgids" "${APPNAME}.tiff" ""
    WriteRegStr HKCR ".tif\OpenWithProgids" "${APPNAME}.tif" ""
    WriteRegStr HKCR ".webp\OpenWithProgids" "${APPNAME}.webp" ""
    
    ; Refresh shell to apply changes
    System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
  ${EndIf}
  
  ; Register uninstaller with Windows
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
SectionEnd

; Optional section for desktop shortcut
Section /o "Desktop Shortcut" SecDesktopShortcut
  StrCpy $CreateDesktopSC 1
SectionEnd

; Optional section for file associations
Section /o "Associate Image Files" SecFileAssoc
  StrCpy $AssocImages 1
SectionEnd

; --------------------------------
; Custom Pages
; --------------------------------
Function PageReinstall
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
  StrCmp $R0 "" done
  
  StrCpy $ReinstallUninstallString $R0
  
  ; Simple message box for reinstallation prompt
  MessageBox MB_YESNO|MB_ICONQUESTION "${APPNAME} is already installed. Uninstall previous version?" IDYES uninstall_previous
  Abort
  
  uninstall_previous:
  StrCpy $0 "$ReinstallUninstallString"
  ExecWait '$0 /S _?=$INSTDIR'
  Delete "$0"
  RMDir "$INSTDIR"
  
  done:
FunctionEnd

Function PageLeaveReinstall
  ; No action needed here since we handle uninstallation in PageReinstall
  ; with a simple message box prompt
FunctionEnd

; --------------------------------
; Uninstaller Section
; --------------------------------
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\${APPNAME}.exe"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\CHANGELOG.md"
  
  ; Remove directories
  RMDir /r "$INSTDIR\assets"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME}.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  DeleteRegKey HKLM "Software\${APPNAME}"
  
  ; Remove file associations
  DeleteRegKey HKCR "${APPNAME}.jpg"
  DeleteRegKey HKCR "${APPNAME}.jpeg"
  DeleteRegKey HKCR "${APPNAME}.png"
  DeleteRegKey HKCR "${APPNAME}.bmp"
  DeleteRegKey HKCR "${APPNAME}.gif"
  DeleteRegKey HKCR "${APPNAME}.tiff"
  DeleteRegKey HKCR "${APPNAME}.tif"
  DeleteRegKey HKCR "${APPNAME}.webp"
  
  ; Refresh shell
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
  
SectionEnd

; --------------------------------
; Functions
; --------------------------------
Function .onInit
  ; Initialize variables
  StrCpy $CreateDesktopSC 0
  StrCpy $AssocImages 0
  
  ; Check for previous installation
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString"
  StrCmp $R0 "" done
  
  ; If previous installation found, show message
  MessageBox MB_YESNO|MB_ICONQUESTION "${APPNAME} is already installed. $\n$\nDo you want to uninstall the previous version before continuing with the installation?" IDYES uninst
  Abort
  
  uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'
    IfErrors no_remove_uninstaller
    Delete $R0
    RMDir $INSTDIR
    
  no_remove_uninstaller:
    IfErrors no_remove_folder
    RMDir /r $INSTDIR
    
  no_remove_folder:
  
  done:
FunctionEnd

Function LaunchApplication
  ExecShell "" "$INSTDIR\${APPNAME}.exe"
FunctionEnd

; --------------------------------
; Section Descriptions
; --------------------------------
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Core application files (required)."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopShortcut} "Create a desktop shortcut for easy access."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecFileAssoc} "Associate common image file types with ${APPNAME}."
!insertmacro MUI_FUNCTION_DESCRIPTION_END
