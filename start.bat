@echo off
title Muse Studio - Control Center

echo ========================================================
echo         MUSE STUDIO - CREATIVE CONTROL CENTER
echo ========================================================
echo.

cd /d "%~dp0"

set "PY_EXE=python"
where python >nul 2>nul
if errorlevel 1 (
    where py >nul 2>nul
    if errorlevel 1 (
        echo [!] Khong tim thay Python tren may tinh!
        echo     Vui long cai dat Python tai https://www.python.org/
        pause
        exit /b 1
    ) else (
        set "PY_EXE=py -3"
    )
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo MUSE_STUDIO_PORT=18610 > .env
    )
)

echo [*] Dang khoi dong may chu backend tai cong 18610...
start "" http://localhost:18610/studio/

echo.
echo ========================================================
echo [OK] Muse Studio da san sang!
echo      Trinh duyet se tu dong mo: http://localhost:18610/studio/
echo      Khong tat cua so nay trong khi su dung Studio.
echo ========================================================
echo.

%PY_EXE% -m uvicorn app:app --host 127.0.0.1 --port 18610
pause
