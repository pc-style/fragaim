from __future__ import annotations

# SPDX-License-Identifier: GPL-3.0-or-later
"""
A minimal PySide6 based GUI for Unibot.

The goal of this module is not to expose every single configuration option –
that would take an enormous amount of time and clutter the interface – but to
cover the most frequently-used ones in a clean, modern looking window inspired
by the screenshots the user provided.

The class hierarchy is intentionally simple so that the file is easy to modify
by anyone who wants to extend the UI:

* ConfigController – thin wrapper around ``ConfigReader`` with helpers to read
  and persist values.
* MainWindow – the Qt *QMainWindow* that contains the navigation list on the
  left and a *QStackedWidget* on the right.
* CategoryPage subclasses – one page per logical feature set (Aim, Recoil, …)
  each exposing a handful of widgets bound to corresponding keys in the
  INI file.

A *Run / Stop* button is provided to start the existing **main.py** loop inside
its own :class:`threading.Thread` so the GUI stays responsive.

This file purposefully avoids any 3rd party Qt styling libraries, instead it
ships a small dark palette and a couple of stylesheet rules so the end result
matches the dark, flat aesthetic from the reference pictures while keeping the
number of external dependencies low (only ``PySide6``).

"""

import os
import sys
import threading
import subprocess
from pathlib import Path
from typing import Tuple

from configparser import ConfigParser

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Helper / Controller
# ---------------------------------------------------------------------------


class ConfigController:
    """Wraps reading + writing of *config.ini*."""

    CONFIG_PATH = Path(__file__).parent.parent / "config.ini"

    def __init__(self) -> None:
        self.parser = ConfigParser()
        self.read()

    # ------------------------------------------------------------------ IO --

    def read(self) -> None:
        self.parser.read(self.CONFIG_PATH, encoding="utf-8")

    def save(self) -> None:
        with self.CONFIG_PATH.open("w", encoding="utf-8") as fp:
            self.parser.write(fp)

    # --------------------------------------------------------- Convenience --

    def get_float(self, section: str, key: str) -> float:
        return self.parser.getfloat(section, key)

    def set_float(self, section: str, key: str, value: float) -> None:
        self.parser.set(section, key, f"{value}")

    def get_int(self, section: str, key: str) -> int:
        return self.parser.getint(section, key)

    def set_int(self, section: str, key: str, value: int) -> None:
        self.parser.set(section, key, str(value))

    def get_bool(self, section: str, key: str) -> bool:
        return self.parser.getboolean(section, key)

    def set_bool(self, section: str, key: str, value: bool) -> None:
        self.parser.set(section, key, "true" if value else "false")

    def get_color(self, section: str, key: str) -> Tuple[int, int, int]:
        raw = self.parser.get(section, key)
        r, g, b = [int(x.strip()) for x in raw.split(",")]
        return r, g, b

    def set_color(self, section: str, key: str, value: Tuple[int, int, int]) -> None:
        r, g, b = value
        self.parser.set(section, key, f"{r}, {g}, {b}")


# ---------------------------------------------------------------------------
# Qt Pages
# ---------------------------------------------------------------------------


class AimPage(QWidget):
    """Controls for [aim] section."""

    def __init__(self, cfg: ConfigController):
        super().__init__()
        self.cfg = cfg

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Smooth ----------------------------------------------------------------
        smooth_label = QLabel("Smooth")
        self.smooth_slider = QSlider(Qt.Horizontal)
        self.smooth_slider.setRange(0, 100)
        self.smooth_slider.setSingleStep(1)
        # value in ini: 0..1 – map to 0..100
        smooth_val = int(self.cfg.get_float("aim", "smooth") * 100)
        self.smooth_slider.setValue(smooth_val)
        self.smooth_slider.valueChanged.connect(self._smooth_changed)

        layout.addWidget(smooth_label)
        layout.addWidget(self.smooth_slider)

        # Speed ------------------------------------------------------------------
        speed_label = QLabel("Base speed")
        self.speed_spin = QDoubleSpinBox(0.0, 1.0, 0.01, cfg.get_float("aim", "speed"))
        self.speed_spin.valueChanged.connect(lambda _v: self.cfg.set_float("aim", "speed", self.speed_spin.value()))
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_spin)

        # Anti shake -------------------------------------------------------------
        self.anti_cb = QCheckBox("Enable anti-shake")
        self.anti_cb.setChecked(self.cfg.get_bool("aim", "enable_anti_shake"))
        self.anti_cb.toggled.connect(lambda v: self.cfg.set_bool("aim", "enable_anti_shake", v))
        layout.addWidget(self.anti_cb)

        layout.addStretch(1)

    # ------------------------------------------------------------------ slots --

    @Slot(int)
    def _smooth_changed(self, val: int) -> None:
        self.cfg.set_float("aim", "smooth", val / 100.0)


class RecoilPage(QWidget):
    def __init__(self, cfg: ConfigController):
        super().__init__()
        self.cfg = cfg

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Recoil X ---------------------------------------------------------------
        rx_label = QLabel("Recoil X")
        self.rx_spin = QDoubleSpinBox(-2.0, 2.0, 0.05, cfg.get_float("recoil", "recoil_x"))
        self.rx_spin.valueChanged.connect(lambda _v: self.cfg.set_float("recoil", "recoil_x", self.rx_spin.value()))
        layout.addWidget(rx_label)
        layout.addWidget(self.rx_spin)

        # Recoil Y ---------------------------------------------------------------
        ry_label = QLabel("Recoil Y")
        self.ry_spin = QDoubleSpinBox(-2.0, 2.0, 0.05, cfg.get_float("recoil", "recoil_y"))
        self.ry_spin.valueChanged.connect(lambda _v: self.cfg.set_float("recoil", "recoil_y", self.ry_spin.value()))
        layout.addWidget(ry_label)
        layout.addWidget(self.ry_spin)

        layout.addStretch(1)


