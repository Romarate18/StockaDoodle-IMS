"""
StockaDoodle Inventory Management System - Multi-Factor Authentication Window

Features:
- Clean, modern UI with StockaDoodle branding
- API-based MFA code verification
- Auto-submit on 6-digit code entry
- Proper error handling and user feedback
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import os

from api_client.stockadoodle_api import StockaDoodleAPI
from utils.styles import get_dialog_style
from utils.helpers import get_feather_icon
from utils.config import AppConfig


class MFAWindow(QDialog):
    """Multi-Factor Authentication dialog for StockaDoodle IMS."""

    mfa_verified = pyqtSignal(dict)

    def __init__(self, user_data: dict, parent=None):
        """
        Initialize MFA dialog.

        Args:
            user_data: User data from login attempt (contains username, role, email)
            parent: Parent widget
        """
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = StockaDoodleAPI()

        self.setWindowTitle("Two-Factor Authentication")
        self.setFixedSize(380, 300)
        self.setStyleSheet(get_dialog_style())
        self.setModal(True)

        # Set window icon
        icon_path = "../desktop_app/assets/icons/stockadoodle-transparent.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        """Initialize the MFA dialog UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Two-Factor Authentication")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            f"A verification code has been sent to your email.\n"
            f"Please enter the 6-digit code below."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #b2bec3; font-size: 12pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Code input
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter 6-digit code")
        self.code_input.setMaxLength(6)
        self.code_input.setFont(QFont("Consolas", 18))
        self.code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_input.setFixedHeight(60)
        self.code_input.textChanged.connect(self.format_code_input)
        layout.addWidget(self.code_input)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(get_feather_icon("x"))
        cancel_btn.clicked.connect(self.reject)

        verify_btn = QPushButton("Verify")
        verify_btn.setIcon(get_feather_icon("check-circle"))
        verify_btn.setDefault(True)
        verify_btn.clicked.connect(self.verify_code)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(verify_btn)
        layout.addLayout(btn_layout)

        # Auto-submit on 6 digits
        self.code_input.textChanged.connect(self.check_auto_submit)

    def format_code_input(self, text):
        """Format code input - only allow digits."""
        if not text.isdigit():
            self.code_input.setText(''.join(filter(str.isdigit, text)))

    def check_auto_submit(self):
        """Auto-submit verification when 6 digits are entered."""
        if len(self.code_input.text()) == 6:
            self.verify_code()

    def verify_code(self):
        """Verify the entered MFA code via API."""
        code = self.code_input.text().strip()

        if len(code) != 6 or not code.isdigit():
            QMessageBox.warning(self, "Invalid Code", 
                              "Please enter a valid 6-digit code.")
            return

        try:
            # Verify MFA code via API
            result = self.api_client.verify_mfa_code(
                self.user_data['username'], 
                code
            )

            user = result.get('user')
            if user:
                QMessageBox.information(self, "Success", 
                                      "Authentication successful!")
                self.mfa_verified.emit(user)
                self.accept()
            else:
                QMessageBox.critical(self, "Verification Failed", 
                                   "Invalid verification code. Please try again.")
                self.code_input.clear()
                self.code_input.setFocus()

        except Exception as e:
            error_msg = str(e)
            QMessageBox.critical(self, "Verification Failed",
                               f"Code verification failed:\n{error_msg}")
            self.code_input.clear()
            self.code_input.setFocus()

    def mousePressEvent(self, event):
        """Allow dragging the window."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Handle mouse release for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        """Handle window dragging."""
        if not hasattr(self, 'old_pos') or not self.old_pos:
            return
        delta = event.globalPosition().toPoint() - self.old_pos
        self.move(self.pos() + delta)
        self.old_pos = event.globalPosition().toPoint()