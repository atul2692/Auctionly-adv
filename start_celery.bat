@echo off
echo Starting Redis, Celery worker, and Celery beat...

REM Start Redis
start cmd /k "cd /d %CD%\redis && redis-server.exe"
echo Redis server started.

REM Wait for Redis to start
timeout /t 3

REM Start Celery worker
start cmd /k "cd /d %CD% && .\env\Scripts\activate && celery -A auction_site worker -l INFO -P solo"

REM Start Celery beat
start cmd /k "cd /d %CD% && .\env\Scripts\activate && celery -A auction_site beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler"

echo All services started.
echo To test if everything is working, run the Django development server in a new command prompt. 