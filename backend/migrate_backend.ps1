# Multi-Tenant SaaS Backend Migration Script
# Compatible with PowerShell 5.1 (Windows 11)
# Author: FastAPI Migration Assistant
# Version: 1.0

param(
    [switch]$DryRun = $false,
    [switch]$Verbose = $false,
    [string]$BackupPath = "",
    [switch]$SkipBackup = $false
)

# Script configuration
$script:LogFile = "migration_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$script:BackupDir = if ($BackupPath) { $BackupPath } else { "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" }
$script:ProjectRoot = Get-Location
$script:AppPath = Join-Path $script:ProjectRoot "app"

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $script:LogFile -Value $logMessage
}

# Error handling
function Handle-Error {
    param([string]$ErrorMessage)
    Write-Log "ERROR: $ErrorMessage" "ERROR"
    Write-Host "Migration failed. Check log file: $script:LogFile" -ForegroundColor Red
    if (Test-Path $script:BackupDir) {
        Write-Host "Backup available at: $script:BackupDir" -ForegroundColor Yellow
    }
    exit 1
}

# Create backup
function Create-Backup {
    if ($SkipBackup) {
        Write-Log "Skipping backup as requested"
        return
    }
    
    Write-Log "Creating backup..."
    try {
        if (Test-Path $script:BackupDir) {
            Remove-Item $script:BackupDir -Recurse -Force
        }
        
        # Create backup directory
        New-Item -ItemType Directory -Path $script:BackupDir -Force | Out-Null
        
        # Copy entire app directory
        if (Test-Path $script:AppPath) {
            Copy-Item -Path $script:AppPath -Destination (Join-Path $script:BackupDir "app") -Recurse -Force
            Write-Log "Backup created successfully at: $script:BackupDir"
        } else {
            Handle-Error "App directory not found: $script:AppPath"
        }
    } catch {
        Handle-Error "Failed to create backup: $($_.Exception.Message)"
    }
}

# Verify PowerShell version
function Test-PowerShellVersion {
    $version = $PSVersionTable.PSVersion
    Write-Log "PowerShell Version: $($version.ToString())"
    if ($version.Major -lt 5) {
        Handle-Error "PowerShell 5.0 or higher required. Current version: $($version.ToString())"
    }
}

# Create directory safely
function New-DirectoryIfNotExists {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
        Write-Log "Created directory: $Path"
    }
}

# Create file safely
function New-FileWithContent {
    param(
        [string]$Path,
        [string]$Content
    )
    if (-not $DryRun) {
        $Content | Out-File -FilePath $Path -Encoding UTF8
    }
    Write-Log "Created file: $Path"
}

# Module structure definition
$ModuleStructure = @{
    "auth" = @{
        "models" = @("User", "UserBase", "UserCreate", "UserUpdate", "UserUpdateMe", "UserPublic", "UsersPublic", "UpdatePassword", "Token", "TokenPayload", "NewPassword")
        "description" = "User authentication and JWT management"
    }
    "tenants" = @{
        "models" = @("Tenant", "TenantBase", "TenantCreate", "TenantUpdate", "TenantPublic", "TenantWithBalancePublic")
        "description" = "Multi-tenant management"
    }
    "subscriptions" = @{
        "models" = @("SubscriptionPlan", "SubscriptionPlanBase", "SubscriptionPlanCreate", "SubscriptionPlanUpdate", "SubscriptionPlanPublic", "SubscriptionPlansPublic", "UserSubscription", "UserSubscriptionBase", "UserSubscriptionCreate", "UserSubscriptionUpdate", "UserSubscriptionPublic")
        "description" = "Billing and subscription plans"
    }
    "credits" = @{
        "models" = @("CreditTransaction", "CreditTransactionCreate", "CreditTransactionPublic")
        "description" = "Credit system and transactions"
    }
    "api_keys" = @{
        "models" = @("TenantApiKey", "TenantApiKeyCreate", "TenantApiKeyPublic", "TenantApiKeyUpdate", "AdminApiKey", "AdminApiKeyCreate", "AdminApiKeyPublic", "AdminApiKeyUpdate", "AdminTenantApiKeyPublic")
        "description" = "Secure API key management"
    }
    "ai_proxy" = @{
        "models" = @()
        "description" = "AI API proxy with credit deduction"
    }
    "email" = @{
        "models" = @("EmailConfig", "EmailConfigBase")
        "description" = "Per-tenant SMTP configuration"
    }
    "invitations" = @{
        "models" = @("TenantInvitation", "TenantInvitationCreate", "TenantInvitationPublic")
        "description" = "User invitation system"
    }
    "items" = @{
        "models" = @("Item", "ItemBase", "ItemCreate", "ItemUpdate", "ItemPublic", "ItemsPublic")
        "description" = "Business entities"
    }
}

