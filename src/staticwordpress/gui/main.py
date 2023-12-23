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
    QMainWindow,
    QAction,
    QApplication,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QMenu,
    QToolBar,
    QDockWidget,
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
from ..gui.workflow import SWWorkflowObject
from ..gui.logger import SWLoggerWidget
from ..gui.editor import SWIPythonWidget
from ..gui.rawtext import SWRawTextDialog
from ..gui.config import SWConfigDialog
from ..gui.project import SWProjectDialog
from ..gui.utils import GUI_SETTINGS, logging_decorator


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_configurations = QSettings(
            CONFIGS["APPLICATION_NAME"], CONFIGS["APPLICATION_NAME"]
        )

        self._project = Project()
        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()

        self.text_edit_logging = SWLoggerWidget(self)
        self.text_edit_logging.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.text_edit_logging)
        logging.getLogger().setLevel(logging.INFO)
        self.setCentralWidget(self.text_edit_logging.plaintext_edit)

        self.statusBar().showMessage(f"{CONFIGS['APPLICATION_NAME']} is Ready")
        self.progressbar = QProgressBar()
        self.progressbar.setAlignment(Qt.AlignCenter)
        self.progressbar.setFormat("No Brackground Process is running")
        self.progressbar.setFixedSize(QSize(300, 25))
        self.progressbar.setValue(0)
        self.statusBar().addPermanentWidget(self.progressbar)

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

        # docked widgets
        self.dockwidget_ipython = QDockWidget("IPython Console", self)
        self.dockwidget_ipython.setFloating(False)
        self.dockwidget_ipython.hide()
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget_ipython)
        self.ipython_console = None

        self.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        self.setWindowTitle(f"{CONFIGS['APPLICATION_NAME']} Version - {VERISON}")
        self.setMinimumSize(QSize(1366, 768))
        self.statusBar()
        logging.info(
            "Loaded static-wordpress Successfully. Open/Create a Project to get started"
        )
        logging.info("".join(140 * ["-"]))
        self.update_widgets()
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

        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Clean Output Folder Content")
        message_box.setText(
            f"Existing content in Output folder will be delete?<br> {self._project.output}",
        )
        pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
        pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
        pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        message_box.setDefaultButton(pushbutton_ok)

        message_box.setWindowIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
        )
        message_box.setTextFormat(Qt.RichText)
        message_box.exec_()

        if message_box.clickedButton() == pushbutton_ok:
            rm_dir_tree(self._project.output)
            logging.info(
                f"Content of output folder at {self._project.output} are deleted"
            )

    @is_new_project
    @logging_decorator
    def extract_url_from_raw_text(self):
        raw_text_dialog = SWRawTextDialog(
            parent=self, src_url=self._project.src_url, dest_url=self._project.dst_url
        )
        if raw_text_dialog.exec_():
            raw_text = raw_text_dialog.textedit_raw_text_with_links.toPlainText()
            if raw_text:
                new_additional_links = extract_urls_from_raw_text(
                    raw_text,
                    raw_text_dialog.lineedit_dest_url.text(),
                    raw_text_dialog.linedit_src_url.text(),
                )
                logging.info(f" {len(new_additional_links)} Additional Urls Found")
                self._project.additional += new_additional_links
                self._project.save()

    @is_new_project
    @logging_decorator
    def clear_crawl_cache(self):
        """Clearing Crawl Cache"""
        logging.info(f"Clearing Crawl Cache")
        get_remote_content.cache_clear()

    def closeEvent(self, event):
        """ """
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle(f"Exiting {CONFIGS['APPLICATION_NAME']}")
        message_box.setIcon(QMessageBox.Question)
        message_box.setText(
            "Do you really want to exit?.<br>Any unsaved changes will be lost!",
        )

        pushbuttonOk = message_box.addButton("OK", QMessageBox.YesRole)
        pushbuttonOk.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbuttonNo = message_box.addButton("Cancel", QMessageBox.NoRole)
        pushbuttonNo.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        message_box.setDefaultButton(pushbuttonOk)

        message_box.setWindowIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
        )
        message_box.setTextFormat(Qt.RichText)
        message_box.exec_()

        if message_box.clickedButton() == pushbuttonOk:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()
                del self._bg_thread
                del self._bg_worker
                super(SWMainWindow, self).closeEvent(event)

            event.accept()

        else:
            event.ignore()

    def set_expert_mode(self):
        expert_widgets = [
            "action_crawler_create_404_page",
            "action_crawler_create_redirects",
            "action_crawler_create_robots_txt",
            "action_crawler_create_search_index",
            "action_crawler_crawl_webpages",
        ]

        for widget_name in expert_widgets:
            self.findChild(QAction, widget_name).setVisible(self.sender().isChecked())

        self.findChild(QAction, "action_crawler_crawl_additional_files").setVisible(
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

    def start_ipython_console(self):
        """ """
        if self.findChild(QAction, "action_start_ipython_console").isChecked():
            if self.ipython_console is None:
                self.ipython_console = SWIPythonWidget(interface_={"iface": self})
                self.dockwidget_ipython.setWidget(self.ipython_console)

            self.dockwidget_ipython.show()
        else:
            self.dockwidget_ipython.hide()

    @logging_decorator
    def show_configs(self):
        """Interface with System Configurations"""
        config_dialog = SWConfigDialog(parent=self)
        if config_dialog.exec_():
            logging.info("Saved/Updated Default Configurations")

    def about(self):
        """ """
        message_box = QMessageBox(parent=self)
        message_box.setText(
            f"Copyright {date.today().year} - SERP Wings"
            f"<br><br>{CONFIGS['APPLICATION_NAME']} Version - {VERISON}"
            "<br><br>This work is an opensource project under <br>GNU General Public License v3 or later (GPLv3+)"
            f"<br>More Information at <a href='https://{CONFIGS['ORGANIZATION_DOMAIN']}/'>{CONFIGS['ORGANIZATION_NAME']}</a>"
        )
        message_box.addButton(QMessageBox.Ok).setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
        )
        message_box.setWindowIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
        )
        message_box.setTextFormat(Qt.RichText)
        message_box.setWindowTitle("About Us")
        message_box.exec()

    @logging_decorator
    def new_project(self):
        """Closing current project will automatically start a new project."""
        self.close_project()

        project_dialog = SWProjectDialog(self, self._project, title_="New Project")
        if project_dialog.exec_():
            self._project = project_dialog._project
            self.app_configurations.setValue("last-project", self._project.output)

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
                str(self.app_configurations.value("last-project")),
                QFileDialog.ShowDirsOnly,
            )

            project_path = Path(f"{project_folder}/._data/.project.json")

            if project_path.exists():
                self._project.open(project_path)
                if self._project.is_open():
                    project_dialog = SWProjectDialog(
                        parent=self, project_=self._project, title_="Project Properties"
                    )

                    if project_dialog.exec_():
                        self._project = project_dialog._project

                    if not self._project.is_older_version():
                        logging.warning(
                            f"Your Project was saved with an older version : {self._project.version}."
                        )

                    logging.info(f"Open Project {self._project.path} Successfully")
                    self.app_configurations.setValue("last-project", project_folder)
            else:
                message_box = QMessageBox(parent=self)
                message_box.setText(
                    f"Project cannot be opened or selected path invalid."
                    f"<br>Please try again with project folder."
                )
                message_box.addButton(QMessageBox.Ok).setIcon(
                    QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
                )
                message_box.setWindowIcon(
                    QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
                )
                message_box.setTextFormat(Qt.RichText)
                message_box.setWindowTitle("Open Project")
                message_box.exec()

                logging.info(
                    "No New Project Opened. Unsaved project properties will be lost."
                )

        self.update_widgets()
        # self._project.save()

    @logging_decorator
    def show_project_settings(self):
        """showing static-wordpress Project File"""
        if self._project.is_open():
            project_dialog = SWProjectDialog(
                self, self._project, title_="Current Project"
            )
            if project_dialog.exec_():
                self._project = project_dialog._project
            self._project.save()
            self.update_widgets()
        else:
            message_box = QMessageBox(parent=self)
            message_box.setText(f"No Project Available.")
            message_box.addButton(QMessageBox.Ok).setIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
            )
            message_box.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            message_box.setTextFormat(Qt.RichText)
            message_box.setWindowTitle("Project Settings")
            message_box.exec()
            logging.info("No New Project found.")

    @is_project_open
    @logging_decorator
    def close_project(self):
        """Assign new project and old properties will be lost.
        Default is assigned as CLOSED project
        """
        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Close Existing Project")
        message_box.setText(
            "Are you sure to close current project and open new one?.<br>All existing project properties will be lost!",
        )
        pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
        pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))
        pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
        pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        message_box.setDefaultButton(pushbutton_ok)

        message_box.setWindowIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
        )
        message_box.setTextFormat(Qt.RichText)
        message_box.exec_()

        if message_box.clickedButton() == pushbutton_ok:
            self._project = Project()
            self.update_widgets()

    @is_project_open
    def start_batch_process(self):
        """Start Crawling"""

        if not self._project.output.exists():
            message_box = QMessageBox(parent=self)
            message_box.setIcon(QMessageBox.Question)
            message_box.setWindowTitle("Output Folder")
            message_box.setText(
                f"Following Output Folder doesnt not exit?.<br>{self._project.output}<br>Do You want to create it now?",
            )
            pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
            pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

            pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
            pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

            message_box.setDefaultButton(pushbutton_ok)

            message_box.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            message_box.setTextFormat(Qt.RichText)
            message_box.exec_()

            if message_box.clickedButton() == pushbutton_ok:
                os.mkdir(self._project.output)
            else:
                return
        else:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()

            self._bg_worker = SWWorkflowObject()
            self._bg_worker.set_project(project_=self._project)

            if self._project.src_type == SOURCE.ZIP:
                if not self._bg_worker._work_flow.verify_simply_static():
                    message_box = QMessageBox(parent=self)
                    message_box.setWindowTitle("ZIP File Missing")
                    message_box.setIcon(QMessageBox.Question)
                    message_box.setText(
                        "ZIP File not found. Please check your project configurations?",
                    )
                    pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
                    pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

                    pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
                    pushbutton_no.setIcon(
                        QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg")
                    )

                    message_box.setDefaultButton(pushbutton_ok)

                    message_box.setWindowIcon(
                        QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
                    )
                    message_box.setTextFormat(Qt.RichText)
                    message_box.exec_()

                    if message_box.clickedButton() == pushbutton_ok:
                        return

            self._bg_thread = QThread(parent=self)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.emit_progress.connect(self.update_statusbar)
            self._bg_thread.started.connect(self._bg_worker.batch_processing)
            self._bg_thread.start()

    @is_project_open
    def stop_process(self) -> None:
        if self._bg_worker.is_running():
            message_box = QMessageBox(parent=self)
            message_box.setWindowTitle("Stop Crawling Process")
            message_box.setText(
                "Do you really want to Stop Crawling Thread?",
            )
            pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
            pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

            pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
            pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

            message_box.setDefaultButton(pushbutton_ok)

            message_box.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            message_box.setTextFormat(Qt.RichText)
            message_box.exec_()

            if message_box.clickedButton() == pushbutton_ok:
                self._bg_worker.stop_calcualations()
                self.update_statusbar("Stoping Processing", 100)

    @is_project_open
    def crawl_webpages(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.pre_processing)
        self._bg_thread.start()

    @is_project_open
    def crawl_additional_files(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.crawl_additional_files)
        self._bg_thread.start()

    @is_project_open
    def create_search_index(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_search)
        self._bg_thread.start()

    @is_project_open
    def create_404_page(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_404_page)
        self._bg_thread.start()

    @is_project_open
    def create_redirects(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_redirects)
        self._bg_thread.start()

    @is_project_open
    def create_robots_txt(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.add_robots_txt)
        self._bg_thread.start()

    @is_project_open
    def create_github_repositoy(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.create_github_repositoy)
        self._bg_thread.start()

    @is_project_open
    def delete_github_repository(self) -> None:
        """"""

        message_box = QMessageBox(parent=self)
        message_box.setWindowTitle("Deleting Repository on GitHub")
        message_box.setText(
            f"Do you really want to delete {self._project.gh_repo} on GitHub?<br>This deletion is not reversible.",
        )
        pushbutton_ok = message_box.addButton("OK", QMessageBox.YesRole)
        pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        pushbutton_no = message_box.addButton("Cancel", QMessageBox.NoRole)
        pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        message_box.setDefaultButton(pushbutton_ok)

        message_box.setWindowIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
        )
        message_box.setTextFormat(Qt.RichText)
        message_box.exec_()

        if message_box.clickedButton() == pushbutton_ok:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()

            self._bg_worker = SWWorkflowObject()
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.emit_progress.connect(self.update_statusbar)
            self._bg_thread.started.connect(self._bg_worker.delete_github_repositoy)
            self._bg_thread.start()

    @is_project_open
    def initialize_repository(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.init_git_repositoy)
        self._bg_thread.start()

    @is_project_open
    def commit_repository(self) -> None:
        """"""
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.commit_git_repositoy)
        self._bg_thread.start()

    @is_project_open
    def publish_repository(self) -> None:
        """ """
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = SWWorkflowObject()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.emit_progress.connect(self.update_statusbar)
        self._bg_thread.started.connect(self._bg_worker.publish_github_repositoy)
        self._bg_thread.start()

    def update_statusbar(self, message_: str = "", percent_: int = 0) -> None:
        if percent_ >= 0:
            self.progressbar.setValue(percent_)
            self.statusBar().showMessage(message_)
        else:
            self.progressbar.setFormat(message_)

        if percent_ >= 100:
            self.progressbar.setFormat(message_)

    def update_widgets(self) -> None:
        # Show Menus
        self.findChild(QMenu, "menu_github").setEnabled(self._project.has_github())
        self.findChild(QMenu, "menu_crawler").setEnabled(
            self._project.is_open()
            and (self._project.has_wordpress() or self._project.can_crawl())
        )
        self.findChild(QMenu, "menu_tools").setEnabled(
            self._project.is_open()
            and (self._project.has_wordpress() or self._project.can_crawl())
        )

        # Show Toolbarss
        self.findChild(QToolBar, "toolbar_github").setEnabled(
            self._project.has_github()
        )
        self.findChild(QToolBar, "toolbar_crawler").setEnabled(
            self._project.is_open()
            and (self._project.has_wordpress() or self._project.can_crawl())
        )

        # Show Menubar Icons
        if self._project.src_type == SOURCE.ZIP:
            self.findChild(QAction, "action_crawler_crawl_webpages").setText(
                "&Download Zip File"
            )
            self.findChild(QAction, "action_crawler_crawl_additional_files").setVisible(
                False
            )
        else:
            self.findChild(QAction, "action_crawler_crawl_webpages").setText(
                "&Crawl Webpages"
            )
            self.findChild(QAction, "action_crawler_crawl_additional_files").setVisible(
                self.findChild(QAction, "action_edit_set_expert_mode").isChecked()
            )

        self.findChild(QAction, "action_crawler_crawl_additional_files").setVisible(
            self.findChild(QAction, "action_edit_set_expert_mode").isChecked()
        )

        self.findChild(QAction, "action_project_show_project_settings").setEnabled(
            self._project.is_open()
        )
        self.findChild(QAction, "action_project_close_project").setEnabled(
            self._project.is_open()
        )

        if self._project.is_open():
            self.setWindowTitle(
                f"{self._project.name} - {CONFIGS['APPLICATION_NAME']}  Version - {VERISON}"
            )
        else:
            self.setWindowTitle(f"{CONFIGS['APPLICATION_NAME']}  Version - {VERISON}")


def main():
    app = QApplication(sys.argv)
    wind = SWMainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    pass
