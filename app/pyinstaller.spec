# -*- mode: python ; coding: utf-8 -*-

import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy_deps import sdl2, angle
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['main.py'],
    pathex = [os.path.abspath('.')],
    datas=[('arc', 'arc')],
    hookspath = [kivymd_hooks_path],
    win_no_prefer_redirects = False,
    win_private_assemblies = False,
    cipher = None,
    noarchive = False,
    excludes=['*.ini', '*.json']
)
a.binaries = TOC([x for x in a.binaries if x[0] not in ['sqlite3.dll', 'tcl85.dll', 'tk85.dll', '_sqlite3', '_ssl', '_tkinter', 'VCRUNTIME140.dll', 'msvcp140.dll', 'mfc140u.dll']])
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher = None
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + angle.dep_bins)],
    name = 'Kynvi',
    debug = False,
    strip = False,
    upx = True,
    console = False,
    icon='arc\\img\\icon.ico',
    version='version.txt'
)