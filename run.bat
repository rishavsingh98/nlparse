@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting NLParse Intent Parser...

REM Function to kill processes on port
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8505') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8506') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Try different Python commands in order of preference
set "FOUND_PYTHON="

REM Check py launcher first (Windows Python Launcher)
echo 🔍 Checking Python Launcher (py)...
py --version >nul 2>&1
if !errorlevel! equ 0 (
    py -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Using Python Launcher with streamlit
        goto :start_with_py
    ) else (
        echo ⚠️  Streamlit not found in Python Launcher, installing...
        py -m pip install streamlit
        if !errorlevel! equ 0 (
            echo ✅ Streamlit installed successfully
            goto :start_with_py
        )
    )
)

REM Check python command
echo 🔍 Checking Python (python)...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    python -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Using Python with streamlit
        goto :start_with_python
    ) else (
        echo ⚠️  Streamlit not found in Python, installing...
        python -m pip install streamlit
        if !errorlevel! equ 0 (
            echo ✅ Streamlit installed successfully
            goto :start_with_python
        )
    )
)

REM Check python3 command
echo 🔍 Checking Python 3 (python3)...
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    python3 -c "import streamlit" >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Using Python 3 with streamlit
        goto :start_with_python3
    ) else (
        echo ⚠️  Streamlit not found in Python 3, installing...
        python3 -m pip install streamlit
        if !errorlevel! equ 0 (
            echo ✅ Streamlit installed successfully
            goto :start_with_python3
        )
    )
)

REM If we get here, nothing worked
echo ❌ Could not find a suitable Python installation with streamlit
echo 📋 Please ensure Python 3.9+ is installed and try:
echo    pip install streamlit
echo    python -m streamlit run chat_app.py --server.port 8505
pause
exit /b 1

:start_with_py
echo 🌐 App will be available at: http://localhost:8505
echo 🛑 Press Ctrl+C to stop the server
py -m streamlit run chat_app.py --server.port 8505
goto :end

:start_with_python
echo 🌐 App will be available at: http://localhost:8505
echo 🛑 Press Ctrl+C to stop the server
python -m streamlit run chat_app.py --server.port 8505
goto :end

:start_with_python3
echo 🌐 App will be available at: http://localhost:8505
echo 🛑 Press Ctrl+C to stop the server
python3 -m streamlit run chat_app.py --server.port 8505
goto :end

:end
pause 