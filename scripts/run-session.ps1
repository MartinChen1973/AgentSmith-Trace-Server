param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Cleanup", "StartServer", "UpdateBrowser", "WriteSession")]
    [string]$Action,

    [string]$ProjectRoot = "",
    [int]$Port = 9000,
    [string]$Reload = "1",
    [int]$ServerPid = 0,
    [int]$BrowserPid = 0,
    [string]$HomeUrl = ""
)

$ErrorActionPreference = "SilentlyContinue"

$WindowTitle = "AgentSmith-Trace Server"
$SessionFileName = ".agentsmith-trace-run.json"
$BrowserProfileRelative = "AgentSmith-Trace\browser-profile"

function Get-ProjectRoot {
    if ($ProjectRoot) {
        return (Resolve-Path -LiteralPath $ProjectRoot).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Get-SessionPath {
    param([string]$Root)
    return Join-Path $Root $SessionFileName
}

function Get-BrowserProfileDir {
    return Join-Path $env:LOCALAPPDATA $BrowserProfileRelative
}

function Get-RunSession {
    param([string]$Root)
    $path = Get-SessionPath -Root $Root
    if (-not (Test-Path -LiteralPath $path)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Save-RunSession {
    param(
        [string]$Root,
        [hashtable]$Data
    )
    $path = Get-SessionPath -Root $Root
    $payload = [ordered]@{
        serverWindowPid   = [int]$Data.serverWindowPid
        browserPid        = [int]$Data.browserPid
        port              = [int]$Data.port
        homeUrl           = [string]$Data.homeUrl
        windowTitle       = $WindowTitle
        browserProfileDir = [string]$Data.browserProfileDir
        startedAt         = [string]$Data.startedAt
    }
    $payload | ConvertTo-Json | Set-Content -LiteralPath $path -Encoding UTF8
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    if ($ProcessId -le 0) {
        return
    }
    $alive = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $alive) {
        return
    }
    & taskkill.exe /PID $ProcessId /T /F | Out-Null
}

function Stop-ServerWindows {
    Get-Process -Name "cmd" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.MainWindowTitle -eq $WindowTitle) {
            Write-Host ("Closing server window PID {0}" -f $_.Id)
            Stop-ProcessTree -ProcessId $_.Id
        }
    }
}

function Stop-BrowserByProfile {
    param([string]$ProfileDir)
    if (-not $ProfileDir) {
        $ProfileDir = Get-BrowserProfileDir
    }
    foreach ($browserName in @("chrome.exe", "msedge.exe")) {
        Get-CimInstance Win32_Process -Filter "Name = '$browserName'" |
            Where-Object { $_.CommandLine -and $_.CommandLine -like "*$ProfileDir*" } |
            ForEach-Object {
                Write-Host ("Closing {0} PID {1} (AgentSmith profile)" -f $browserName, $_.ProcessId)
                Stop-ProcessTree -ProcessId $_.ProcessId
            }
    }
}

function Invoke-Cleanup {
    param([string]$Root)
    $session = Get-RunSession -Root $Root
    if ($session) {
        if ($session.serverWindowPid) {
            Write-Host ("Stopping previous server window PID {0}" -f $session.serverWindowPid)
            Stop-ProcessTree -ProcessId ([int]$session.serverWindowPid)
        }
        if ($session.browserPid) {
            Write-Host ("Stopping previous browser PID {0}" -f $session.browserPid)
            Stop-ProcessTree -ProcessId ([int]$session.browserPid)
        }
        $profileDir = [string]$session.browserProfileDir
        if ($profileDir) {
            Stop-BrowserByProfile -ProfileDir $profileDir
        }
    }

    Stop-ServerWindows
    Stop-BrowserByProfile -ProfileDir (Get-BrowserProfileDir)

    $path = Get-SessionPath -Root $Root
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

function Start-ServerWindow {
    param(
        [string]$Root,
        [int]$ListenPort,
        [string]$ReloadFlag
    )
    $startScript = Join-Path $Root "scripts\start-server.cmd"
    $cmdLine = "title $WindowTitle & set AGENTSMITH_TRACE_PORT=$ListenPort & set AGENTSMITH_TRACE_RELOAD=$ReloadFlag & call `"$startScript`""
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/K", $cmdLine -WorkingDirectory $Root -PassThru
    Write-Output $proc.Id
}

function Update-BrowserPid {
    param(
        [string]$Root,
        [int]$Pid
    )
    $session = Get-RunSession -Root $Root
    if (-not $session) {
        return
    }
    $data = @{
        serverWindowPid   = [int]$session.serverWindowPid
        browserPid        = $Pid
        port              = [int]$session.port
        homeUrl           = [string]$session.homeUrl
        browserProfileDir = [string]$session.browserProfileDir
        startedAt         = [string]$session.startedAt
    }
    Save-RunSession -Root $Root -Data $data
}

function Write-NewSession {
    param(
        [string]$Root,
        [int]$ServerWindowPid,
        [int]$BrowserProcessPid,
        [int]$ListenPort,
        [string]$Url
    )
    $data = @{
        serverWindowPid   = $ServerWindowPid
        browserPid        = $BrowserProcessPid
        port              = $ListenPort
        homeUrl           = $Url
        browserProfileDir = Get-BrowserProfileDir
        startedAt         = (Get-Date).ToUniversalTime().ToString("o")
    }
    Save-RunSession -Root $Root -Data $data
}

$root = Get-ProjectRoot

switch ($Action) {
    "Cleanup" {
        Invoke-Cleanup -Root $root
        exit 0
    }
    "StartServer" {
        $id = Start-ServerWindow -Root $root -ListenPort $Port -ReloadFlag $Reload
        Write-Output $id
        exit 0
    }
    "UpdateBrowser" {
        Update-BrowserPid -Root $root -Pid $BrowserPid
        exit 0
    }
    "WriteSession" {
        Write-NewSession -Root $root -ServerWindowPid $ServerPid -BrowserProcessPid $BrowserPid -ListenPort $Port -Url $HomeUrl
        exit 0
    }
}
