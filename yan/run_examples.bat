@echo off
chcp 65001 >nul
echo ========================================
echo Yan Language Examples Runner
echo ========================================
echo.

cd /d "%~dp0"

for %%f in (examples\*.yan) do (
    echo ========================================
    echo Running: %%f
    echo ========================================
    python main.py "%%f"
    echo.
    echo.
)

echo ========================================
echo All examples completed.
echo ========================================
pause
