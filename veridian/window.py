# coding:utf-8
import os
import sqlite3

# import qdarktheme
from PyQt6.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QFrame
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme, setTheme, Theme,
                            PopUpAniStackedWidget, setThemeColor)
from qframelesswindow import FramelessWindow, TitleBar

import home
import tasks
import projects

APP_NAME = "Veridian"
VERSION = "1.0.0"


# with open("resources/misc/config.json", "r") as themes_file:
#    _themes = json.load(themes_file)

# theme_color = _themes["theme"]
# progressive = _themes["progressive"]

def initialize_database():
    connection = sqlite3.connect("resources/data/tasks.db")
    cursor = connection.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0
        )
    """)
    print("Table checked or created successfully.")

    # Ensure 'completed' column exists
    try:
        cursor.execute("ALTER TABLE habits ADD COLUMN completed INTEGER DEFAULT 0")
        print("Added missing 'completed' column.")
    except sqlite3.OperationalError:
        print("'completed' column already exists.")

    connection.commit()
    connection.close()

def initialize_study_db():

    DB_PATH = "resources/data/study_projects.db"

    """Initialize the database and create tables if they don't exist."""
    if not os.path.exists("resources/data"):
        os.makedirs("resources/data")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Create Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            FOREIGN KEY (project_id) REFERENCES Projects (id) ON DELETE CASCADE
        )
    """)

    # Create Chapters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES Subjects (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


class StackedWidget(QFrame):
    """ Stacked widget """

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.Type.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        self.setResizeEnabled(False)

        initialize_database()
        initialize_study_db()

        # use dark theme mode
        setTheme(Theme.DARK)

        # change the theme color
        setThemeColor("#68E95C")

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationInterface(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        #self.musicInterface = Player.MusicPlayerWidget()
        self.homeInterface = home.DashboardWidget()
        self.habitsInterface = tasks.TasksWidget()
        self.projectInterface = projects.MainWidget()
        # self.captionInterface = get_captions.CaptionWidget()
        # self.settingsInterface = settings.SettingsPage()

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Dashboard', selectedIcon=FIF.HOME)
        self.addSubInterface(self.habitsInterface, FIF.ACCEPT, 'Tasks', selectedIcon=FIF.ACCEPT_MEDIUM)
        self.addSubInterface(self.projectInterface, FIF.BOOK_SHELF, 'Projects', selectedIcon=FIF.BOOK_SHELF)

        self.navigationBar.addItem(
            routeKey='About',
            icon=FIF.HELP,
            text='About',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(1000, 600)
        self.setWindowIcon(QIcon('resources/icons/icon.png'))
        self.setWindowTitle(APP_NAME)
        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resources/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        text_for_about = f"Heya! it's Rohan, the creator of {APP_NAME}. I hope you've enjoyed using this app as much as I enjoyed making it." + "" + "\n" + "\n" \
                                                                                                                                                            "I'm a school student and I can't earn my own money LEGALLY. So any donations will be largely appreciated. Also, if you find any bugs / have any feature requests, you can open a Issue/ Pull Request in the Repo." \
                                                                                                                                                            "You can visit GitHub by pressing the button below. You can find Ko-Fi link there :) " + "\n" + "\n" + \
                         f"Once again, thank you for using {APP_NAME}. Please consider giving it a star ⭐ as it will largely motivate me to create more of such apps. Also do consider giving me a follow ;) "
        title = APP_NAME + "\n" + VERSION
        w = MessageBox(
            title,
            text_for_about,
            self
        )
        w.yesButton.setText('GitHub')
        w.cancelButton.setText('Return')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/rohankishore/Youtility"))
