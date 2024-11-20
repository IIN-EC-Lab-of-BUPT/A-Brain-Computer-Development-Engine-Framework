set "originalPath=%CD%"
start cmd /k "cd .\app\Algorithm && python -m Algorithm.main"
REM timeout /t 5 /nobreak
cd /d "%originalPath%"
start cmd /k "cd .\app\Collector && python -m ApplicationFramework.main"
cd /d "%originalPath%"
start cmd /k "cd .\app\ProcessHub && python -m ApplicationFramework.main"
cd /d "%originalPath%"
start cmd /k "cd .\app\Stimulator && python -m ApplicationFramework.main"
