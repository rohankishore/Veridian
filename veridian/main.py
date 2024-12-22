from veridian import window
# coding:utf-8
import sys

# import qdarktheme
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # qdarktheme.enable_hi_dpi()
    w = window.Window()
    # qdarktheme.setup_theme("dark", custom_colors={"primary": theme_color})
    w.show()
    sys.exit(app.exec())
