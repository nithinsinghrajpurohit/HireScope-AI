@echo off
echo ===================================================
echo   HireScope AI - Setup and Launch Script
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10 or higher and try again.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate

:: Upgrade pip and install requirements
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing required packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    pause
    exit /b 1
)

:: Download NLTK data
echo [INFO] Downloading NLTK tokenizer and stopword corpora...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
if %errorlevel% neq 0 (
    echo [WARNING] Failed to download NLTK data. Some features might not work without internet.
)

:: Launch Streamlit app
echo [INFO] Starting Streamlit dashboard...
echo.
echo ===================================================
echo   HireScope AI dashboard is launching!
echo   If a browser window does not open automatically,
echo   visit http://localhost:8501
echo ===================================================
echo.
streamlit run app.py

pause
