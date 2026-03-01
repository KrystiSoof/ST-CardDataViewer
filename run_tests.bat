@echo off
echo ========================================
echo Running SillyTavern Card Editor Tests
echo ========================================
echo.

python -m pytest tests/ -v

echo.
pause
