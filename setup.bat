@echo off

if exist venv/ (
  echo remake venv
  rmdir /s /q venv
) else (
  echo make new venv
)

@echo on

py -3 -m venv venv
call .\venv\Scripts\Activate.bat
python --version
pip install numpy
call deactivate
