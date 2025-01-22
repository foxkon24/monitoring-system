@echo off

@if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

cd D:\xampp\htdocs\system\room_door\massage

cd %~dp0

python appmain.py

