$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$basePython = Get-Command python -ErrorAction Stop
$machine = & $basePython.Source -c 'import struct; print(struct.calcsize(chr(80)) * 8)'
if ($LASTEXITCODE -ne 0 -or $machine.Trim() -ne '64') { throw 'Use Python de 64 bits para compilar o aplicativo Windows x64.' }

$venv = Join-Path $root '.venv'
$python = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $basePython.Source -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o ambiente virtual de build.' }
}

& $python -m pip install --disable-pip-version-check -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível instalar as dependências de build.' }
& $python -m PyInstaller --noconfirm --clean --windowed --name 'PDF para Markdown' --collect-all pymupdf4llm --collect-all pymupdf app.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller não conseguiu gerar o executável.' }

$exe = Join-Path $root 'dist\PDF para Markdown\PDF para Markdown.exe'
if (-not (Test-Path -LiteralPath $exe)) { throw "Executável não encontrado: $exe" }
Get-Item -LiteralPath $exe | Select-Object FullName, Length
Write-Host 'Build concluído. Compile installer\PDF-para-Markdown.iss no Inno Setup 6 para gerar o instalador.'
