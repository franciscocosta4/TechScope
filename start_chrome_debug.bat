@echo off
set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
set PROFILE_DIR=C:\Users\Utilizador\CODE\TechScope\data-pipeline\scrapers\chrome-profile

"%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%PROFILE_DIR%"
