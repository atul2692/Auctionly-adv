# PowerShell script to download and extract Redis for Windows

# Create Redis directory if it doesn't exist
$redisDir = ".\redis"
if (!(Test-Path -Path $redisDir)) {
    New-Item -ItemType Directory -Path $redisDir
}

# Download Redis for Windows (Microsoft fork)
$url = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
$output = "$redisDir\redis.zip"

Write-Host "Downloading Redis for Windows..."
Invoke-WebRequest -Uri $url -OutFile $output

# Extract the ZIP file
Write-Host "Extracting Redis..."
Expand-Archive -Path $output -DestinationPath $redisDir -Force

# Remove the ZIP file
Remove-Item -Path $output

Write-Host "Redis for Windows has been installed to $redisDir"
Write-Host "To start Redis server, run: .\redis\redis-server.exe" 