# Compila o projeto e copia o executável para a área de trabalho (PowerShell)
$pyinstaller = "pyinstaller"
$nomeExe = "My IBGE AutoClicker.exe"
$icone = "icon.ico"
$main = "main.py"

# Compilar
& $pyinstaller --onefile --name "My IBGE AutoClicker" --icon $icone $main

# Caminhos
$distPath = Join-Path $PSScriptRoot "dist"
$exeOrigem = Join-Path $distPath $nomeExe
$desktop = [Environment]::GetFolderPath("Desktop")
$exeDestino = Join-Path $desktop $nomeExe

# Copiar para a área de trabalho
if (Test-Path $exeOrigem) {
    Copy-Item $exeOrigem $exeDestino -Force
    Write-Host "[SUCESSO] Compilação finalizada. O executável está em 'dist' e na área de trabalho." -ForegroundColor Green
} else {
    Write-Host "[ERRO] Não foi possível encontrar o executável em 'dist'." -ForegroundColor Red
}
