#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def _prepend_path(path: Path) -> None:
    if path.is_dir():
        os.environ["PATH"] = str(path) + os.pathsep + os.environ.get("PATH", "")


def _candidate_roots() -> list[Path]:
    roots: list[Path] = []
    # Source mode
    roots.append(Path(__file__).resolve().parent)
    # Frozen mode (PyInstaller)
    if getattr(sys, "frozen", False):
        roots.append(Path(sys.executable).resolve().parent)
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            roots.append(Path(meipass))
            roots.append(Path(meipass).parent)
    return roots


def _configure_runtime_path() -> None:
    seen: set[Path] = set()
    for root in _candidate_roots():
        if root in seen:
            continue
        seen.add(root)

        # Ensure bundled ffmpeg/ffprobe can be found.
        _prepend_path(root)
        _prepend_path(root / "_internal")

        # PyInstaller onedir layout and source-mode venv fallback.
        _prepend_path(root / "torch" / "lib")
        _prepend_path(root / "_internal" / "torch" / "lib")
        _prepend_path(root / "onnxruntime" / "capi")
        _prepend_path(root / "_internal" / "onnxruntime" / "capi")
        _prepend_path(root / "venv" / "Lib" / "site-packages" / "torch" / "lib")
        _prepend_path(root / "venv" / "Lib" / "site-packages" / "onnxruntime" / "capi")

        nvidia_dir = root / "venv" / "Lib" / "site-packages" / "nvidia"
        if nvidia_dir.is_dir():
            for pkg in nvidia_dir.iterdir():
                _prepend_path(pkg / "bin")


_configure_runtime_path()

# Import the tkinter fix to patch the ScreenChanged error
import tkinter_fix

from modules import core

if __name__ == '__main__':
    core.run()
