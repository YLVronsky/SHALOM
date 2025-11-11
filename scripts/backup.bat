@echo off
setlocal enabledelayedexpansion

:: 1. Определяем корень проекта (родитель scripts)
pushd "%~dp0"
cd ..
set "PROJECT_ROOT=%CD%"
popd

:: 2. Пути
set "OUTPUT_DIR=%PROJECT_ROOT%\backup"
set "LOG_DIR=%PROJECT_ROOT%\logs"
set "LOG_FILE=%LOG_DIR%\backup.log"
set "BUILD_DIR=%PROJECT_ROOT%\build"

:: 3. Создание директорий
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

:: 4. Определение имени файла для нового бэкапа
set "base_name=all_sources"
set "counter=0"
set "OUTPUT_FILE=%OUTPUT_DIR%\%base_name%.txt"

:check_filename
if exist "%OUTPUT_FILE%" (
    set /a "counter+=1"
    set "OUTPUT_FILE=%OUTPUT_DIR%\%base_name%_!counter!.txt"
    goto :check_filename
)

:: 5. Очистка логов
del /q "%LOG_FILE%" >nul 2>&1

:: 6. Список разрешённых расширений
set "ALLOWED_EXTS=.cpp .h .hpp .c .cc .cs .java .py .sh .bat .js .ts .json .xml .yml .yaml .ini .conf .md .svg .ui .qrc .css"

:: 7. Заголовок
echo [%date% %time%] Start merge >> "%LOG_FILE%"
echo === All source files merged on %date% %time% === > "%OUTPUT_FILE%"

:: 8. Рекурсивный обход файлов
for /r "%PROJECT_ROOT%" %%F in (*) do (
    set "FULL=%%~fF"
    set "EXT=%%~xF"
    set "IS_ALLOWED=0"

    rem Проверка, что файл не из папок логов или бэкапа
    echo !FULL! | findstr /i /c:"\%OUTPUT_DIR%\" >nul
    if !errorlevel! == 0 (
        echo [SKIP] backup folder: %%F >> "%LOG_FILE%"
    ) else (
        echo !FULL! | findstr /i /c:"\%LOG_DIR%\" >nul
        if !errorlevel! == 0 (
            echo [SKIP] logs folder: %%F >> "%LOG_FILE%"
        ) else (
            rem Проверка разрешённого расширения
            for %%E in (%ALLOWED_EXTS%) do (
                if /i "!EXT!"=="%%E" set "IS_ALLOWED=1"
            )

            if "!IS_ALLOWED!"=="1" (
                echo [ADD] %%~fF >> "%LOG_FILE%"
                echo. >> "%OUTPUT_FILE%"
                echo ==== FILE: %%~dpnxF ==== >> "%OUTPUT_FILE%"
                type "%%~fF" >> "%OUTPUT_FILE%"
                echo. >> "%OUTPUT_FILE%"
                echo. >> "%OUTPUT_FILE%"
            ) else (
                echo [SKIP] Unsupported file: %%~fF >> "%LOG_FILE%"
            )
        )
    )
)

echo [%date% %time%] Merge complete >> "%LOG_FILE%"
echo Done. Output: %OUTPUT_FILE%
echo Log:    %LOG_FILE%