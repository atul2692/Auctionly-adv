@echo off
echo Starting Redis server...
start cmd /k "cd /d %CD%\redis && redis-server.exe"
echo Redis server started. 