CREAR UN .EXE "TODO EN UNO" (para compartir a gente no técnica)
===============================================================

Objetivo: generar un solo archivo:
  dist_final\eliminar_metadata.exe
que funcione sin instalar Python ni ExifTool.

PASOS
-----
1) Descarga ExifTool para Windows y obtén el archivo "exiftool.exe".
2) Copia "exiftool.exe" en esta misma carpeta (junto a eliminar_metadata.py).
3) Ejecuta:
   - Clic derecho en la carpeta -> "Abrir en Terminal" (PowerShell)
   - Luego:
     .\build.ps1

RESULTADO
---------
- Comparte SOLO este archivo con la otra persona:
  dist_final\eliminar_metadata.exe

NOTA
----
ExifTool es un programa de terceros. Revisa su licencia/términos si planeas redistribuirlo.

