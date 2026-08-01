param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Urls
)

if (-not $Urls -or $Urls.Count -eq 0) {
    Write-Error "No URLs provided."
    exit 1
}

function Find-Browser {
    param([string]$Name, [string[]]$Candidates)
    foreach ($path in $Candidates) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }
    return $null
}

$chrome = Find-Browser "Chrome" @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe"
)

$edge = Find-Browser "Edge" @(
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)

$browserArgs = @("--new-window", "--new-instance") + $Urls

if ($chrome) {
    Start-Process -FilePath $chrome -ArgumentList $browserArgs
    exit 0
}

if ($edge) {
    Start-Process -FilePath $edge -ArgumentList $browserArgs
    exit 0
}

foreach ($url in $Urls) {
    Start-Process $url
}

exit 0
