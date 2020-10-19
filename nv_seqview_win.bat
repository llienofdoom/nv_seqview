SET scriptPath=%~dp0
cd /d %scriptPath%
CALL venv_win\Scripts\activate
python main.py %*
pause
