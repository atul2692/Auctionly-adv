@echo off
echo Setting up and starting the auction system with Celery...

REM Activate virtual environment
call .\env\Scripts\activate

REM Install Redis if not already installed
if not exist "redis" (
    echo Installing Redis for Windows...
    powershell -ExecutionPolicy Bypass -File .\install_redis.ps1
)

REM Make migrations
echo Running migrations...
python manage.py migrate

REM Start all services
echo Starting all services...
call start_celery.bat

REM Start Django development server
echo Starting Django development server...
start cmd /k "cd /d %CD% && .\env\Scripts\activate && python manage.py runserver"

echo System is up and running!
echo Access the site at http://localhost:8000/ 