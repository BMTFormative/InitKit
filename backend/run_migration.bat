@echo off
REM Multi-Tenant SaaS Backend Migration Launcher
REM Compatible with Windows 11
REM Version: 1.1 - Fixed syntax issues

title Multi-Tenant SaaS Backend Migration Tool

echo ================================================================
echo        Multi-Tenant SaaS Backend Migration Tool
echo ================================================================
echo.

REM Check if PowerShell is available
powershell -Command "Write-Host 'PowerShell Test'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required but not available!
    echo Please ensure PowerShell 5.1 or higher is installed.
    echo.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist app (
    echo ERROR: This script must be run from the backend project root directory.
    echo Please navigate to your FastAPI project root where 'app' folder exists.
    echo.
    echo Current directory: %CD%
    echo.
    echo Expected structure:
    echo   your-project/
    echo   ├── app/                   ^<-- Should exist
    echo   ├── run_migration.bat      ^<-- This file
    echo   └── migrate_backend.ps1    ^<-- Migration script
    echo.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo App directory found: OK
echo.

:MENU
echo Choose migration option:
echo 1. DRY RUN (Preview changes without modifying files)
echo 2. FULL MIGRATION (Create backup and migrate)
echo 3. CUSTOM OPTIONS
echo 4. VERIFY STRUCTURE (Check if migration worked)
echo 5. VIEW HELP
echo 6. EXIT
echo.
set /p "choice=Enter your choice (1-6): "

if "%choice%"=="1" goto DRY_RUN
if "%choice%"=="2" goto FULL_MIGRATION
if "%choice%"=="3" goto CUSTOM_OPTIONS
if "%choice%"=="4" goto VERIFY_STRUCTURE
if "%choice%"=="5" goto VIEW_HELP
if "%choice%"=="6" goto EXIT
echo Invalid choice. Please try again.
echo.
goto MENU

:DRY_RUN
echo.
echo ================================================================
echo                    RUNNING DRY RUN MODE
echo ================================================================
echo This will preview all changes without modifying any files.
echo.
powershell.exe -ExecutionPolicy Bypass -Command "& '.\migrate_backend.ps1' -DryRun -Verbose"
if errorlevel 1 (
    echo.
    echo ERROR: PowerShell script execution failed.
    echo Try running PowerShell as Administrator or check execution policy.
)
goto POST_EXECUTION

:FULL_MIGRATION
echo.
echo ================================================================
echo                  RUNNING FULL MIGRATION
echo ================================================================
echo This will create a backup and perform the full migration.
echo.
set /p "confirm=Are you sure you want to proceed? (y/N): "
if /i not "%confirm%"=="y" (
    echo Migration cancelled.
    echo.
    goto MENU
)
echo.
echo Starting migration...
powershell.exe -ExecutionPolicy Bypass -Command "& '.\migrate_backend.ps1' -Verbose"
if errorlevel 1 (
    echo.
    echo ERROR: Migration failed. Check the error messages above.
    echo Your files have not been modified.
)
goto POST_EXECUTION

:CUSTOM_OPTIONS
echo.
echo ================================================================
echo                    CUSTOM OPTIONS
echo ================================================================
echo Available options:
echo   -DryRun      : Preview without changes
echo   -Verbose     : Detailed logging
echo   -SkipBackup  : Skip backup creation (NOT RECOMMENDED)
echo   -BackupPath  : Custom backup location
echo.
echo Example: -DryRun -Verbose
echo.
set /p "custom_args=Enter PowerShell arguments: "
if "%custom_args%"=="" (
    echo No arguments provided. Returning to menu.
    goto MENU
)
echo.
powershell.exe -ExecutionPolicy Bypass -Command "& '.\migrate_backend.ps1' %custom_args%"
goto POST_EXECUTION

:VERIFY_STRUCTURE
echo.
echo ================================================================
echo                   VERIFYING STRUCTURE
echo ================================================================
echo Checking if migration was successful...
echo.
if exist verify_structure.ps1 (
    powershell.exe -ExecutionPolicy Bypass -Command "& '.\verify_structure.ps1' -Verbose"
) else (
    echo verify_structure.ps1 not found. Creating basic verification...
    echo.
    if exist "app\modules" (
        echo [OK] Modules directory exists
        echo Contents:
        dir "app\modules" /b 2>nul
    ) else (
        echo [ERROR] Modules directory not found
    )
    if exist "app\shared" (
        echo [OK] Shared directory exists
    ) else (
        echo [ERROR] Shared directory not found
    )
    echo.
    echo For detailed verification, ensure verify_structure.ps1 is in this directory.
)
goto POST_EXECUTION

:VIEW_HELP
echo.
echo ================================================================
echo                        HELP
echo ================================================================
echo.
echo MIGRATION PROCESS:
echo 1. Always start with DRY RUN to preview changes
echo 2. Run FULL MIGRATION to create the modular structure
echo 3. Use VERIFY STRUCTURE to confirm everything worked
echo 4. Gradually move your code to the new modules
echo.
echo TROUBLESHOOTING:
echo - If you get execution policy errors, run PowerShell as Administrator
echo - Ensure you're in the project root directory (where 'app' folder exists)
echo - Check that migrate_backend.ps1 file exists in this directory
echo.
echo FILES NEEDED:
echo - migrate_backend.ps1     (Main migration script)
echo - verify_structure.ps1    (Verification script)
echo - run_migration.bat       (This launcher)
echo.
echo SAFETY:
echo - Automatic backup is created before migration
echo - Dry run mode lets you preview all changes safely
echo - All existing files are preserved
echo.
pause
goto MENU

:POST_EXECUTION
echo.
echo ================================================================
echo                    EXECUTION COMPLETE
echo ================================================================
echo.
if exist migration_summary.md (
    echo Migration summary created: migration_summary.md
)
for %%f in (migration_log_*.txt) do (
    echo Check migration log: %%f
    goto found_log
)
:found_log
echo.
set /p "return_menu=Return to menu? (y/N): "
if /i "%return_menu%"=="y" goto MENU
goto EXIT

:EXIT
echo.
echo ================================================================
echo               Thank you for using the Migration Tool!
echo ================================================================
echo.
echo NEXT STEPS:
echo 1. Review the generated structure in app/modules/
echo 2. Check migration_summary.md for details
echo 3. Start moving your existing code to the new modules
echo 4. Test your application thoroughly
echo.
echo SUPPORT:
echo - Check migration log files for detailed information
echo - Use DRY RUN mode to safely test changes
echo - Keep backups until migration is complete
echo.
pause
exit /b 0