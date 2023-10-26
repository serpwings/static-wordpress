# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/gui/mainwindow.py
    
    Copyright (C) 2020-2023 Faisal Shahzad <info@serpwings.com>

<LICENSE_BLOCK>
The contents of this file are subject to version 3 of the 
GNU General Public License (GPL-3.0). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/gpl-3.0.txt
https://github.com/serpwings/static-wordpress/blob/master/LICENSE


Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# STANDARD LIBARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
import logging
import os
import shutil
from pathlib import Path
from datetime import date


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QAction,
    QApplication,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QMenu,
    QToolBar,
)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QThread, QSize, QSettings, QUrl


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import (
    VERISON,
    CONFIGS,
    SHARE_FOLDER_PATH,
    SOURCE,
)
from ..core.project import Project
from ..core.utils import (
    rm_dir_tree,
    get_remote_content,
    extract_urls_from_raw_text,
)
from .workflow import WorkflowGUI
from ..gui.logger import LoggerWidget
from ..gui.rawtext import RawTextDialog
from ..gui.config import ConfigDialog
from ..gui.project import ProjectDialog
from ..gui.utils import GUI_SETTINGS, logging_decorator

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class StaticWordPressGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.appConfigurations = QSettings(
            CONFIGS["APPLICATION_NAME"], CONFIGS["APPLICATION_NAME"]
        )

        self._project = Project()
        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()

        self.text_edit_logging = LoggerWidget(self)
        self.text_edit_logging.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.text_edit_logging)
        logging.getLogger().setLevel(logging.INFO)

        self.setCentralWidget(self.text_edit_logging.plainTextEdit)
        self.statusBar().showMessage(f"{CONFIGS['APPLICATION_NAME']} is Ready")
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setFormat("No Brackground Process is running")
        self.progressBar.setFixedSize(QSize(300, 25))
        self.progressBar.setValue(0)
        self.statusBar().addPermanentWidget(self.progressBar)

        # ALL menus
        for current_menu in GUI_SETTINGS["MENUS"]:
            parent = self.findChild(QMenu, current_menu["parent"])
            if not parent:
                parent = self.menuBar()

            menu = parent.addMenu(current_menu["text"])
            menu.setObjectName(current_menu["name"])
            menu.setEnabled(current_menu["enable"])
            if current_menu["icon"]:
                menu.setIcon(QIcon(f"{SHARE_FOLDER_PATH}{current_menu['icon']}"))

        # all toolbars
        for current_toolbar in GUI_SETTINGS["TOOLBARS"]:
            toolbar = self.addToolBar(current_toolbar["text"])
            toolbar.setObjectName(current_toolbar["name"])
            toolbar.setEnabled(current_toolbar["enable"])

        # all actions
        for current_action in GUI_SETTINGS["ACTIONS"]:
            action = QAction(
                QIcon(f"{SHARE_FOLDER_PATH}{ current_action['icon']}"),
                current_action["text"],
                self,
            )
            action.setObjectName(current_action["name"])
            action.setShortcut(current_action["shortcut"])
            action.setStatusTip(current_action["tooltip"])
            action.setToolTip(current_action["tooltip"])
            action.setVisible(current_action["visible"])
            action.triggered.connect(eval(current_action["function"]))
            action.setCheckable(current_action["setCheckable"])

            current_menu = (
                self.findChild(QMenu, current_action["menu"])
                if current_action["menu"]
                else None
            )
            current_toolbar = (
                self.findChild(QToolBar, current_action["toolbar"])
                if current_action["toolbar"]
                else None
            )

            if current_menu:
                current_menu.addAction(action)
            if current_action["seperator"]:
                current_menu.addSeparator()
            if current_toolbar:
                current_toolbar.addAction(action)

        self.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        self.setWindowTitle(f"{CONFIGS['APPLICATION_NAME']} Version - {VERISON}")
        self.setMinimumSize(QSize(1366, 768))
        self.statusBar()
        logging.info(
            "Loaded static-wordpress Successfully. Open/Create a Project to get started"
        )
        logging.info("".join(140 * ["-"]))
        self.show()

    # decorators
    def is_power_user(func):
        def inner(self):
            if self.findChild(QAction, "action_edit_expert_mode").isChecked():
                return func(self)

        return inner

    def is_new_project(func):
        def inner(self):
            if self._project.is_open() or self._project.is_new():
                return func(self)

        return inner

    def is_project_open(func):
        def inner(self):
            if self._project.is_open():
                return func(self)

        return inner

    def has_project_github(func):
        def inner(self):
            if self._project.has_github():
                return func(self)

        return inner

    @is_project_open
    @logging_decorator
    def clean_output_directory(self):
        """Clean Output Directory"""

        msgBox = QMessageBox(parent=self)
        msgBox.setWindowTitle("Clean Output Folder Content")
        msgBox.setText(
            f"Existing content in Output folder will be delete?<br> {self._project.output}",
        )
        pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
        pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
        pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        msgBox.setDefaultButton(pushbuttonOk)

        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.exec_()

        if msgBox.clickedButton() == pushbuttonOk:
            rm_dir_tree(self._project.output)
            logging.info(
                f"Content of output folder at {self._project.output} are deleted"
            )

    @is_new_project
    @logging_decorator
    def extract_url_from_raw_text(self):
        rtp = RawTextDialog(
            parent=self, src_url=self._project.src_url, dest_url=self._project.dst_url
        )
        if rtp.exec_():
            raw_text = rtp.textedit_raw_text_with_links.toPlainText()
            if raw_text:
                new_additional_links = extract_urls_from_raw_text(
                    raw_text, rtp.lineedit_dest_url.text(), rtp.linedit_src_url.text()
                )
                logging.info(f" {len(new_additional_links)} Additional Urls Found")
                self._project.additional += new_additional_links
                self._project.save()

    @is_new_project
    @logging_decorator
    def clear_cache(self):
        """Clearing Crawl Cache"""
        logging.info(f"Clearing Crawl Cache")
        get_remote_content.cache_clear()

    def closeEvent(self, event):
        """ """
        msgBox = QMessageBox(parent=self)
        msgBox.setWindowTitle(f"Exiting {CONFIGS['APPLICATION_NAME']}")
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(
            "Do you really want to exit?.<br>Any unsaved changes will be lost!",
        )

        pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
        pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
        pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        msgBox.setDefaultButton(pushbuttonOk)

        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.exec_()

        if msgBox.clickedButton() == pushbuttonOk:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()
                del self._bg_thread
                del self._bg_worker
                super(StaticWordPressGUI, self).closeEvent(event)

            event.accept()

        else:
            event.ignore()

    def set_expert_mode(self):
        expert_widgets = [
            "action_wordpress_404_page",
            "action_wordpress_redirects",
            "action_wordpress_robots_txt",
            "action_wordpress_search_index",
            "action_wordpress_webpages",
        ]

        for widget_name in expert_widgets:
            self.findChild(QAction, widget_name).setVisible(self.sender().isChecked())

        self.findChild(QAction, "action_wordpress_additional_files").setVisible(
            self.sender().isChecked() and self._project.src_type != SOURCE.ZIP
        )

    def set_debug_mode(self):
        if self.sender().isChecked():
            logging.getLogger().setLevel(
                logging.INFO & logging.DEBUG & logging.ERROR & logging.WARNING
            )
        else:
            logging.getLogger().setLevel(logging.INFO)

    def help(self):
        """ """
        url = QUrl(CONFIGS["HELP_URL"])

        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, "Open Help URL", "Could not open Help URL")

    @logging_decorator
    def show_configs(self):
        """Interface with System Configurations"""
        w = ConfigDialog(parent=self)
        if w.exec_():
            logging.info("Saved/Updated Default Configurations")

    def about(self):
        """ """
        msgBox = QMessageBox(parent=self)
        msgBox.setText(
            f"Copyright {date.today().year} - SERP Wings"
            f"<br><br>{CONFIGS['APPLICATION_NAME']} Version - {VERISON}"
            "<br><br>This work is an opensource project under <br>GNU General Public License v3 or later (GPLv3+)"
            f"<br>More Information at <a href='https://{CONFIGS['ORGANIZATION_DOMAIN']}/'>{CONFIGS['ORGANIZATION_NAME']}</a>"
        )
        msgBox.addButton(QMessageBox.Ok).setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
        )
        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setWindowTitle("About Us")
        msgBox.exec()

    @logging_decorator
    def new_project(self):
        """Closing current project will automatically start a new project."""
        self.close_project()

        pdialog = ProjectDialog(self, self._project, title_="New Project")
        if pdialog.exec_():
            self._project = pdialog._project
            self.appConfigurations.setValue("last-project", self._project.output)

            if Path(self._project.output).is_dir():
                self._project.path.parent.mkdir(parents=True, exist_ok=True)
                src = Path(f"{SHARE_FOLDER_PATH}/_ignore")
                dst = Path(f"{self._project.output}/.gitignore")
                if src.exists():
                    shutil.copyfile(src, dst)
            else:
                return

            self.update_widgets()
            logging.info("Saved/Update Project")
            self._project.save()

    @logging_decorator
    def open_project(self):
        """Opening static-wordpress Project File"""
        self.close_project()
        if not self._project.is_open():
            project_folder = QFileDialog.getExistingDirectory(
                self,
                "Select Static-WordPress Project Directory",
                str(self.appConfigurations.value("last-project")),
                QFileDialog.ShowDirsOnly,
            )

            project_path = Path(f"{project_folder}/._data/.project.json")

            if project_path.exists():
                self._project.open(project_path)
                if self._project.is_open():
                    pdialog = ProjectDialog(
                        self, self._project, title_="Project Properties"
                    )

                    if pdialog.exec_():
                        self._project = pdialog._project

                    if not self._project.is_older_version():
                        logging.warning(
                            f"Your Project was saved with an older version : {self._project.version}."
                        )

                    logging.info(f"Open Project {self._project.path} Successfully")
                    self.appConfigurations.setValue("last-project", project_folder)
            else:
                msgBox = QMessageBox(parent=self)
                msgBox.setText(
                    f"Project cannot be opened or selected path invalid."
                    f"<br>Please try again with project folder."
                )
                msgBox.addButton(QMessageBox.Ok).setIcon(
                    QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
                )
                msgBox.setWindowIcon(
                    QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
                )
                msgBox.setTextFormat(Qt.RichText)
                msgBox.setWindowTitle("Open Project")
                msgBox.exec()

                logging.info(
                    "No New Project Opened. Unsaved project properties will be lost."
                )

        self.update_widgets()
        # self._project.save()

    @logging_decorator
    def show_project(self):
        """showing static-wordpress Project File"""
        if self._project.is_open():
            pdialog = ProjectDialog(self, self._project, title_="Current Project")
            if pdialog.exec_():
                self._project = pdialog._project
            self._project.save()
            self.update_widgets()
        else:
            msgBox = QMessageBox(parent=self)
            msgBox.setText(f"No Project Available.")
            msgBox.addButton(QMessageBox.Ok).setIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
            )
            msgBox.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            msgBox.setTextFormat(Qt.RichText)
            msgBox.setWindowTitle("Project Settings")
            msgBox.exec()
            logging.info("No New Project found.")

    @is_project_open
    @logging_decorator
    def close_project(self):
        """Assign new project and old properties will be lost.
        Default is assigned as CLOSED project
        """
        msgBox = QMessageBox(parent=self)
        msgBox.setWindowTitle("Close Existing Project")
        msgBox.setText(
            "Are you sure to close current project and open new one?.<br>All existing project properties will be lost!",
        )
        pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
        pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
        pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        msgBox.setDefaultButton(pushbuttonOk)

        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.exec_()

        if msgBox.clickedButton() == pushbuttonOk:
            self._project = Project()
            self.update_widgets()

    @is_project_open
    def start_batch_process(self):
        """Start Crawling"""

        if not self._project.output.exists():
            msgBox = QMessageBox(parent=self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle("Output Folder")
            msgBox.setText(
                f"Following Output Folder doesnt not exit?.<br>{self._project.output}<br>Do You want to create it now?",
            )
            pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
            pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

            pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
            pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

            msgBox.setDefaultButton(pushbuttonOk)

            msgBox.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            msgBox.setTextFormat(Qt.RichText)
            msgBox.exec_()

            if msgBox.clickedButton() == pushbuttonOk:
                os.mkdir(self._project.output)
            else:
                return
        else:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()

            self._bg_worker = WorkflowGUI()
            self._bg_worker.set_project(project_=self._project)

            if self._project.src_type == SOURCE.ZIP:
                if not self._bg_worker._work_flow.verify_simply_static():
                    msgBox = QMessageBox(parent=self)
                    msgBox.setWindowTitle("ZIP File Missing")
                    msgBox.setIcon(QMessageBox.Question)
                    msgBox.setText(
                        "ZIP File not found. Please check your project configurations?",
                    )
                    pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
                    pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

                    pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
                    pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

                    msgBox.setDefaultButton(pushbuttonOk)

                    msgBox.setWindowIcon(
                        QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
                    )
                    msgBox.setTextFormat(Qt.RichText)
                    msgBox.exec_()

                    if msgBox.clickedButton() == pushbuttonOk:
                        return

            self._bg_thread = QThread(parent=self)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.signalProgress.connect(self.update_statusbar)
            self._bg_thread.started.connect(self._bg_worker.batch_processing)
            self._bg_thread.start()

    @is_project_open
    def stop_process(self) -> None:
        if self._bg_worker.is_running():
            msgBox = QMessageBox(parent=self)
            msgBox.setWindowTitle("Stop Crawling Process")
            msgBox.setText(
                "Do you really want to Stop Crawling Thread?",
            )
            pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
            pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

            pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
            pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

            msgBox.setDefaultButton(pushbuttonOk)

            msgBox.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            msgBox.setTextFormat(Qt.RichText)
            msgBox.exec_()

            if msgBox.clickedButton() == pushbuttonOk:
                self._bg_worker.stop_calcualations()
                self.update_statusbar("Stoping Processing", 100)

    @is_project_open
    def crawl_website(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.pre_processing)
        self._bg_thread.start()

    @is_project_open
    def crawl_additional_files(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.crawl_additional_files)
        self._bg_thread.start()

    @is_project_open
    def create_search_index(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_search)
        self._bg_thread.start()

    @is_project_open
    def create_404_page(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_404_page)
        self._bg_thread.start()

    @is_project_open
    def create_redirects(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_redirects)
        self._bg_thread.start()

    @is_project_open
    def create_robots_txt(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_robots_txt)
        self._bg_thread.start()

    @is_project_open
    def create_github_repositoy(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.create_github_repositoy)
        self._bg_thread.start()

    @is_project_open
    def delete_github_repository(self) -> None:
        """"""

        msgBox = QMessageBox(parent=self)
        msgBox.setWindowTitle("Deleting Repository on GitHub")
        msgBox.setText(
            f"Do you really want to delete {self._project.gh_repo} on GitHub?<br>This deletion is not reversible.",
        )
        pushbuttonOk = msgBox.addButton("OK", QMessageBox.YesRole)
        pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbuttonNo = msgBox.addButton("Cancel", QMessageBox.NoRole)
        pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        msgBox.setDefaultButton(pushbuttonOk)

        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.exec_()

        if msgBox.clickedButton() == pushbuttonOk:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()

            self._bg_worker = WorkflowGUI()
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.signalProgress.connect(self.update_statusbar)
            self._bg_thread.started.connect(self._bg_worker.delete_github_repositoy)
            self._bg_thread.start()

    @is_project_open
    def initialize_repository(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.init_git_repositoy)
        self._bg_thread.start()

    @is_project_open
    def commit_repository(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.commit_git_repositoy)
        self._bg_thread.start()

    @is_project_open
    def publish_repository(self) -> None:
        """ """
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.publish_github_repositoy)
        self._bg_thread.start()

    def update_statusbar(self, message_, percent_) -> None:
        if percent_ >= 0:
            self.progressBar.setValue(percent_)
            self.statusBar().showMessage(message_)
        else:
            self.progressBar.setFormat(message_)

        if percent_ >= 100:
            self.progressBar.setFormat(message_)

    def update_widgets(self) -> None:
        self.findChild(QMenu, "menu_github").setEnabled(self._project.has_github())
        self.findChild(QMenu, "menu_wordpress").setEnabled(
            self._project.has_wordpress() or self._project.can_crawl()
        )
        self.findChild(QToolBar, "toolbar_github").setEnabled(
            self._project.has_github()
        )
        self.findChild(QToolBar, "toolbar_wordpres").setEnabled(
            self._project.has_wordpress() or self._project.can_crawl()
        )

        # update menu items
        if self._project.src_type == SOURCE.ZIP:
            self.findChild(QAction, "action_wordpress_webpages").setText(
                "&Download Zip File"
            )
            self.findChild(QAction, "action_wordpress_additional_files").setVisible(
                False
            )
        else:
            self.findChild(QAction, "action_wordpress_webpages").setText(
                "&Crawl Webpages"
            )
            self.findChild(QAction, "action_wordpress_additional_files").setVisible(
                self.findChild(QAction, "action_edit_expert_mode").isChecked()
            )

        new_window_title = (
            f"{self._project.name} - {CONFIGS['APPLICATION_NAME']}  Version - {VERISON}"
        )

        self.setWindowTitle(new_window_title)


def main():
    app = QApplication(sys.argv)
    wind = StaticWordPressGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    pass
