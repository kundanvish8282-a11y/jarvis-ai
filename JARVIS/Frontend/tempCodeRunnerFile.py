import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QLabel,
    QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt5.QtGui import QMovie, QColor, QTextCharFormat, QFont, QTextBlockFormat, QPainter, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

# ================= ENV =================
env = dotenv_values(".env")
ASSISTANT_NAME = env.get("ASSISTANT_NAME", "JARVIS")

BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "Frontend", "Files")
GRAPHICS_DIR = os.path.join(BASE_DIR, "Frontend", "Graphics")

os.makedirs(TEMP_DIR, exist_ok=True)

for f in ["Responses.data", "Status.data", "Mic.data"]:
    path = os.path.join(TEMP_DIR, f)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write("")

def temp_path(name): return os.path.join(TEMP_DIR, name)
def gfx(name): return os.path.join(GRAPHICS_DIR, name)

# ================= UTIL =================
def write_file(name, text):
    with open(temp_path(name), "w", encoding="utf-8") as f:
        f.write(text)

def read_file(name):
    try:
        with open(temp_path(name), "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# ================= CHAT SECTION =================
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.last_text = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setFrameStyle(QFrame.NoFrame)
        self.chat.setStyleSheet("background:black;color:white;")
        font = QFont()
        font.setPointSize(13)
        self.chat.setFont(font)

        self.status = QLabel("")
        self.status.setStyleSheet("color:white;font-size:16px;")
        self.status.setAlignment(Qt.AlignRight)

        self.gif = QLabel()
        gif_path = gfx("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(480, 270))
            movie.start()
            self.gif.setMovie(movie)
        else:
            self.gif.setText("GIF NOT FOUND")
            self.gif.setStyleSheet("color:white;")

        layout.addWidget(self.chat)
        layout.addWidget(self.status)
        layout.addWidget(self.gif)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chat)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(150)

    def update_chat(self):
        text = read_file("Responses.data")
        if text and text != self.last_text:
            self.last_text = text
            cursor = self.chat.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("white"))
            block = QTextBlockFormat()
            block.setTopMargin(10)
            cursor.setBlockFormat(block)
            cursor.setCharFormat(fmt)
            cursor.insertText(text + "\n")
            self.chat.setTextCursor(cursor)

    def update_status(self):
        self.status.setText(read_file("Status.data"))

# ================= HOME SCREEN =================
class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.toggled = True
        layout = QVBoxLayout(self)

        self.gif = QLabel()
        gif_path = gfx("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(800, 450))
            movie.start()
            self.gif.setMovie(movie)
        else:
            self.gif.setText("GIF NOT FOUND")
            self.gif.setStyleSheet("color:white;")

        self.status = QLabel("")
        self.status.setStyleSheet("color:white;font-size:16px;")

        self.mic = QLabel()
        self.set_icon("Mic_on.png")
        self.mic.mousePressEvent = self.toggle_mic

        layout.addWidget(self.gif, alignment=Qt.AlignCenter)
        layout.addWidget(self.status, alignment=Qt.AlignCenter)
        layout.addWidget(self.mic, alignment=Qt.AlignCenter)
        self.setStyleSheet("background:black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(150)

    def set_icon(self, name):
        icon_path = gfx(name)
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(60, 60)
            self.mic.setPixmap(pix)

    def toggle_mic(self, _=None):
        if self.toggled:
            self.set_icon("Mic_off.png")
            write_file("Mic.data", "OFF")
        else:
            self.set_icon("Mic_on.png")
            write_file("Mic.data", "ON")
        self.toggled = not self.toggled

    def update_status(self):
        self.status.setText(read_file("Status.data"))

# ================= TOP BAR =================
class TopBar(QWidget):
    def __init__(self, parent, stack):
        super().__init__(parent)
        self.stack = stack
        self.setFixedHeight(50)

        layout = QHBoxLayout(self)
        title = QLabel(f" {ASSISTANT_NAME} AI ")
        title.setStyleSheet("background:white;font-size:18px;")

        btn_home = QPushButton("Home")
        btn_chat = QPushButton("Chat")
        btn_close = QPushButton("X")

        btn_home.clicked.connect(lambda: stack.setCurrentIndex(0))
        btn_chat.clicked.connect(lambda: stack.setCurrentIndex(1))
        btn_close.clicked.connect(parent.close)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(btn_home)
        layout.addWidget(btn_chat)
        layout.addWidget(btn_close)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)

# ================= MAIN =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)

        