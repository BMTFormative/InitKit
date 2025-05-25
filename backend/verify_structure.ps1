# Structure Verification Script
# Compatible with PowerShell 5.1
# Verifies the modular migration was successful

param(
    [switch]$Verbose = $false
)

$script:Passed = 0
$script:Failed = 0
$script:Warnings = 0

function Write-Check {
    param(
        [string]$Description,
        [bool]$Result,
        [string]$Details = "",
        [bool]$IsWarning = $false
    )
    
    if ($Result) {
        Write-Host "✓ " -ForegroundColor Green -NoNewline
        Write-Host $Description -ForegroundColor White
        if ($Details -and $Verbose) {
            Write-Host "    $Details" -ForegroundColor Gray
        }
        $script:Passed++
    } else {
        if ($IsWarning) {
            Write-Host "⚠ " -ForegroundColor Yellow -NoNewline
            Write-Host $Description -ForegroundColor Yellow
            $script:Warnings++
        } else {
            Write-Host "✗ " -ForegroundColor Red -NoNewline
            Write-Host $Description -ForegroundColor Red
            $script:Failed++
        }
        if ($Details) {
            Write-Host "    $Details" -ForegroundColor Gray
        }
    }
}

function Test-DirectoryStructure {
    Write-Host "`n=== Directory Structure ===" -ForegroundColor Cyan
    
    # Test main directories
    Write-Check "App directory exists" (Test-Path "app")
    Write-Check "Modules directory exists" (Test-Path "app/modules")
    Write-Check "Shared directory exists" (Test-Path "app/shared")
    
    # Test module directories
    $expectedModules = @("auth", "tenants", "subscriptions", "credits", "api_keys", "ai_proxy", "email", "invitations", "items")
    
    foreach ($module in $expectedModules) {
        $modulePath = "app/modules/$module"
        Write-Check "Module '$module' directory exists" (Test-Path $modulePath)
        
        if (Test-Path $modulePath) {
            # Check module files
            Write-Check "  $module/__init__.py exists" (Test-Path "$modulePath/__init__.py")
            Write-Check "  $module/models.py exists" (Test-Path "$modulePath/models.py")
            Write-Check "  $module/service.py exists" (Test-Path "$modulePath/service.py")
            Write-Check "  $module/routes.py exists" (Test-Path "$modulePath/routes.py")
        }
    }
    
    # Test shared structure
    Write-Check "Shared constants directory exists" (Test-Path "app/shared/constants")
    Write-Check "Shared utils directory exists" (Test-Path "app/shared/utils")
    Write-Check "Shared exceptions directory exists" (Test-Path "app/shared/exceptions")
}

function Test-FileContent {
    Write-Host "`n=== File Content Validation ===" -ForegroundColor Cyan
    
    # Test main.py updates
    if (Test-Path "app/main.py") {
        $mainContent = Get-Content "app/main.py" -Raw
        Write-Check "main.py contains custom_generate_unique_id function" ($mainContent -match "custom_generate_unique_id")
        Write-Check "main.py has proper error handling" ($mainContent -match "IndexError|AttributeError")
    }
    
    # Test module init files
    $moduleInitPath = "app/modules/auth/__init__.py"
    if (Test-Path $moduleInitPath) {
        $initContent = Get-Content $moduleInitPath -Raw
        Write-Check "Module __init__.py has proper imports" ($initContent -match "from \.models import \*")
    }
    
    # Test shared exceptions
    $exceptionsPath = "app/shared/exceptions/custom.py"
    if (Test-Path $exceptionsPath) {
        $exceptionsContent = Get-Content $exceptionsPath -Raw
        Write-Check "Custom exceptions defined" ($exceptionsContent -match "TenantNotFoundError")
    }
}

function Test-OriginalFiles {
    Write-Host "`n=== Original Files Preserved ===" -ForegroundColor Cyan
    
    # Check that original files still exist
    Write-Check "Original models.py preserved" (Test-Path "app/models.py")
    Write-Check "Original crud.py preserved" (Test-Path "app/crud.py")
    Write-Check "Original core directory preserved" (Test-Path "app/core")
    Write-Check "Original api directory preserved" (Test-Path "app/api")
    Write-Check "Original services preserved" (Test-Path "app/services") $true $true # Warning only
    
    # Check if routes directory exists
    Write-Check "Original routes preserved" (Test-Path "app/api/routes") $true $true # Warning only
}

