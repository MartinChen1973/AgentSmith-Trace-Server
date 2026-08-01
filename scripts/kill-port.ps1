param(
    [Parameter(Mandatory = $true)]
    [int]$Port
)

$ErrorActionPreference = "SilentlyContinue"

function Get-ListeningPids {
    param([int]$ListenPort)
    $ids = New-Object System.Collections.Generic.HashSet[int]
    netstat -ano | ForEach-Object {
        $line = $_
        if ($line -notmatch "LISTENING") { return }
        if ($line -notmatch ":$ListenPort\s") { return }
        if ($line -match "\s+(\d+)\s*$") {
            [void]$ids.Add([int]$Matches[1])
        }
    }
    return @($ids)
}

function Test-PortExclusive {
    param([int]$ListenPort)
    $code = @"
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    s.bind(('127.0.0.1', $ListenPort))
    s.close()
    raise SystemExit(0)
except OSError:
    raise SystemExit(1)
"@
    $python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        $python = "python"
    }
    & $python -c $code
    return ($LASTEXITCODE -eq 0)
}

$pids = Get-ListeningPids -ListenPort $Port
foreach ($procId in $pids) {
    if ($procId -le 0) { continue }
    $alive = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($alive) {
        Write-Host ("Stopping listener PID {0}" -f $procId)
        & taskkill.exe /PID $procId /T /F | Out-Null
    } else {
        Write-Host ("Stale netstat PID {0} on port {1} (no process)" -f $procId, $Port)
    }
}

if ($pids.Count -gt 0) {
    Start-Sleep -Seconds 1
}

if (Test-PortExclusive -ListenPort $Port) {
    Write-Host "Port $Port is usable."
    exit 0
}

Write-Host "Port $Port is stuck (zombie listener). Prefer a free alternate port."
exit 2
