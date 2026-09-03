@echo off
setlocal

echo.
echo ==========================================
echo GitHub SeasonData Downloader
echo ==========================================
echo.
echo Enter the destination folder.
echo Example: D:\Test\F1
echo.

set /p "DEST=Destination: "

if not defined DEST (
    echo.
    echo No destination entered.
    pause
    exit /b 1
)

echo.
echo Downloading to:
echo "%DEST%"
echo.

set "ZIP=%TEMP%\F1-Challenge-99-02.zip"
set "TEMP_DIR=%TEMP%\F1-Challenge-99-02-download"

echo Downloading repository ZIP...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
"$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/gabberworld/F1-Challenge-99-02/archive/refs/heads/main.zip' -OutFile $env:ZIP"

if errorlevel 1 (
    echo.
    echo ==========================================
    echo ERROR - GitHub download failed!
    echo ==========================================
    pause
    exit /b 1
)

echo Download complete.
echo.
echo Extracting...

if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
"Expand-Archive -LiteralPath $env:ZIP -DestinationPath $env:TEMP_DIR -Force"

if errorlevel 1 (
    echo.
    echo ==========================================
    echo ERROR - ZIP extraction failed!
    echo ==========================================
    del "%ZIP%" >nul 2>&1
    pause
    exit /b 1
)

echo Extraction complete.
echo.
echo Copying SeasonData...

if not exist "%DEST%" mkdir "%DEST%"

robocopy "%TEMP_DIR%\F1-Challenge-99-02-main\SeasonData" "%DEST%" /E

if errorlevel 8 (
    echo.
    echo ==========================================
    echo ERROR - Copy failed!
    echo ==========================================
    rmdir /s /q "%TEMP_DIR%" >nul 2>&1
    del "%ZIP%" >nul 2>&1
    pause
    exit /b 1
)

echo.
echo Cleaning temporary files...

rmdir /s /q "%TEMP_DIR%" >nul 2>&1
del "%ZIP%" >nul 2>&1

echo.
echo ==========================================
echo Download complete!
echo ==========================================
echo.
echo Files were downloaded to:
echo "%DEST%"
echo.

pause