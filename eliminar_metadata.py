import os, time, subprocess, sys, shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic"}

def strip_metadata_exiftool(p: Path):
    cmd, cwd, env = build_exiftool_command()
    if not cmd:
        raise FileNotFoundError("No se encontró ExifTool")
    # Silencia salida normal; deja stderr para errores.
    subprocess.run([*cmd, "-all=", "-overwrite_original", str(p)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
                   cwd=str(cwd) if cwd else None, env=env)

def get_app_dir() -> Path:
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

def unique_dest(dir_path: Path, filename: str) -> Path:
    dest = dir_path / filename
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        candidate = dir_path / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def find_exiftool_home() -> Path | None:
    """
    Devuelve la carpeta que contiene `exiftool_files/` si existe (en MEIPASS o junto al ejecutable/script).
    """
    candidates: list[Path] = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.append(Path(getattr(sys, "_MEIPASS")))
    candidates.append(get_app_dir())
    candidates.append(Path.cwd())

    for base in candidates:
        if (base / "exiftool_files").is_dir():
            return base
    return None

def build_exiftool_command() -> tuple[list[str] | None, Path | None, dict[str, str] | None]:
    """
    Construye el comando más robusto posible.

    Preferimos ejecutar: perl.exe -I <exiftool_files/lib> <exiftool_files/exiftool.pl>
    porque el launcher exiftool.exe puede fallar si el runtime Perl no queda bien resuelto.
    """
    home = find_exiftool_home()
    if home:
        exif_dir = home / "exiftool_files"
        perl = exif_dir / "perl.exe"
        script = exif_dir / "exiftool.pl"
        lib_dir = exif_dir / "lib"
        if perl.exists() and script.exists() and lib_dir.is_dir():
            # Asegura que Perl encuentre los módulos (strict.pm, etc) desde el arranque.
            env = os.environ.copy()
            env["PERL5LIB"] = str(lib_dir)
            return ([str(perl), "-I", str(lib_dir), str(script)], exif_dir, env)

    # Fallback: si el usuario instaló exiftool en PATH
    p = shutil.which("exiftool") or shutil.which("exiftool.exe")
    if p:
        return ([p], Path(p).parent, None)

    return (None, None, None)

def set_file_times(p: Path, epoch: float):
    os.utime(p, (epoch, epoch))

def iter_images(paths):
    for path in paths:
        p = Path(path)
        if p.is_file() and p.suffix.lower() in EXTS:
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in EXTS:
                    yield f

class App:
    def __init__(self, root):
        self.root = root
        root.title("Limpiador de metadatos")

        self.selected = []

        tk.Button(root, text="Seleccionar imágenes", width=25, command=self.pick_images).pack(pady=6)
        tk.Button(root, text="Seleccionar carpeta", width=25, command=self.pick_folder).pack(pady=6)
        tk.Button(root, text="Limpiar metadatos", width=25, command=self.clean).pack(pady=10)

        self.label = tk.Label(root, text="0 elementos seleccionados")
        self.label.pack(pady=6)

    def pick_images(self):
        files = filedialog.askopenfilenames(title="Elige imágenes")
        if files:
            self.selected = list(files)
            self.label.config(text=f"{len(self.selected)} archivo(s) seleccionado(s)")

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Elige una carpeta")
        if folder:
            self.selected = [folder]
            self.label.config(text=f"Carpeta seleccionada: {folder}")

    def clean(self):
        if not self.selected:
            messagebox.showwarning("Nada seleccionado", "Selecciona imágenes o una carpeta primero.")
            return
        if not build_exiftool_command()[0]:
            messagebox.showerror(
                "Falta ExifTool",
                "No se encontró ExifTool.\n\n"
                "Si usas el ejecutable 'final', esto NO debería pasar.\n"
                "Vuelve a descargar el .exe que incluye ExifTool o contacta a quien te lo pasó.",
            )
            return
        try:
            epoch = time.time()
            out_dir = get_app_dir() / "imagenes_limpias"
            out_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for img in iter_images(self.selected):
                # Copia a la carpeta junto al .exe (no toca el original)
                dest = unique_dest(out_dir, img.name)
                shutil.copy2(img, dest)
                strip_metadata_exiftool(dest)
                set_file_times(dest, epoch)
                count += 1
            messagebox.showinfo("Listo", f"Se limpiaron {count} imagen(es).\n\nGuardadas en:\n{out_dir}")
        except subprocess.CalledProcessError as e:
            msg = (e.stderr or "").strip() or str(e)
            messagebox.showerror("Error de ExifTool", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = tk.Tk()
App(root)
root.mainloop()
