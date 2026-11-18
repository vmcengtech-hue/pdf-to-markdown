$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$appExe = Join-Path $root 'dist\PDF para Markdown\PDF para Markdown.exe'
if (-not (Test-Path -LiteralPath $appExe)) {
    throw "O executável não existe. Rode build.ps1 primeiro: $appExe"
}

$candidates = @(
    (Join-Path ${env:LOCALAPPDATA} 'Programs\Inno Setup 6\ISCC.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe')
)
$compiler = Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
if (-not $compiler) {
    $compiler = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $compiler) { throw 'Inno Setup 6 não encontrado. Instale-o para compilar o instalador.' }

$output = Join-Path $root 'dist-installer'
New-Item -ItemType Directory -Force -Path $output | Out-Null
& $compiler "/O$output" (Join-Path $root 'installer\PDF-para-Markdown.iss')
if ($LASTEXITCODE -ne 0) { throw 'Inno Setup não conseguiu compilar o instalador.' }

Get-ChildItem -LiteralPath $output -Filter '*.exe' -File | Select-Object FullName, Length
