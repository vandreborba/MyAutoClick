# Atualiza automaticamente o valor de VERSAO_SISTEMA em config_interface.py
$configInterface = Join-Path $PSScriptRoot 'automacoes/config_interface.py'
if (Test-Path $configInterface) {
    $linhas = Get-Content $configInterface
    $novaVersao = $null
    $linhasAtualizadas = $linhas | ForEach-Object {
        if ($_ -match 'VERSAO_SISTEMA\s*=\s*"([0-9]+)\.([0-9]+)"') {
            $major = [int]$matches[1]
            $minor = [int]$matches[2] + 1
            $novaVersao = "$major.$minor"
            "VERSAO_SISTEMA = `"$novaVersao`""
        } else {
            $_
        }
    }
    if ($novaVersao) {
        Set-Content -Path $configInterface -Value $linhasAtualizadas -Encoding UTF8
        Write-Host "[INFO] VERSAO_SISTEMA atualizada para $novaVersao em config_interface.py." -ForegroundColor Yellow
    } else {
        Write-Host "[AVISO] Não foi possível localizar a linha de versão em config_interface.py." -ForegroundColor Yellow
    }
}

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
