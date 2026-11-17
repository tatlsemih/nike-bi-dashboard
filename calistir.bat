@echo off
REM ===============================================================
REM  Nike BI Dashboard - Windows calistirma scripti
REM ---------------------------------------------------------------
REM  Bu dosyaya cift tiklayarak dashboard'u ayaga kaldirabilirsin.
REM  Python ve pip kurulu olmali (python.org uzerinden).
REM ===============================================================

echo.
echo ============================================================
echo   Nike (NKE) BI Dashboard - Is Zekasi ve Karar Verme
echo ============================================================
echo.

REM Gerekli paketleri kontrol et / kur
echo [1/2] Gerekli Python paketleri kontrol ediliyor...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo HATA: Paketler kurulamadi.
    echo Onceden "pip install streamlit pandas numpy plotly" komutunu calistir.
    pause
    exit /b 1
)

echo.
echo [2/2] Dashboard baslatiliyor...
echo Tarayicin otomatik acilacak. Kapatmak icin bu pencerede Ctrl+C.
echo.

streamlit run BIDashboard.py

pause
