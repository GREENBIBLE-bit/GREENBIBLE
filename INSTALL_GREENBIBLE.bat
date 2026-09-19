@echo off
cd /d "%~dp0"
echo Installing GREENBIBLE requirements...
py -m pip install sounddevice SpeechRecognition requests
if errorlevel 1 pause & exit /b 1
echo.
echo Put kjv.sqlite in this folder if it is not already here.
echo Testing Python files...
py -m py_compile app.py smart_parser.py
if errorlevel 1 (
 echo BUILD TEST FAILED.
 pause
 exit /b 1
)
echo BUILD TEST PASSED.
echo Start GREENBIBLE with: py app.py
pause
