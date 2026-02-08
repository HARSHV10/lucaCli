$ErrorActionPreference = "Stop"

Write-Host "Installing LucaCli..." -ForegroundColor Cyan

# Install the package
pip install -e .

# Get Python Scripts directory (User installation path)
$pythonPath = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$pythonPath = $pythonPath.Trim()

Write-Host "Python Scripts directory: $pythonPath" -ForegroundColor Gray

# Check if PATH contains the scripts directory
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -like "*$pythonPath*") {
    Write-Host "PATH already configured." -ForegroundColor Green
} else {
    Write-Host "Adding to PATH..." -ForegroundColor Yellow
    $newPath = $currentPath + ";$pythonPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    # Update current session PATH (approximate)
    $env:PATH += ";$pythonPath"
    Write-Host "PATH updated." -ForegroundColor Green
}

Write-Host "`nInstallation Complete!" -ForegroundColor Green
Write-Host "You can now run 'luca' from anywhere." -ForegroundColor Cyan
Write-Host "Note: You might need to restart your terminal for changes to take full effect." -ForegroundColor Yellow
