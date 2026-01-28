#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import sys
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic"}

def get_app_dir() -> Path:
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

def get_app_resources() -> Path:
    # PyInstaller: _MEIPASS; py2app: ../Resources relative to executable
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        exec_dir = Path(sys.executable).resolve().parent
        resources = exec_dir.parent / "Resources"
        if resources.exists():
            return resources
    return get_app_dir()

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
    """ Busca exiftool incluido en Resources (dentro del .app) o en rutas mac comunes,
    o en PATH. """
    candidates: list[Path] = []

    resources = get_app_resources()
    candidates.append(resources)

    # Rutas comunes de Homebrew (Apple Silicon / Intel)
    candidates.append(Path("/opt/homebrew/bin"))
    candidates.append(Path("/usr/local/bin"))
    candidates.append(Path.cwd())
    candidates.append(get_app_dir())

    for base in candidates:
        for name in ("exiftool", "exiftool.exe"):
            p = base / name
            if p.exists() and os.access(p, os.X_OK):
                return base

    # fallback: exiftool en PATH
    p = shutil.which("exiftool") or shutil.which("exiftool.exe")
    if p:
        return Path(p).parent

    return None

def build_exiftool_command() -> tuple[list[str] | None, Path | None, dict[str, str] | None]:
    home = find_exiftool_home()
    if home:
        for name in ("exiftool", "exiftool.exe"):
            exe = home / name
            if exe.exists() and os.access(exe, os.X_OK):
                return ([str(exe)], home, None)
    return (None, None, None)

def strip_metadata_exiftool(p: Path):
    cmd, cwd, env = build_exiftool_command()
    if not cmd:
        raise FileNotFoundError("No se encontró ExifTool")
    subprocess.run([*cmd, "-all=", "-overwrite_original", str(p)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
                   cwd=str(cwd) if cwd else None, env=env)

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

        tk.Button(root, text="Seleccionar imágenes", width=30, command=self.pick_images).pack(pady=6)
        tk.Button(root, text="Seleccionar carpeta", width=30, command=self.pick_folder).pack(pady=6)
        tk.Button(root, text="Limpiar metadatos", width=30, command=self.clean).pack(pady=10)

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
                "La aplicación debería incluirlo, pero no fue posible localizarlo.\n"
                "Si estás desarrollando, instala exiftool (brew install exiftool) o incluye el binario en Resources.",
            )
            return
        try:
            epoch = time.time()
            out_dir = get_app_dir() / "imagenes_limpias"
            out_dir.mkdir(parents=True, exist_ok=True)
            count = 0
            for img in iter_images(self.selected):
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

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()