function Test-BackupExists {
    Write-Host "`n=== Backup Verification ===" -ForegroundColor Cyan
    
    # Look for backup directories
    $backupDirs = Get-ChildItem -Directory | Where-Object { $_.Name -match "backup_\d{8}_\d{6}" }
    
    if ($backupDirs.Count -gt 0) {
        $latestBackup = $backupDirs | Sort-Object Name | Select-Object -Last 1
        Write-Check "Recent backup exists" $true "Latest: $($latestBackup.Name)"
        
        # Verify backup contents
        $backupAppPath = Join-Path $latestBackup.FullName "app"
        Write-Check "Backup contains app directory" (Test-Path $backupAppPath)
    } else {
        Write-Check "Backup directory found" $false "No backup_* directories found" $true
    }
}

function Show-Summary {
    Write-Host "`n" + "="*50 -ForegroundColor Cyan
    Write-Host "             VERIFICATION SUMMARY" -ForegroundColor Cyan
    Write-Host "="*50 -ForegroundColor Cyan
    
    Write-Host "✓ Passed: " -ForegroundColor Green -NoNewline
    Write-Host $script:Passed -ForegroundColor White
    
    if ($script:Warnings -gt 0) {
        Write-Host "⚠ Warnings: " -ForegroundColor Yellow -NoNewline
        Write-Host $script:Warnings -ForegroundColor White
    }
    
    if ($script:Failed -gt 0) {
        Write-Host "✗ Failed: " -ForegroundColor Red -NoNewline
        Write-Host $script:Failed -ForegroundColor White
    }
    
    Write-Host ""
    
    if ($script:Failed -eq 0) {
        Write-Host "🎉 Migration verification completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Start extracting models from app/models.py to module-specific models.py files"
        Write-Host "2. Move business logic from app/crud.py to module services"
        Write-Host "3. Update route imports to use new module structure"
        Write-Host "4. Test your application thoroughly"
    } else {
        Write-Host "❌ Migration verification found issues!" -ForegroundColor Red
        Write-Host "Please review the failed checks above and re-run the migration if needed."
    }
    
    Write-Host ""
}

function Show-NextSteps {
    Write-Host "=== DETAILED NEXT STEPS ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Model Migration:" -ForegroundColor Yellow
    Write-Host "   - Extract User-related models from app/models.py to app/modules/auth/models.py"
    Write-Host "   - Extract Tenant models to app/modules/tenants/models.py"
    Write-Host "   - Continue for other modules..."
    Write-Host ""
    Write-Host "2. Service Migration:" -ForegroundColor Yellow
    Write-Host "   - Move user CRUD operations to app/modules/auth/service.py"
    Write-Host "   - Move tenant operations to app/modules/tenants/service.py"
    Write-Host "   - Update existing services in app/services/ to use new structure"
    Write-Host ""
    Write-Host "3. Route Updates:" -ForegroundColor Yellow
    Write-Host "   - Update app/api/main.py to include new module routers"
    Write-Host "   - Gradually migrate route logic to module-specific routes"
    Write-Host ""
    Write-Host "4. Import Updates:" -ForegroundColor Yellow
    Write-Host "   - Update imports throughout the codebase"
    Write-Host "   - Use new module structure: from app.modules.auth.models import User"
    Write-Host ""
    Write-Host "5. Testing:" -ForegroundColor Yellow
    Write-Host "   - Test each endpoint after migration"
    Write-Host "   - Ensure all existing functionality still works"
    Write-Host "   - Run your test suite"
}

# Main execution
Write-Host "Multi-Tenant SaaS Backend Structure Verification" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "Checking project structure and migration results..."
Write-Host ""

# Run all tests
Test-DirectoryStructure
Test-FileContent
Test-OriginalFiles
Test-BackupExists

# Show results
Show-Summary

if ($Verbose) {
    Show-NextSteps
}