# Create module structure
function Create-ModuleStructure {
    Write-Log "Creating modular structure..."
    
    $modulesPath = Join-Path $script:AppPath "modules"
    New-DirectoryIfNotExists $modulesPath
    
    foreach ($moduleName in $ModuleStructure.Keys) {
        $moduleInfo = $ModuleStructure[$moduleName]
        $modulePath = Join-Path $modulesPath $moduleName
        
        Write-Log "Creating module: $moduleName - $($moduleInfo.description)"
        New-DirectoryIfNotExists $modulePath
        
        # Create __init__.py
        $initContent = @"
"""
$($moduleInfo.description)
"""
from .models import *
from .service import *
from .routes import *
"@
        New-FileWithContent (Join-Path $modulePath "__init__.py") $initContent
        
        # Create models.py
        $modelsContent = Create-ModuleModels $moduleName $moduleInfo.models
        New-FileWithContent (Join-Path $modulePath "models.py") $modelsContent
        
        # Create service.py
        $serviceContent = Create-ModuleService $moduleName
        New-FileWithContent (Join-Path $modulePath "service.py") $serviceContent
        
        # Create routes.py
        $routesContent = Create-ModuleRoutes $moduleName
        New-FileWithContent (Join-Path $modulePath "routes.py") $routesContent
    }
    
    # Create shared utilities
    Create-SharedUtilities
}

# Generate module models
function Create-ModuleModels {
    param(
        [string]$ModuleName,
        [array]$ModelNames
    )
    
    $imports = @"
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, Column, JSON

"@
    
    $models = ""
    if ($ModelNames.Count -eq 0) {
        $models = "# No specific models for this module - uses shared models"
    } else {
        $models = "# Models will be extracted from main models.py during migration"
    }
    
    return $imports + $models
}

# Generate module service
function Create-ModuleService {
    param([string]$ModuleName)
    
    return @"
"""
$ModuleName service layer
Contains business logic for $ModuleName operations
"""
import uuid
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from .models import *
from ..shared.exceptions import *


class $($ModuleName.Substring(0,1).ToUpper() + $ModuleName.Substring(1))Service:
    """Service class for $ModuleName operations"""
    
    def __init__(self):
        pass
    
    # Add service methods here
    # Example:
    # def get_by_id(self, session: Session, id: uuid.UUID):
    #     """Get entity by ID"""
    #     pass
"@
}

