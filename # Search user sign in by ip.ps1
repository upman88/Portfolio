# Function to install necessary modules
function Install-Modules {
    $modules = @("AzureAD", "MSOnline", "Microsoft.Graph")
    foreach ($module in $modules) {
        if (-not (Get-Module -ListAvailable -Name $module)) {
            Install-Module -Name $module -Force
        }
    }
}

# Function to connect to Azure AD
function Connect-AzureADServices {
    try {
        Connect-AzureAD
        Connect-MsolService
        Write-Host "Connected to Azure AD and MS Online services." -ForegroundColor Green
    } catch {
        Write-Host "Failed to connect to Azure AD or MS Online services." -ForegroundColor Red
        exit
    }
}

# Function to search logs using AzureAD module
function Search-UsingAzureAD {
    try {
        $signInLogs = Get-AzureADAuditSignInLogs -All $true
        $filteredLogs = $signInLogs | Where-Object { $_.IPAddress -eq $searchIP }
        if ($filteredLogs) {
            $filteredLogs
        } else {
            Write-Host "No logs found for IP address $searchIP using AzureAD module." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Error retrieving logs using AzureAD module." -ForegroundColor Red
    }
}

# Function to search logs using Microsoft Graph API with client credentials
function Search-UsingGraphAPI {
    try {
        # Prompt for client credentials
        $clientId = Read-Host "Enter the Azure AD application (client) ID"
        $tenantId = Read-Host "Enter the Azure AD directory (tenant) ID"
        $clientSecret = Read-Host "Enter the Azure AD client secret" -AsSecureString

        # Convert the secure string to plain text for authentication
        $clientSecretPlainText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret))

        # Connect to Microsoft Graph using client credentials
        $tokenResponse = Invoke-RestMethod -Uri "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token" `
            -Method POST `
            -ContentType "application/x-www-form-urlencoded" `
            -Body @{
                client_id     = $clientId
                scope         = "https://graph.microsoft.com/.default"
                client_secret = $clientSecretPlainText
                grant_type    = "client_credentials"
            }

        $accessToken = $tokenResponse.access_token

        # Set the authorization header for subsequent Graph API requests
        $headers = @{
            Authorization = "Bearer $accessToken"
        }

        $filter = "ipAddress eq '$searchIP'"
        $url = "https://graph.microsoft.com/v1.0/auditLogs/signIns?`$filter=$filter"

        $signInLogs = Invoke-RestMethod -Uri $url -Headers $headers -Method GET

        if ($signInLogs.value) {
            $signInLogs.value
        } else {
            Write-Host "No logs found for IP address $searchIP using Microsoft Graph API." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Error retrieving logs using Microsoft Graph API." -ForegroundColor Red
        Write-Host $_.Exception.Message
    }
}

# Main script execution
Install-Modules

# Prompt the user to enter the IP address
$searchIP = Read-Host "Enter the IP address to search for"

Connect-AzureADServices
Search-UsingAzureAD
Search-UsingGraphAPI
