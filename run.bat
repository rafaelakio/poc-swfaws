@echo off
REM Script de automação para Windows
REM Facilita a execução dos componentes da aplicação

echo.
echo ========================================
echo   AWS SWF Workflow - Menu Principal
echo ========================================
echo.
echo 1. Setup inicial (registrar dominio e workflow)
echo 2. Iniciar Decision Worker
echo 3. Iniciar Activity Worker
echo 4. Executar demonstracao
echo 5. Executar workflow customizado
echo 6. Sair
echo.

set /p choice="Escolha uma opcao (1-6): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto decision
if "%choice%"=="3" goto activity
if "%choice%"=="4" goto demo
if "%choice%"=="5" goto custom
if "%choice%"=="6" goto end

:setup
echo.
echo Executando setup inicial...
python setup.py
pause
goto end

:decision
echo.
echo Iniciando Decision Worker...
echo Pressione Ctrl+C para parar
python decision_worker.py
pause
goto end

:activity
echo.
echo Iniciando Activity Worker...
echo Pressione Ctrl+C para parar
python activity_worker.py
pause
goto end

:demo
echo.
echo Executando demonstracao...
echo.
echo IMPORTANTE: Certifique-se de que os workers estao rodando!
echo - Decision Worker (em outro terminal)
echo - Activity Worker (em outro terminal)
echo.
pause
python demo.py
pause
goto end

:custom
echo.
echo Executando workflow customizado...
python workflow_starter.py
pause
goto end

:end
echo.
echo Ate logo!
