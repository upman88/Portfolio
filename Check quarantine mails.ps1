# Connect to Exchange Online
Connect-ExchangeOnline -UserPrincipalName patrick@example.com

# Get all quarantined messages for all users
$quarantinedEmails = Get-QuarantineMessage -PageSize 1000

# Remove duplicate messages based on MessageId
$uniqueEmails = $quarantinedEmails | Sort-Object MessageId -Unique

# Export the unique quarantined emails to a CSV file (no filtering)
$uniqueEmails | Select-Object UserAddress, MessageId, Subject, SenderAddress, Received, Expires, QuarantineType | Export-Csv -Path "C:\Users\pupman\OneDrive - AuthorityBrands\Desktop\quarantinedEmails.csv" -NoTypeInformation

# Display unique emails to the user for reference
$uniqueEmails | Select-Object UserAddress, MessageId, Subject, SenderAddress, Received

# Prompt user for the MessageId to release
$messageIdToRelease = Read-Host -Prompt "Please enter the Message ID of the email you want to release"

# Check if the provided Message ID exists in the unique emails
if ($uniqueEmails.MessageId -contains $messageIdToRelease) {
    # Release the specified quarantined message
    Release-QuarantineMessage -MessageId $messageIdToRelease -Confirm:$false
    Write-Host "Message ID $messageIdToRelease has been released from quarantine."
} else {
    Write-Host "Error: Message ID $messageIdToRelease not found in the list of quarantined emails."
}

# Disconnect from Exchange Online
Disconnect-ExchangeOnline -Confirm:$false
