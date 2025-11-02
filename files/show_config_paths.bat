@echo off
echo ====================================
echo Claude Desktop Configuration Helper
echo ====================================
echo.
echo Copy these paths to your Claude Desktop config:
echo.

REM Get current directory
set CURRENT_DIR=%cd%

echo Python path:
echo %CURRENT_DIR%\venv\Scripts\python.exe
echo.

echo Server script path:
echo %CURRENT_DIR%\postgres_mcp.py
echo.

echo Claude Desktop config location:
echo %APPDATA%\Claude\claude_desktop_config.json
echo.

echo ====================================
echo Your configuration should look like:
echo ====================================
echo {
echo   "mcpServers": {
echo     "postgres": {
echo       "command": "%CURRENT_DIR:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%CURRENT_DIR:\=\\%\\postgres_mcp.py"],
echo       "env": {
echo         "POSTGRES_HOST": "localhost",
echo         "POSTGRES_PORT": "5432",
echo         "POSTGRES_DB": "your_database_name",
echo         "POSTGRES_USER": "your_username",
echo         "POSTGRES_PASSWORD": "your_password"
echo       }
echo     }
echo   }
echo }
echo.
pause
