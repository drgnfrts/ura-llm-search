@echo off
setlocal EnableDelayedExpansion


REM Set source and destination directories - FILL IN BEFORE STARTING

set "source_dir=C:\Users\nicol\intern\ura-llm-search\data\Development-Control"

set "dest_dir=C:\Users\nicol\intern\ura-llm-search\data\Development-Control-md"



REM Replicate directory structure in destination

for /r "%source_dir%" %%d in (.) do (

    set "sub_path=%%~dpnd"

    set "sub_path=!sub_path:%source_dir%=!"

    mkdir "%dest_dir%!sub_path!"

)

REM Traverse the source directory and its subdirectories, creating the a new destination file path in the new destination subdirectry

for /r "%source_dir%" %%G in (*.html) do (

    set "file_name=%%~nG"

    set "relative_path=%%~dpG"

    set "relative_path=!relative_path:%source_dir%=!"

    set "docx_file=%dest_dir%!relative_path!!file_name!.md"

    REM Convert HTML to DOCX and place it in corresponding directory in destination

    pandoc -s -o "!docx_file!" -f html -t markdown_strict "%%G"

)

endlocal