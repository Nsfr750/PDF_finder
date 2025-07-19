; PDF_Finder Uninstaller
; NSIS script for creating an uninstaller

;--------------------------------
; Include Modern UI
!include "MUI2.nsh"

;--------------------------------
; General

; Name and file
Name "PDF_Finder"
OutFile "PDF_Finder_Uninstall.exe"

; Default installation folder
!define INSTDIR "$PROGRAMFILES64\PDF_Finder"
InstallDir "${INSTDIR}"

; Request application privileges for Windows Vista and later
RequestExecutionLevel admin

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Remove files and directories
  RMDir /r "$INSTDIR"
  
  ; Remove start menu shortcuts
  Delete "$SMPROGRAMS\PDF_Finder\PDF_Finder.lnk"
  Delete "$SMPROGRAMS\PDF_Finder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\PDF_Finder"
  
  ; Remove desktop shortcut
  Delete "$DESKTOP\PDF_Finder.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\PDF_Finder"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PDF_Finder"
  
  ; Remove file associations if they exist
  ; Example: .pdf files
  ; DeleteRegKey HKCR ".pdf\OpenWithProgids\PDF_Finder"
  ; DeleteRegValue HKCR "Applications\PDF_Finder.exe" ""
  
  ; Remove environment variables if any
  ; Delete "$INSTDIR" from PATH
  ; Push "$INSTDIR"
  ; Call un.RemoveFromPath

SectionEnd

;--------------------------------
; Functions

; Function to remove from PATH
; Function un.RemoveFromPath
;   Exch $0
;   Push $1
;   Push $2
;   Push $3
;   Push $4
;   
;   ReadRegStr $1 HKCU "Environment" "PATH"
;   StrCpy $2 $1 1 -1
;   StrCmp $2 ";" 0 +2
;     StrCpy $1 $1 -1
;   Push $1
;   Push ";"
;   Push $0
;   Call un.StrStr
;   Pop $2
;   StrCmp $2 "" unremoveFromPath_done
;   
;   StrLen $3 $0
;   StrLen $4 $2
;   StrCpy $1 $1 -$4
;   StrCpy $1 $1$3
;   StrCmp $1 $0 0 unremoveFromPath_done
;     StrCpy $1 $2 $3
;     StrCmp $1 $0 0 unremoveFromPath_done
;       StrCpy $1 $2 "" $3
;       StrCpy $0 $2 $3
;       StrCmp $1 "" 0 +3
;         StrCpy $2 ""
;         Goto +2
;       StrCpy $2 "$1$2"
;       
;       WriteRegExpandStr HKCU "Environment" "PATH" "$2"
;       SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
;       
;   unremoveFromPath_done:
;     Pop $4
;     Pop $3
;     Pop $2
;     Pop $1
;     Pop $0
; FunctionEnd

; Function to find a string in another string
; Function un.StrStr
;   Exch $R1 ; st=haystack,old$R1, stk=needle
;   Exch    ; st=old$R1,haystack, stk=needle
;   Exch $R2 ; st=old$R1,needle, stk=haystack
;   Push $R3
;   Push $R4
;   Push $R5
;   StrLen $R3 $R1
;   StrCpy $R4 0
;   ; $R1=needle
;   ; $R2=haystack
;   ; $R3=len(needle)
;   ; $R4=cnt
;   ; $R5=tmp
;   loop:
;     StrCpy $R5 $R2 $R3 $R4
;     StrCmp $R5 $R1 done
;     StrCmp $R5 "" done
;     IntOp $R4 $R4 + 1
;     Goto loop
;   done:
;   StrCpy $R1 $R2 "" $R4
;   Pop $R5
;   Pop $R4
;   Pop $R3
;   Pop $R2
;   Exch $R1
; FunctionEnd
