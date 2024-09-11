@echo off
setlocal enabledelayedexpansion

REM settings
set EXE_NAME1=dj_main.exe
set EXE_PATH1="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\dj_main.exe.lnk"

set EXE_NAME2=wt_main.exe
set EXE_PATH2="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\wt_main.exe.lnk"

set EXE_NAME3=push_main.exe
set EXE_PATH3="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\push_main.exe.lnk"

set EXE_NAME4=qjcs_main.exe
set EXE_PATH4="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\qjcs_main.exe.lnk"

set EXE_NAME5=xstx_main.exe
set EXE_PATH5="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\xstx_main.exe.lnk"

set EXE_NAME6=jlcxx_main.exe
set EXE_PATH6="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\jlcxx_main.exe.lnk"

set EXE_NAME7=checkStatus.exe
set EXE_PATH7="C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\checkStatus.exe.lnk"


REM init
set "PROCESS_FOUND1=false"
set "PROCESS_FOUND2=false"
set "PROCESS_FOUND3=false"
set "PROCESS_FOUND4=false"
set "PROCESS_FOUND5=false"
set "PROCESS_FOUND6=false"
set "PROCESS_FOUND7=false"

REM check1
for /f "tokens=1,* delims= " %%a in ('tasklist /FI "IMAGENAME eq %EXE_NAME1%" ^| findstr /I "dj_main"') do (
    echo DEBUG: %%a
    if "%%a"=="%EXE_NAME1%" set "PROCESS_FOUND1=true"
)

REM check2
for /f "tokens=1,* delims= " %%b in ('tasklist /FI "IMAGENAME eq %EXE_NAME2%" ^| findstr /I "wt_main"') do (
    echo DEBUG: %%b
    if "%%b"=="%EXE_NAME2%" set "PROCESS_FOUND2=true"
)

REM check3
for /f "tokens=1,* delims= " %%c in ('tasklist /FI "IMAGENAME eq %EXE_NAME3%" ^| findstr /I "push_main"') do (
    echo DEBUG: %%c
    if "%%c"=="%EXE_NAME3%" set "PROCESS_FOUND3=true"
)

REM check4
for /f "tokens=1,* delims= " %%d in ('tasklist /FI "IMAGENAME eq %EXE_NAME4%" ^| findstr /I "qjcs_main"') do (
    echo DEBUG: %%d
    if "%%d"=="%EXE_NAME4%" set "PROCESS_FOUND4=true"
)

REM check5
for /f "tokens=1,* delims= " %%d in ('tasklist /FI "IMAGENAME eq %EXE_NAME5%" ^| findstr /I "xstx_main"') do (
    echo DEBUG: %%d
    if "%%d"=="%EXE_NAME5%" set "PROCESS_FOUND5=true"
)

REM check6
for /f "tokens=1,* delims= " %%d in ('tasklist /FI "IMAGENAME eq %EXE_NAME6%" ^| findstr /I "jlcxx_main"') do (
    echo DEBUG: %%d
    if "%%d"=="%EXE_NAME6%" set "PROCESS_FOUND6=true"
)

REM check7
for /f "tokens=1,* delims= " %%d in ('tasklist /FI "IMAGENAME eq %EXE_NAME7%" ^| findstr /I "checkStatus"') do (
    echo DEBUG: %%d
    if "%%d"=="%EXE_NAME7%" set "PROCESS_FOUND7=true"
)


REM print
echo PROCESS_FOUND1=!PROCESS_FOUND1!
echo PROCESS_FOUND2=!PROCESS_FOUND2!
echo PROCESS_FOUND3=!PROCESS_FOUND3!
echo PROCESS_FOUND4=!PROCESS_FOUND4!
echo PROCESS_FOUND5=!PROCESS_FOUND5!
echo PROCESS_FOUND6=!PROCESS_FOUND6!
echo PROCESS_FOUND7=!PROCESS_FOUND7!

timeout /t 2

REM if starting -> close
if "!PROCESS_FOUND1!"=="true" (
    echo %EXE_NAME1% is running, terminating...
    taskkill /F /IM %EXE_NAME1%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND2!"=="true" (
    echo %EXE_NAME2% is running, terminating...
    taskkill /F /IM %EXE_NAME2%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND3!"=="true" (
    echo %EXE_NAME3% is running, terminating...
    taskkill /F /IM %EXE_NAME3%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND4!"=="true" (
    echo %EXE_NAME4% is running, terminating...
    taskkill /F /IM %EXE_NAME4%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND5!"=="true" (
    echo %EXE_NAME5% is running, terminating...
    taskkill /F /IM %EXE_NAME5%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND6!"=="true" (
    echo %EXE_NAME6% is running, terminating...
    taskkill /F /IM %EXE_NAME6%
    timeout /t 1 /nobreak
)

if "!PROCESS_FOUND7!"=="true" (
    echo %EXE_NAME7% is running, terminating...
    taskkill /F /IM %EXE_NAME7%
    timeout /t 1 /nobreak
)

REM start
echo Starting %EXE_NAME1%...
start "" %EXE_PATH1%

echo Starting %EXE_NAME2%...
start "" %EXE_PATH2%

echo Starting %EXE_NAME3%...
start "" %EXE_PATH3%

echo Starting %EXE_NAME4%...
start "" %EXE_PATH4%

echo Starting %EXE_NAME5%...
start "" %EXE_PATH5%

echo Starting %EXE_NAME6%...
start "" %EXE_PATH6%

echo Starting %EXE_NAME7%...
start "" %EXE_PATH7%


timeout /t 5

endlocal