# Instrucciones para construir la app macOS (py2app)

Estos pasos permiten generar `LimpiadorMetadatos.app` empaquetando tu script con `py2app` y incluyendo `exiftool` en los recursos.

Requisitos (en tu Mac de desarrollo):
- macOS con Python 3 (preferiblemente instalador oficial para asegurarte de que Tkinter esté presente)
- Homebrew (opcional, para instalar exiftool)
- Cuenta Apple Developer (solo si vas a firmar/notarizar; no es necesario para probar localmente)

Pasos rápidos (local):
1. Copia el binario exiftool al repo (si quieres incluirlo localmente):
   - brew install exiftool
   - cp $(which exiftool) ./exiftool
   - chmod +x ./exiftool

2. Ejecuta:
   - chmod +x build_app.sh
   - ./build_app.sh

3. Resultado:
   - dist/LimpiadorMetadatos.app

Firmar y notarizar (opcional, recomendado para distribución):
- Para distribuir sin advertencias Gatekeeper la app debe estar firmada y notarizada con una cuenta Apple Developer.
- Este paso NO se realiza en el workflow por defecto.

Notas:
- El workflow de GitHub Actions `build-macos-app.yml` compila en un runner macOS y sube el .app como artefacto ZIP.
- Incluir el binario exiftool en el repositorio puede no ser deseable por tamaño/licencia; el workflow instala exiftool con Homebrew durante la compilación y lo copia al bundle.

Probar la app en macOS:
- Descarga el artefacto LimpiadorMetadatos.app.zip desde Actions → run → Artifacts
- Descomprime y ejecuta `open LimpiadorMetadatos.app`. macOS puede mostrar advertencias si la app no está firmada; eso es esperado.

Si quieres firmar y notarizar en CI, puedo indicar los secretos y pasos necesarios.