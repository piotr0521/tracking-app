# main.py
from PyQt5.QtWidgets import QApplication
from tray_app import TrayApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TrayApp()
    sys.exit(app.exec_())
