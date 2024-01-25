from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen, QMessageBox, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
import shutil

from ftplib import FTP
from setting_window import SettingsWindow

class FTPUploader:
    def __init__(self, HOSTNAME, ftp_user, ftp_password, ftp_directory='/'):
        self.HOSTNAME = HOSTNAME
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.ftp_directory = ftp_directory

    def upload_file(self, local_path, remote_filename):
        try:
            with FTP(self.HOSTNAME) as ftp:
                ftp.login(user=self.ftp_user, passwd=self.ftp_password)
                ftp.cwd(self.ftp_directory)
                with open(local_path, 'rb') as file:
                    ftp.storbinary(f'STOR {remote_filename}', file)
            print('values: ', self.HOSTNAME, self.ftp_user, self.ftp_password)
        except Exception as e:
            print('error: ',e)

    def move_file(self, local_path, destination_folder):
        shutil.move(local_path, destination_folder)

class MyHandler(FileSystemEventHandler):
    def __init__(self, ftp_uploader, destination_folder):
        self.ftp_uploader = ftp_uploader
        self.destination_folder = destination_folder

    def on_created(self, event):
        if event.is_directory:
            return
        local_path = event.src_path
        remote_filename = os.path.basename(local_path)

        try:
            # Upload the file to FTP
            self.ftp_uploader.upload_file(local_path, remote_filename)

            # Move the file to the destination folder
            self.ftp_uploader.move_file(local_path, self.destination_folder)
            QMessageBox.information(None, 'Success', 'File upload success', QMessageBox.Ok)
            print(f"Uploaded {local_path} to FTP and moved to {self.destination_folder}.")
        except Exception as e:
            QMessageBox.critical(None, 'Error', f'File upload failed: {str(e)}', QMessageBox.Ok)


class TrayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_icon = QIcon("assets/tray.png")  # Replace with the actual path to your icon file
        self.tray_icon = QSystemTrayIcon(QIcon("assets/tray.png"), self)  # Specify self.app as the parent
        self.tray_menu = QMenu()
        self.disable_action = QAction("Inactive", self)
        self.settings_window = None

        self.show_splash_screen()

        self.read_settings()        
        self.observer = Observer()
        ftp_uploader = FTPUploader(self.HOSTNAME, self.username, self.password)
        event_handler = MyHandler(ftp_uploader, self.saving_path)
        self.observer.schedule(event_handler, path=self.local_path, recursive=False)
        
        self.setup_ui()
        self.start_service()

        self.splash.hide()
        
    def show_splash_screen(self):
        # Create a QPixmap with the splash screen image
        splash_pix = QPixmap('assets/splash.png')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())

        # Add a label with a message to the splash screen
        message_label = QLabel("Loading...")
        message_label.setAlignment(Qt.AlignCenter)
        font = message_label.font()
        font.setPointSize(14)
        message_label.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(message_label)
        splash.setLayout(layout)

        # Show the splash screen
        splash.show()

        # Center the splash screen on the screen
        splash.move((QApplication.desktop().width() - splash.width()) // 2,
                    (QApplication.desktop().height() - splash.height()) // 2)

        # Process events to make sure the splash screen is displayed immediately
        QApplication.processEvents()

        self.splash = splash

    def setup_ui(self):
        # Connect actions to functions
        self.disable_action.triggered.connect(self.toggle_service)
        self.disable_action.setIcon(QIcon('./assets/active.png'))
        self.setting_action = QAction("Setting", self)
        self.setting_action.setIcon(QIcon('./assets/setting.png'))
        self.exit_action = QAction("Exit", self)
        self.exit_action.setIcon(QIcon('./assets/exit.png'))

        self.setting_action.triggered.connect(self.setting_window)
        self.exit_action.triggered.connect(self.close_application)

        # Add actions to the tray menu
        self.tray_menu.addAction(self.disable_action)
        self.tray_menu.addAction(self.setting_action)
        self.tray_menu.addAction(self.exit_action)

        # Set the tray icon properties
        self.tray_icon.setContextMenu(self.tray_menu)

        # Show the tray icon
        self.tray_icon.show()
 
    def close_application(self):
        # Perform any cleanup or additional steps before closing, if needed
        QApplication.quit()

    def toggle_service(self):
        current_label = self.disable_action.text()
        
        if current_label == "Inactive":
            # Stop the current observer if it exists
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            self.disable_action.setText("Active")
            self.disable_action.setIcon(QIcon('./assets/active.png'))
        else:
            # Start a new observer (assuming self.observer is initialized somewhere)
            if not self.observer or not self.observer.is_alive():
                # Initialize or restart the observer if it doesn't exist or is not alive
                self.observer = Observer()  # Replace with your observer class instantiation
                self.observer.start()
            self.disable_action.setText("Inactive")
            self.disable_action.setIcon(QIcon('./assets/inactive.png'))

    def setting_window(self):
        if not self.settings_window or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(settings_callback=self.restart_service)
            self.settings_window.show()

    def read_settings(self):

        current_path = os.getcwd()
        source_path = os.path.join(current_path, 'source')
        target_path = os.path.join(current_path, 'target')

        if not os.path.exists(source_path):
            os.makedirs(source_path)

        if not os.path.exists(target_path):
            os.makedirs(target_path)
        
        try:
            if os.path.isfile('settings.ini'):
                # Read the settings from the text file
                with open('settings.ini', 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        key, value = map(str.strip, line.split('='))
                        if key == 'USER':
                            self.username = value
                        elif key == 'PASSWORD':
                            self.password = value
                        elif key == 'SOURCE':
                            self.local_path = value if len(value) > 0 else source_path
                        elif key == 'TARGET':
                            self.saving_path = value if len(value) > 0 else target_path
                        elif key == 'DESTINATION':
                            self.remote_path = value
                        elif key == 'HOSTNAME':
                            self.HOSTNAME = value
            else:
                with open('settings.ini', 'w') as file:
                    file.write(f"HOSTNAME=\n")
                    file.write(f"USER=\n")
                    file.write(f"PASSWORD=\n")
                    file.write(f"SOURCE={source_path}\n")
                    file.write(f"TARGET={target_path}\n")
                    self.local_path = source_path
                    self.saving_path = target_path
                    #   file.write(f"DESTINATION={remote_path}\n")

        except FileNotFoundError:
            print("Settings file not found. Save settings first.")

    def start_service(self):
        self.observer.start()

    def restart_service(self):
        if self.observer:
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join(timeout=5)  # Specify a timeout in seconds to avoid potential deadlock
        else:
            print("Observer is not running")
