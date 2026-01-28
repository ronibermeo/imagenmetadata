$ErrorActionPreference = "Stop"

Write-Host "== Build eliminar_metadata.exe (onefile, sin consola) ==" -ForegroundColor Cyan

if (-not (Test-Path ".\exiftool.exe")) {
  Write-Host ""
  Write-Host "FALTA exiftool.exe en esta carpeta." -ForegroundColor Yellow
  Write-Host "Para crear UN SOLO .exe que funcione sin instalaciones, necesitas exiftool.exe (una sola vez, solo para compilar)." -ForegroundColor Yellow
  Write-Host "Descárgalo desde la web oficial de ExifTool y colócalo aquí como: exiftool.exe" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "Luego ejecuta de nuevo este script." -ForegroundColor Yellow
  exit 1
}

if (-not (Test-Path ".\exiftool_files")) {
  Write-Host ""
  Write-Host "FALTA la carpeta exiftool_files en esta carpeta." -ForegroundColor Yellow
  Write-Host "ExifTool para Windows necesita esa carpeta (dlls/perl) para funcionar." -ForegroundColor Yellow
  Write-Host "Cópiala junto a este script como: .\exiftool_files\" -ForegroundColor Yellow
  Write-Host ""
  exit 1
}

python -m pip install --upgrade pyinstaller | Out-Null

$dist = ".\dist_final"
$work = ".\build_final"
try {
  if (Test-Path $dist) { Remove-Item -Recurse -Force $dist }
  if (Test-Path $work) { Remove-Item -Recurse -Force $work }
} catch {
  # Si el exe anterior está abierto, Windows bloquea el borrado.
  $dist = ".\dist_final_v2"
  $work = ".\build_final_v2"
  if (Test-Path $dist) { Remove-Item -Recurse -Force $dist }
  if (Test-Path $work) { Remove-Item -Recurse -Force $work }
}

pyinstaller `
  --onefile `
  --noconsole `
  --clean `
  --distpath $dist `
  --workpath $work `
  --add-binary "exiftool.exe;." `
  --add-data "exiftool_files;exiftool_files" `
  eliminar_metadata.py

Copy-Item -Force .\README_USO.txt (Join-Path $dist "README_USO.txt")

Write-Host ""
Write-Host ("LISTO: " + (Join-Path $dist "eliminar_metadata.exe")) -ForegroundColor Green
Write-Host "Ese .exe YA incluye ExifTool: el usuario final solo hace doble clic y funciona." -ForegroundColor Green

