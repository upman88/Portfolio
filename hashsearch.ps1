# Prompt the user to enter the target hash
$targetHash = Read-Host "Enter the target hash (SHA256)"

# Counter for files deleted
$filesDeletedCount = 0
$hashFoundLocations = @()

# Function to check if the hash is found in a file
function CheckFileForHash($filePath) {
    try {
        # Compute the SHA256 hash of the file content
        $hashAlgorithm = 'SHA256'
        $fileHash = Get-FileHash -Path $filePath -Algorithm $hashAlgorithm | Select-Object -ExpandProperty Hash
        
        # Compare the computed hash with the target hash
        if ($fileHash -eq $targetHash) {
            return $true
        }
    } catch {
        # Catch errors related to file access
        Write-Output "Error processing file: $filePath - $_"
    }
    
    return $false
}

# Function to search for the hash and delete containing file
function SearchAndDeleteFile($currentDirectory) {
    Write-Output "Pending: Searching for hash in $currentDirectory"
    
    # Get all the files in the current directory
    $files = Get-ChildItem -Path $currentDirectory -Recurse -File -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        # Check if the file contains the target hash
        if (CheckFileForHash $file.FullName) {
            Write-Output "Hash found in $file. Deleting file: $file"
            Remove-Item -Path $file.FullName -Force
            $global:filesDeletedCount++
            $hashFoundLocations += "Hash found in $file"
        }
    }
}

# Get all logical drives on the system
$drives = Get-PSDrive -PSProvider FileSystem

# Loop through each drive and look for the hash
foreach ($drive in $drives) {
    $driveRoot = $drive.Root
    Write-Output "Starting search on drive: $driveRoot"
    
    try {
        SearchAndDeleteFile $driveRoot
    } catch {
        Write-Output "Error processing drive ${driveRoot}: $_"
    }
}

# Display the summary
if ($hashFoundLocations.Count -gt 0) {
    Write-Output "Execution complete. Hash found in the following locations:"
    $hashFoundLocations | ForEach-Object { Write-Output $_ }
} else {
    Write-Output "Execution complete. Hash not found."
}

Write-Output "Files deleted: $filesDeletedCount"

# Wait for user input to close the PowerShell session
Read-Host "Press Enter to exit..."
