from cx_Freeze import setup, Executable
import os
import sys

os.environ['TCL_LIBRARY'] = 'D:\\code\\anaconda\\tcl\\tcl8\\8.6'
os.environ['TK_LIBRARY'] = 'D:\\code\\anaconda\\tcl\\tK8.6'
path_platforms = ("D:\\code\\anaconda\\pkgs\\qt-5.9.7-vc14h73c81de_0\\Library\\plugins\\platforms\\qwindows.dll",
                  "platforms\\qwindows.dll")
includes = ["atexit", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
           "numpy", "numpy.core._methods", "pandas", "csv", "sqlite3"]
includefiles = [path_platforms]
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses',
            'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
            'tcl','TKconstants', 'TKinter']
packages = ["os", "numpy.lib.format"]
path = []

build_exe_options = {
                     "includes":      includes,
                     "include_files": includefiles,
                     "excludes":      excludes,
                     "packages":      packages,
                     "path":          path
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
exe = None

if sys.platform == "win32":
    exe = Executable(
      script="d:\\code\\egovexport\\code\\egovexport.py",
      initScript = None,
      base="Win32GUI",
      targetName="egovexport.exe",
      icon = None
    )

setup(
      name = "egovexport",
      version = "0.1",
      author = 'me',
      description = "egovexport",
      options = {"build_exe": build_exe_options},
      executables = [exe]
)
