@echo off

setlocal enabledelayedexpansion



REM Set source and destination directories

set "source_dir=C:\Users\nicol\intern\ura-llm-search\data\Development-Control"

set "dest_dir=C:\Users\nicol\intern\ura-llm-search\data\Development-Control-docx"



REM Create directory structure in destination

for /r "%source_dir%" %%d in (.) do (

    set "sub_path=%%~dpnd"

    set "sub_path=!sub_path:%source_dir%=!"

    mkdir "%dest_dir%!sub_path!"

)



REM Traverse the source directory and its subdirectories to convert HTML to DOCX

for /r "%source_dir%" %%f in (*.html) do (

    set "html_file=%%f"

    REM set "relative_path=%%~dpFf"

    echo %html_file%

    @REM REM Turn off delayed expansion to handle special characters properly

    @REM setlocal disabledelayedexpansion

    @REM set "relative_path=%relative_path:%source_dir%=%"

    @REM set "docx_file=%dest_dir%%relative_path:~0,-1%.docx"

    @REM endlocal & set "docx_file=%docx_file%"



    REM Convert HTML to DOCX and place it in corresponding directory in destination

    REM pandoc "%%f" -o "!docx_file!"

)



endlocal

pause