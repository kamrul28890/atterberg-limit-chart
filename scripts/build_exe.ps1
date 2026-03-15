$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $env:PYTHONPATH = 'src'
    .\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name AtterbergLimitChart --paths src src\main.py
}
finally {
    Pop-Location
}
