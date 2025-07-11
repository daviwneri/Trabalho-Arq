@echo off
title Simulador RISC-V - Interface Grafica
cls

echo ====================================
echo   SIMULADOR RISC-V COM PIPELINE
echo   Interface Grafica com Tkinter
echo ====================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.6+ e tente novamente.
    pause
    exit /b 1
)

echo.
echo Verificando Tkinter...
python -c "import tkinter; print('Tkinter OK')"
if errorlevel 1 (
    echo ERRO: Tkinter nao encontrado!
    echo Instale o modulo tkinter e tente novamente.
    pause
    exit /b 1
)

echo.
echo Iniciando interface grafica...
echo.

REM Tentar com ambiente virtual primeiro, depois python global
if exist ".venv\Scripts\python.exe" (
    echo Usando ambiente virtual...
    .venv\Scripts\python.exe interface_grafica.py
) else (
    echo Usando Python global...
    python interface_grafica.py
)

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao executar a interface!
    echo Verifique se todos os arquivos estao presentes:
    echo - montador.py
    echo - simulador.py
    echo - interface_grafica.py
    echo - Teste.asm
    echo.
    pause
)

echo.
echo Interface fechada.
pause
