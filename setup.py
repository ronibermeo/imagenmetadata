from setuptools import setup

APP = ['eliminar_metadata.py']
DATA_FILES = ['exiftool']  # Si existe, será incluido en Contents/Resources/
OPTIONS = {
    'argv_emulation': False,
    'packages': [],
    'includes': [],
    'resources': DATA_FILES,
    'optimize': 0,
    # 'iconfile': 'icon.icns',  # descomenta y añade icon.icns si tienes icono
}

setup(
    app=APP,
    name='LimpiadorMetadatos',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)