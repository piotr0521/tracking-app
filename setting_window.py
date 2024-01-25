# settings_window.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QFormLayout, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ftplib import FTP
import os

class SettingsWindow(QWidget):
    def __init__(self, settings_callback=None):
        super().__init__()
        self.settings_callback = settings_callback
        self.init_ui()

    def init_ui(self):
        icon = QIcon("assets/setting.png")
        self.setWindowIcon(icon)
        app_icon = QIcon("assets/setting.png")
        QApplication.instance().setWindowIcon(app_icon)

        fixed_width = 350
        self.setFixedWidth(fixed_width)
        self.setFixedHeight(fixed_width)
        self.setGeometry(300, 300, fixed_width, fixed_width)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowTitle("Settings")
        self.center_on_screen()
        
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Example settings fields
        self.HOSTNAME_input = QLineEdit(self)
        form_layout.addRow('Host:', self.HOSTNAME_input)

        self.username_input = QLineEdit(self)
        form_layout.addRow('User:', self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Password:', self.password_input)

        self.local_file_path_input = QLineEdit(self)
        self.local_file_path_input.setDisabled(True)
        self.browse_button1 = QPushButton('...', self)
        self.browse_button1.setFixedWidth(30)
        self.browse_button1.clicked.connect(lambda: self.browse_directory(self.browse_button1))
        row_layout1 = QHBoxLayout()
        row_layout1.addWidget(self.local_file_path_input)
        row_layout1.addWidget(self.browse_button1)
        form_layout.addRow('Source:', row_layout1)

        self.saving_file_path_input = QLineEdit(self)
        self.saving_file_path_input.setDisabled(True)
        self.browse_button2 = QPushButton('...', self)
        self.browse_button2.setFixedWidth(30)
        self.browse_button2.clicked.connect(lambda: self.browse_directory(self.browse_button2))
        row_layout2 = QHBoxLayout()
        row_layout2.addWidget(self.saving_file_path_input)
        row_layout2.addWidget(self.browse_button2)
        form_layout.addRow('Target:', row_layout2)
        
        # Separate line for the remote_file_path_input and browse_button2
        # self.remote_file_path_input = QLineEdit(self)
        # self.remote_file_path_input.setDisabled(True)
        # self.browse_button3 = QPushButton('...', self)
        # self.browse_button3.setFixedWidth(30)
        # self.browse_button3.clicked.connect(lambda: self.browse_directory(self.browse_button3))
        # row_layout3 = QHBoxLayout()
        # row_layout3.addWidget(self.remote_file_path_input)
        # row_layout3.addWidget(self.browse_button3)
        # form_layout.addRow('Destination:', row_layout3)

        layout.addLayout(form_layout)
        
        test_button = QPushButton('Test', self)
        test_button.clicked.connect(self.test_connection)

        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_settings)

        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.hide)

        layout.addWidget(test_button)
        layout.addWidget(save_button)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def center_on_screen(self):
        # Center the frameless window on the screen
        screen_geometry = QApplication.desktop().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

    def test_connection(self):
        try:
            # Connect to the FTP server
            host = self.HOSTNAME_input.text()
            username = self.username_input.text()
            password = self.password_input.text()

            ftp = FTP()
            ftp.connect(host)
            ftp.login(username, password)

            # List files in the current directory
            file_list = ftp.nlst()
            # Close the FTP connection
            ftp.quit()

            QMessageBox.information(self, 'Success', 'FTP Connection Successful')
        except Exception as e:
            print(e)
            QMessageBox.critical(self, 'Error', 'FTP Connection Failed')

    def save_settings(self):
        username = self.username_input.text()
        password = self.password_input.text()
        local_path = self.local_file_path_input.text()
        saving_path = self.saving_file_path_input.text()
        # remote_path = self.remote_file_path_input.text()
        HOSTNAME = self.HOSTNAME_input.text()

        with open('settings.ini', 'w') as file:
          file.write(f"USER={username}\n")
          file.write(f"PASSWORD={password}\n")
          file.write(f"SOURCE={local_path}\n")
          file.write(f"TARGET={saving_path}\n")
        #   file.write(f"DESTINATION={remote_path}\n")
          file.write(f"HOSTNAME={HOSTNAME}\n")

        print("Settings saved to 'settings.ini'")

        self.hide()

    def browse_directory(self, sender_button):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly | QFileDialog.ShowDirsOnly
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if directory_path:
            # Determine which line edit was associated with the browse button
            sender_button = self.sender()
            if sender_button == self.browse_button1:
                self.local_file_path_input.setText(directory_path)
            elif sender_button == self.browse_button2:
                self.saving_file_path_input.setText(directory_path)
            else :
                self.remote_file_path_input.setText(directory_path)

    def read_settings(self):
        try:
            # Read the settings from the text file
            with open('settings.ini', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    key, value = map(str.strip, line.split('='))
                    if key == 'USER':
                        self.username_input.setText(f'{value}')
                    elif key == 'PASSWORD':
                        self.password_input.setText(f'{value}')
                    elif key == 'SOURCE':
                        self.local_file_path_input.setText(f'{value if len(value) > 0 else os.getcwd() + "/source"}')
                    elif key == 'TARGET':
                        self.saving_file_path_input.setText(f'{value if len(value) > 0 else os.getcwd() + "/target"}')
                    # elif key == 'DESTINATION':
                    #     self.remote_file_path_input.setText(f'{value}')
                    elif key == 'HOSTNAME':
                        self.HOSTNAME_input.setText(f'{value}')

        except FileNotFoundError:
            print("Settings file not found. Save settings first.")

    def showEvent(self, event):
        # Override the showEvent method to call read_settings when the window is shown
        super().showEvent(event)
        self.read_settings()
