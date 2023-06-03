@echo off
pyinstaller --onefile .\dayz_server_manager.py
copy .\manager.cfg .\dist\
copy .\modslist.csv .\dist\
copy .\serverDZ.cfg .\dist\
pause
