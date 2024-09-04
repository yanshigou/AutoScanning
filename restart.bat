@echo off
setlocal enabledelayedexpansion

REM 设置要检测的进程和路径
set EXE_NAME1=dj_main.exe
set EXE_PATH1="E:\dj_main_v2.7_20240807.exe.lnk"

set EXE_NAME2=wt_main.exe
set EXE_PATH2="E:\wt_main_v2.4_20240807.exe.lnk"

set EXE_NAME3=push_main.exe
set EXE_PATH3="E:\push_main_v2.4_20240807.exe.lnk"

set EXE_NAME4=checkStatus.exe
set EXE_PATH4="E:\checkStatus_v2.5_20240807.exe.lnk"

REM 初始化标志变量
set "PROCESS_FOUND1=false"
set "PROCESS_FOUND2=false"
set "PROCESS_FOUND3=false"
set "PROCESS_FOUND4=false"

REM 检查第一个进程是否在运行
for /f "tokens=1,* delims= " %%a in ('tasklist /FI "IMAGENAME eq %EXE_NAME1%" ^| findstr /I "dj_main"') do (
    echo DEBUG: %%a
    if "%%a"=="%EXE_NAME1%" set "PROCESS_FOUND1=true"
)

REM 检查第二个进程是否在运行
for /f "tokens=1,* delims= " %%b in ('tasklist /FI "IMAGENAME eq %EXE_NAME2%" ^| findstr /I "wt_main"') do (
    echo DEBUG: %%b
    if "%%b"=="%EXE_NAME2%" set "PROCESS_FOUND2=true"
)

REM 检查第三个进程是否在运行
for /f "tokens=1,* delims= " %%c in ('tasklist /FI "IMAGENAME eq %EXE_NAME3%" ^| findstr /I "push_main"') do (
    echo DEBUG: %%c
    if "%%c"=="%EXE_NAME3%" set "PROCESS_FOUND3=true"
)

REM 检查第四个进程是否在运行
for /f "tokens=1,* delims= " %%d in ('tasklist /FI "IMAGENAME eq %EXE_NAME4%" ^| findstr /I "checkStatus"') do (
    echo DEBUG: %%d
    if "%%d"=="%EXE_NAME4%" set "PROCESS_FOUND4=true"
)

REM 打印进程状态
echo PROCESS_FOUND1=!PROCESS_FOUND1!
echo PROCESS_FOUND2=!PROCESS_FOUND2!
echo PROCESS_FOUND3=!PROCESS_FOUND3!
echo PROCESS_FOUND4=!PROCESS_FOUND4!

timeout /t 2

REM 如果进程正在运行，则结束进程
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

REM 启动应用程序
echo Starting %EXE_NAME1%...
start "" %EXE_PATH1%

echo Starting %EXE_NAME2%...
start "" %EXE_PATH2%

echo Starting %EXE_NAME3%...
start "" %EXE_PATH3%

echo Starting %EXE_NAME4%...
start "" %EXE_PATH4%

timeout /t 5

endlocal