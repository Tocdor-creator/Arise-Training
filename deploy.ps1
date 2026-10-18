# Envia o ARISE para o servidor caseiro (Termux no celular via Tailscale) e reinicia.
# Uso: powershell -File deploy.ps1
$ErrorActionPreference = "Stop"
$HostIp = "100.98.189.36"
$Port = 8022
$Remote = "arise-training"
Set-Location $PSScriptRoot

$files = @("app.py", "game.py", "exercises.py", "requirements.txt", "servidor.sh", "README.md", "static", "data")
tar -czf "$env:TEMP\arise.tgz" @files
scp -P $Port "$env:TEMP\arise.tgz" "${HostIp}:arise.tgz"
ssh -p $Port $HostIp "mkdir -p ~/$Remote && tar -xzf ~/arise.tgz -C ~/$Remote && rm ~/arise.tgz && sh ~/$Remote/servidor.sh reiniciar"
Write-Host "Pronto: http://${HostIp}:5050"
