param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Urls,

    [switch]$UpdateSession
)

if (-not $Urls -or $Urls.Count -eq 0) {
    Write-Error "No URLs provided."
    exit 1
}

$browserProfileDir = Join-Path $env:LOCALAPPDATA "AgentSmith-Trace\browser-profile"
New-Item -ItemType Directory -Force -Path $browserProfileDir | Out-Null

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

$browserArgs = @(
    "--user-data-dir=$browserProfileDir",
    "--new-window",
    "--new-instance"
) + $Urls

$browserProc = $null

if ($chrome) {
    $browserProc = Start-Process -FilePath $chrome -ArgumentList $browserArgs -PassThru
}

if (-not $browserProc -and $edge) {
    $browserProc = Start-Process -FilePath $edge -ArgumentList $browserArgs -PassThru
}

if ($browserProc -and $UpdateSession) {
    $sessionScript = Join-Path $PSScriptRoot "run-session.ps1"
    & $sessionScript -Action UpdateBrowser -BrowserPid $browserProc.Id
}

if ($browserProc) {
    exit 0
}

foreach ($url in $Urls) {
    Start-Process $url
}

exit 0
