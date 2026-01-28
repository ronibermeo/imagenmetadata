#!/usr/bin/env bash
set -euo pipefail

echo "== Build eliminar_metadata (macOS, onefile, sin consola) =="

if [[ ! -f "./exiftool" ]]; then
  echo ""
  echo "FALTA ./exiftool en esta carpeta."
  echo "En macOS, necesitas el binario 'exiftool' (sin .exe) para poder incluirlo dentro del .app/.exe generado."
  echo "Colócalo aquí con el nombre exacto: exiftool"
  echo ""
  exit 1
fi

python3 -m pip install --upgrade pyinstaller >/dev/null

rm -rf ./dist_final_mac ./build_final_mac || true

pyinstaller \
  --onefile \
  --windowed \
  --clean \
  --distpath dist_final_mac \
  --workpath build_final_mac \
  --add-binary "exiftool:." \
  eliminar_metadata.py

cp -f ./README_USO.txt ./dist_final_mac/README_USO.txt

echo ""
echo "LISTO: dist_final_mac/eliminar_metadata"
echo "Ese binario YA incluye ExifTool. Puedes renombrarlo o envolverlo en .app/.dmg si quieres."

