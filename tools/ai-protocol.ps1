<#
.SYNOPSIS
    Wrapper PowerShell para el runtime CLI de AI Workspace Protocol (AIWP).
.DESCRIPTION
    Invoca tools/ai_protocol.py usando el intérprete de Python disponible en el sistema.
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "ai_protocol.py"

if (-not (Test-Path -LiteralPath $PythonScript)) {
    Write-Error "No se encontró el script Python: $PythonScript"
    exit 1
}

$PythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonExe) {
    Write-Error "No se encontró el ejecutable 'python' en el PATH del sistema."
    exit 1
}

& python $PythonScript @ScriptArgs
exit $LASTEXITCODE