class ScreenPage(QWidget):
    def __init__(self, cfg: ConfigController):
        super().__init__()
        self.cfg = cfg
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # FOV --------------------------------------------------------------------
        fov_label = QLabel("Field of view X")
        self.fov_spin = QSpinBox()
        self.fov_spin.setRange(10, 1500)
        self.fov_spin.setValue(cfg.get_int("screen", "fov_x"))
        self.fov_spin.valueChanged.connect(lambda v: cfg.set_int("screen", "fov_x", v))
        layout.addWidget(fov_label)
        layout.addWidget(self.fov_spin)

        # Color picker -----------------------------------------------------------
        color_btn = QPushButton("Upper color …")
        color_btn.clicked.connect(self._choose_color)
        layout.addWidget(color_btn)

        layout.addStretch(1)

    # ------------------------------------------------------------------ slots --

    def _choose_color(self):
        r, g, b = self.cfg.get_color("screen", "upper_color")
        initial = QColor(r, g, b)
        dialog = QColorDialog(initial, self)
        if dialog.exec():
            col = dialog.selectedColor()
            self.cfg.set_color("screen", "upper_color", (col.red(), col.green(), col.blue()))


# ---------------------------------------------------------------------------
# Widgets with built-in range / step
# ---------------------------------------------------------------------------


class QDoubleSpinBox(QSpinBox):
    """A spinbox that stores floats while still looking like an int box."""

    def __init__(self, minimum: float, maximum: float, step: float, value: float):
        super().__init__()
        self._factor = 1 / step
        self.setRange(int(minimum * self._factor), int(maximum * self._factor))
        self.setValue(int(value * self._factor))
        self._step = int(step * self._factor)
        self.setSingleStep(self._step)

    def value(self) -> float:  # type: ignore[override]
        return super().value() / self._factor

    def stepBy(self, steps: int) -> None:  # noqa: D401
        super().stepBy(steps)

    def textFromValue(self, value: int) -> str:  # noqa: D401
        return f"{value / self._factor:.2f}"

    def valueFromText(self, text: str) -> int:  # noqa: D401
        return int(float(text) * self._factor)


# ---------------------------------------------------------------------------
# MainWindow
# ---------------------------------------------------------------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unibot Configurator")
        self.resize(720, 420)

        # Controller
        self.cfg = ConfigController()

        # Central layout --------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)  # vertical: body + footer
        outer.setContentsMargins(0, 0, 0, 0)

        body = QHBoxLayout()
        outer.addLayout(body, 1)  # stretch 1

        # Navigation list -------------------------------------------------------
        self.nav = QListWidget()
        self.nav.setFixedWidth(150)
        self.nav.setStyleSheet("QListWidget::item { padding: 10px; } QListWidget::item:selected { background:#3e3e3e; }")
        body.addWidget(self.nav)

        # Stacked pages ---------------------------------------------------------
        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        # Create pages ----------------------------------------------------------
        pages = [
            ("Aim", AimPage(self.cfg)),
            ("Recoil", RecoilPage(self.cfg)),
            ("Screen", ScreenPage(self.cfg)),
        ]
        for idx, (name, widget) in enumerate(pages):
            self.stack.addWidget(widget)
            item = QListWidgetItem(name)
            self.nav.addItem(item)
            if idx == 0:
                item.setSelected(True)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)

        # Footer buttons --------------------------------------------------------
        footer = QHBoxLayout()
        outer.addLayout(footer)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save)
        footer.addWidget(self.save_btn)

        self.run_btn = QPushButton("Run bot")
        self.run_btn.setCheckable(True)
        self.run_btn.toggled.connect(self._toggle_bot)
        footer.addWidget(self.run_btn)

        footer.addStretch(1)

    # ------------------------------------------------------------------ slots --

    @Slot()
    def _save(self) -> None:
        self.cfg.save()

    # -------------------------------------------------------------- bot spawn --

    def _toggle_bot(self, checked: bool) -> None:
        if checked:
            self.run_btn.setText("Stop bot")
            self.bot_thread = threading.Thread(target=self._run_bot_process, daemon=True)
            self.bot_thread.start()
        else:
            self.run_btn.setText("Run bot")
            # The quickest way without refactoring main.py is to kill the child
            # process. This is ugly but practical for now.
            if hasattr(self, "_bot_process") and self._bot_process.poll() is None:
                self._bot_process.terminate()

    def _run_bot_process(self) -> None:
        python = sys.executable
        self._bot_process = subprocess.Popen([python, str(Path(__file__).parent / "main.py")])
        self._bot_process.wait()
        # When the process ends by itself (crash, user stopped, …) reflect that
        # in the UI so the toggle button goes back to 'off'.
        self.run_btn.blockSignals(True)
        self.run_btn.setChecked(False)
        self.run_btn.setText("Run bot")
        self.run_btn.blockSignals(False)


# ---------------------------------------------------------------------------
# Dark palette helper
# ---------------------------------------------------------------------------


def set_dark_theme(app: QApplication) -> None:
    """Apply a simple dark palette to *app*."""
    palette = QPalette()
    # Window
    palette.setColor(QPalette.Window, QColor(37, 37, 38))
    palette.setColor(QPalette.WindowText, Qt.white)
    # Base
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(37, 37, 38))
    # ToolTip
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    # Text
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 48))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    # Highlight
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, Qt.white)

    app.setPalette(palette)


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------


def main() -> None:
    app = QApplication(sys.argv)
    set_dark_theme(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()