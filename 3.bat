set "originalPath=%CD%"
start cmd /k "cd .\proceed\collector && java -jar collector.jar"
cd /d "%originalPath%"
start cmd /k "cd .\proceed\stimulator && java -jar stimulator.jar"
cd /d "%originalPath%"
start cmd /k "cd .\proceed\task && java -jar task.jar"
cd /d "%originalPath%"
