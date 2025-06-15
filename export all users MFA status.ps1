# Install and import the MSOnline module
Install-Module -Name MSOnline -Force -AllowClobber -Scope CurrentUser
Import-Module MSOnline

# Connect to Azure AD (you will be prompted to enter credentials)
Connect-MsolService

# Get all users and export their MFA status to a CSV file in each user's download folder
$users = Get-MsolUser -EnabledFilter EnabledOnly -MaxResults 10000

foreach ($user in $users) {
    $MFAMethod = $user.StrongAuthenticationMethods | Where-Object { $_.IsDefault -eq $true } | Select-Object -ExpandProperty MethodType
    $Method = ""

    If (($user.StrongAuthenticationRequirements) -or ($user.StrongAuthenticationMethods)) {
        Switch ($MFAMethod) {
            "OneWaySMS" { $Method = "SMS token" }
            "TwoWayVoiceMobile" { $Method = "Phone call verification" }
            "PhoneAppOTP" { $Method = "Hardware token or authenticator app" }
            "PhoneAppNotification" { $Method = "Authenticator app" }
        }
    }

    $outputObject = [PSCustomObject]@{
        DisplayName       = $user.DisplayName
        UserPrincipalName = $user.UserPrincipalName
        "MFA Enabled"     = if ($user.StrongAuthenticationMethods) { $true } else { $false }
        "MFA Default Type"= $Method
        "SMS token"       = if ($user.StrongAuthenticationMethods.MethodType -contains "OneWaySMS") { $true } else { "-" }
        "Phone call verification" = if ($user.StrongAuthenticationMethods.MethodType -contains "TwoWayVoiceMobile") { $true } else { "-" }
        "Hardware token or authenticator app" = if ($user.StrongAuthenticationMethods.MethodType -contains "PhoneAppOTP") { $true } else { "-" }
        "Authenticator app" = if ($user.StrongAuthenticationMethods.MethodType -contains "PhoneAppNotification") { $true } else { "-" }
        MFAEnforced       = if ($user.StrongAuthenticationRequirements) { $true } else { "-" }
    }

    # Export the results to CSV in the user's download folder
    $outputPath = Join-Path -Path $([System.Environment]::GetFolderPath('UserProfile')) -ChildPath 'Downloads\MFA_Status.csv'
    $outputObject | Export-Csv -Path $outputPath -Append -NoTypeInformation
}

Write-Host "MFA status for all users exported to CSV: $outputPath"