# Generate module routes
function Create-ModuleRoutes {
    param([string]$ModuleName)
    
    return @"
"""
$ModuleName API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from ...api.deps import SessionDep, CurrentUser, get_current_active_superuser
from .models import *
from .service import $($ModuleName.Substring(0,1).ToUpper() + $ModuleName.Substring(1))Service

router = APIRouter(prefix="/$ModuleName", tags=["$ModuleName"])
service = $($ModuleName.Substring(0,1).ToUpper() + $ModuleName.Substring(1))Service()

# Add routes here
# Example:
# @router.get("/")
# def list_items(session: SessionDep, current_user: CurrentUser):
#     """List items"""
#     return {"message": "$ModuleName routes"}
"@
}

# Create shared utilities
function Create-SharedUtilities {
    Write-Log "Creating shared utilities..."
    
    $sharedPath = Join-Path $script:AppPath "shared"
    New-DirectoryIfNotExists $sharedPath
    
    # Create constants
    $constantsPath = Join-Path $sharedPath "constants"
    New-DirectoryIfNotExists $constantsPath
    New-FileWithContent (Join-Path $constantsPath "__init__.py") ""
    
    $rolesContent = @"
"""
Role and status constants
"""

# User roles
class UserRoles:
    SUPERADMIN = "superadmin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"

# Subscription statuses
class SubscriptionStatus:
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

# Transaction types
class TransactionTypes:
    ADD = "add"
    DEDUCT = "deduct"
    REFUND = "refund"
"@
    New-FileWithContent (Join-Path $constantsPath "roles.py") $rolesContent
    
    # Create utils
    $utilsPath = Join-Path $sharedPath "utils"
    New-DirectoryIfNotExists $utilsPath
    New-FileWithContent (Join-Path $utilsPath "__init__.py") ""
    
    # Create exceptions
    $exceptionsPath = Join-Path $sharedPath "exceptions"
    New-DirectoryIfNotExists $exceptionsPath
    New-FileWithContent (Join-Path $exceptionsPath "__init__.py") ""
    
    $exceptionsContent = @"
"""
Custom exceptions for the application
"""
from fastapi import HTTPException


class TenantNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Tenant not found")


class InsufficientCreditsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=402, detail="Insufficient credits")


class UnauthorizedTenantAccessError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied to this tenant's resources")
"@
    New-FileWithContent (Join-Path $exceptionsPath "custom.py") $exceptionsContent
}

# Create updated main.py with proper error handling
function Create-UpdatedMain {
    Write-Log "Creating updated main.py..."
    
    $mainContent = @"
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for routes, handling missing tags gracefully"""
    try:
        if route.tags and len(route.tags) > 0:
            return f"{route.tags[0]}-{route.name}"
        else:
            # Fallback for routes without tags
            return f"default-{route.name}"
    except (IndexError, AttributeError):
        # Handle any other edge cases
        return f"route-{route.name}"


if sentry_sdk and settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Configure CORS middleware
cors_origins = settings.all_cors_origins
# For local development, allow all origins
if settings.ENVIRONMENT == "local":  # pragma: no cover
    cors_origins = ["*"]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
"@
    
    $mainPath = Join-Path $script:AppPath "main.py"
    if (-not $DryRun) {
        $mainContent | Out-File -FilePath $mainPath -Encoding UTF8
    }
    Write-Log "Updated main.py with proper error handling"
}

# Create migration summary
function Create-MigrationSummary {
    $summaryPath = "migration_summary.md"
    $summary = @"
# Backend Migration Summary

## Migration completed: $(Get-Date)

### Created Structure:
- **Modules Directory**: `app/modules/`
- **Shared Utilities**: `app/shared/`

### Domain Modules Created:
"@
    
    foreach ($moduleName in $ModuleStructure.Keys) {
        $moduleInfo = $ModuleStructure[$moduleName]
        $summary += @"

#### $moduleName
- **Description**: $($moduleInfo.description)
- **Models**: $($moduleInfo.models -join ", ")
- **Files**: models.py, service.py, routes.py, __init__.py
"@
    }
    
    $summary += @"

### Next Steps:
1. **Review generated structure** in `app/modules/`
2. **Extract models** from `app/models.py` to module-specific `models.py` files
3. **Move route logic** from existing routes to module routes
4. **Update imports** in existing files to use new module structure
5. **Test functionality** to ensure nothing is broken
6. **Gradually migrate** existing code to use new services

### Files Modified:
- `app/main.py` - Updated with better error handling for route tags

### Backup Location:
- **Backup Directory**: $script:BackupDir

### Migration Log:
- **Log File**: $script:LogFile
"@
    
    if (-not $DryRun) {
        $summary | Out-File -FilePath $summaryPath -Encoding UTF8
    }
    Write-Log "Created migration summary: $summaryPath"
}

# Main execution
function Main {
    Write-Log "Starting Multi-Tenant SaaS Backend Migration"
    Write-Log "Dry Run Mode: $DryRun"
    Write-Log "Project Root: $script:ProjectRoot"
    
    # Verify environment
    Test-PowerShellVersion
    
    if (-not (Test-Path $script:AppPath)) {
        Handle-Error "App directory not found. Please run from the backend project root."
    }
    
    # Create backup
    if (-not $DryRun) {
        Create-Backup
    } else {
        Write-Log "DRY RUN: Would create backup at $script:BackupDir"
    }
    
    # Create modular structure
    Create-ModuleStructure
    
    # Update main.py
    Create-UpdatedMain
    
    # Create migration summary
    Create-MigrationSummary
    
    Write-Log "Migration completed successfully!"
    Write-Log "Next steps:"
    Write-Log "1. Review the generated structure in app/modules/"
    Write-Log "2. Run the verification script: .\verify_structure.ps1"
    Write-Log "3. Start moving existing code to the new modules"
    Write-Log "4. Test your application to ensure everything still works"
    
    if ($DryRun) {
        Write-Log "This was a DRY RUN - no files were actually modified"
    }
}

# Execute main function
try {
    Main
} catch {
    Handle-Error $_.Exception.Message
}