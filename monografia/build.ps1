# Gera monografia/TCC2.pdf com o MiKTeX local (latexmk + pdflatex + bibtex).
#   .\build.ps1          compila (incremental)
#   .\build.ps1 -Clean   apaga build/ e o PDF antes de compilar
param([switch]$Clean)

# Sem ErrorActionPreference=Stop: o latexmk escreve mensagens informativas no
# stderr, e o PowerShell 5.1 as trataria como erro fatal. O resultado vale pelo
# codigo de saida.
Set-Location $PSScriptRoot

if ($Clean) {
    Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
    Remove-Item -Force TCC2.pdf -ErrorAction SilentlyContinue
}

latexmk
$codigo = $LASTEXITCODE

if (Test-Path build/tcc.pdf) {
    Copy-Item build/tcc.pdf TCC2.pdf -Force
}

$avisos = Select-String -Path build/tcc.log -Pattern 'undefined on input line' -ErrorAction SilentlyContinue
if ($avisos) {
    Write-Warning "$($avisos.Count) referencias/citacoes indefinidas (veja build/tcc.log)"
}

if ($codigo -ne 0) {
    Write-Error "latexmk terminou com codigo $codigo (veja build/tcc.log)"
}
Write-Host "PDF gerado: $PSScriptRoot\TCC2.pdf"
