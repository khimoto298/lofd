if not exist venv/ (
  call setup.bat
)

call .\venv\Scripts\Activate.bat
python --version
pip list
echo ======================================
echo �v���O�������N�����܂���
echo ======================================
python .\main.py
if %errorlevel% neq 0 (
	echo ======================================
	echo �v���O�������ُ�I�����܂���
	echo ======================================
	cmd /k call deactivate
) else (
	call deactivate
)
