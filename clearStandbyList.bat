@echo off
rem 设置 RAMMap 的路径
set RAMMAP_PATH="E:\RAMMap\RAMMap64.exe"

rem 检查 RAMMap 是否存在
if exist %RAMMAP_PATH% (
    rem 清空 Standby List
    %RAMMAP_PATH% -Et
    echo Standby List Cleared Successfully.
) else (
    echo RAMMap.exe 路径无效或文件不存在。
)


timeout /t 5
