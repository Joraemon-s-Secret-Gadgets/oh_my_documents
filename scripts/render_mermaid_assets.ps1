$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$env:npm_config_cache = Join-Path $root ".npm-cache"
$config = Join-Path $PSScriptRoot "mermaid-puppeteer-config.json"
$sourceDir = Join-Path $root "assets\images\mermaid"

Get-ChildItem -Path $sourceDir -Filter "*.mmd" | Sort-Object Name | ForEach-Object {
    $output = [System.IO.Path]::ChangeExtension($_.FullName, ".png")
    Write-Host "render $($_.Name)"
    npx -y @mermaid-js/mermaid-cli -i $_.FullName -o $output -b white -s 2 -p $config
}
