# Connect to Exchange Online PowerShell
Connect-ExchangeOnline -UserPrincipalName patrick@example.com

# Connect to MS Online Service
Connect-MsolService

# Retrieve a list of shared mailboxes
$sharedMailboxes = Get-Mailbox -RecipientTypeDetails SharedMailbox

# Initialize an empty array to store results
$results = @()

# Loop through each shared mailbox
foreach ($mailbox in $sharedMailboxes) {
    $msolUser = Get-MsolUser -UserPrincipalName $mailbox.UserPrincipalName
    $mfaStatus = if ($msolUser.StrongAuthenticationRequirements) { "Enabled" } else { "Not Enabled" }

    # Add mailbox details and MFA status to results array
    $results += [PSCustomObject]@{
        DisplayName = $mailbox.DisplayName
        UserPrincipalName = $mailbox.UserPrincipalName
        MFAStatus = $mfaStatus
    }
}

# Determine the user's download folder
$downloadFolder = [Environment]::GetFolderPath("Desktop")

# Export results to a CSV file in the user's download folder
$results | Export-Csv -Path "$downloadFolder\sharedMBMFA.csv" -NoTypeInformation

# Disconnect from Exchange Online PowerShell
Disconnect-ExchangeOnline -Confirm:$false
