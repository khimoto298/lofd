if not exist venv/ (
  call setup.bat
)

call .\venv\Scripts\Activate.bat
python --version
pip list
echo ======================================
echo プログラムを起動しました
echo ======================================
python .\main.py
if %errorlevel% neq 0 (
	echo ======================================
	echo プログラムが異常終了しました
	echo ======================================
	cmd /k call deactivate
) else (
	call deactivate
)
