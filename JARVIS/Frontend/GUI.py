import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QLabel,
    QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt5.QtGui import (
    QMovie, QColor, QTextCharFormat, QFont,
    QTextBlockFormat, QPainter, QPixmap
)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

# ================= ENV =================
env = dotenv_values(".env")
ASSISTANT_NAME = env.get("Assistantname", "JARVIS")

BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "Frontend", "Files")
GRAPHICS_DIR = os.path.join(BASE_DIR, "Frontend", "Graphics")

os.makedirs(TEMP_DIR, exist_ok=True)

for f in ["Responses.data", "Status.data", "Mic.data", "Database.data"]:
    path = os.path.join(TEMP_DIR, f)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fp:
            fp.write("")

# ================= PATH HELPERS =================
def TempDictonaryPath(name):
    return os.path.join(TEMP_DIR, name)

def gfx(name):
    return os.path.join(GRAPHICS_DIR, name)

# ================= FILE HELPERS =================
def write_file(name, text):
    with open(TempDictonaryPath(name), "w", encoding="utf-8") as f:
        f.write(text)

def read_file(name):
    try:
        with open(TempDictonaryPath(name), "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

# ================= FUNCTIONS REQUIRED BY main.py =================
def ShowTextToScreen(text):
    write_file("Responses.data", text)

def SetAssistantStatus(status):
    write_file("Status.data", status)

def GetAssistantStatus():
    return read_file("Status.data")

def SetMicrophoneStatus(status):
    write_file("Mic.data", status)

def GetMicrophoneStatus():
    return read_file("Mic.data")

def AnswerModifier(text):
    return "\n".join(line for line in text.split("\n") if line.strip())

def QueryModifier(query):
    query = query.strip()
    if not query.endswith((".", "?", "!")):
        query += "?"
    return query

# ================= CHAT SCREEN =================
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

        layout.addWidget(self.chat)
        layout.addWidget(self.status)
        layout.addWidget(self.gif)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chat)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(200)

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
            self.chat.verticalScrollBar().setValue(
                self.chat.verticalScrollBar().maximum()
            )

    def update_status(self):
        self.status.setText(GetAssistantStatus())

# ================= HOME SCREEN =================
class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.toggled = False

        layout = QVBoxLayout(self)

        self.gif = QLabel()
        gif_path = gfx("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(800, 450))
            movie.start()
            self.gif.setMovie(movie)

        self.status = QLabel("")
        self.status.setStyleSheet("color:white;font-size:18px;")

        self.mic = QLabel()
        self.set_icon("Mic_off.png")
        self.mic.mousePressEvent = self.toggle_mic

        layout.addWidget(self.gif, alignment=Qt.AlignCenter)
        layout.addWidget(self.status, alignment=Qt.AlignCenter)
        layout.addWidget(self.mic, alignment=Qt.AlignCenter)
        self.setStyleSheet("background:black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(200)

    def set_icon(self, name):
        path = gfx(name)
        if os.path.exists(path):
            self.mic.setPixmap(QPixmap(path).scaled(60, 60))

    def toggle_mic(self, _=None):
        if self.toggled:
            self.set_icon("Mic_off.png")
            SetMicrophoneStatus("False")
            SetAssistantStatus("Mic OFF")
        else:
            self.set_icon("Mic_on.png")
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
        self.toggled = not self.toggled

    def update_status(self):
        self.status.setText(GetAssistantStatus())

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

# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.stack = QStackedWidget()
        self.stack.addWidget(HomeScreen())
        self.stack.addWidget(ChatSection())

        self.setCentralWidget(self.stack)
        self.setMenuWidget(TopBar(self, self.stack))
        self.showMaximized()

        SetAssistantStatus("Available...")

# ================= REQUIRED BY main.py =================
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
