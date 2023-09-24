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
from pathlib import Path
from datetime import date


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QAction,
    QApplication,
    QDockWidget,
    QWidget,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QFormLayout,
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
    ENUMS_MAP,
    SHARE_FOLDER_PATH,
    HOST,
    REDIRECTS,
    PROJECT,
    SOURCE,
    USER_AGENT,
)
from ..core.project import Project
from ..core.utils import (
    rm_dir_tree,
    get_remote_content,
    extract_urls_from_raw_text,
)
from .workflow import WorkflowGUI
from ..gui.logger import LoggerWidget
from ..gui.rawtext import RawTextWidget
from ..gui.config import ConfigWidget
from ..gui.utils import logging_decorator, GUI_SETTINGS

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class StaticWordPressGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.appConfigurations = QSettings(
            CONFIGS["APPLICATION_NAME"], CONFIGS["APPLICATION_NAME"]
        )
        self.appConfigurations.setValue("icon_path", SHARE_FOLDER_PATH)

        self._project = Project()
        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()

        self.docked_widget_project_properties = QDockWidget("Project Properties", self)
        self.docked_widget_project_properties.setMinimumSize(QSize(400, 100))

        widget_project_properties = QWidget()
        form_layout_project_properties = QFormLayout()

        self.lineedit_project_name = QLineEdit()
        self.lineedit_project_name.setObjectName("name")
        self.lineedit_project_name.textChanged.connect(self.update_windows_title)
        form_layout_project_properties.addRow(
            QLabel("Project Name:"), self.lineedit_project_name
        )

        horizontal_Layout_project_scource = QHBoxLayout()
        self.combobox_source_type = QComboBox()
        self.combobox_source_type.setObjectName("source")
        self.combobox_source_type.currentTextChanged.connect(self.update_windows_title)
        self.combobox_source_type.setMinimumWidth(120)
        self.combobox_source_type.addItems([item.value for item in list(SOURCE)])
        horizontal_Layout_project_scource.addWidget(self.combobox_source_type)
        horizontal_Layout_project_scource.addStretch()
        self.combobox_user_agent = QComboBox()
        self.combobox_user_agent.setObjectName("user-agent")
        self.combobox_user_agent.setMinimumWidth(120)
        self.combobox_user_agent.addItems([item.value for item in list(USER_AGENT)])
        self.combobox_user_agent.currentTextChanged.connect(self.update_windows_title)
        horizontal_Layout_project_scource.addWidget(QLabel("User Agent"))
        horizontal_Layout_project_scource.addWidget(self.combobox_user_agent)
        form_layout_project_properties.addRow(
            QLabel("Project Source"), horizontal_Layout_project_scource
        )
        self.lineedit_src_url = QLineEdit()
        self.lineedit_src_url.setObjectName("src-url")
        self.lineedit_src_url.textChanged.connect(self.update_windows_title)
        form_layout_project_properties.addRow(
            QLabel("Source Url"), self.lineedit_src_url
        )
        self.combobox_project_destination = QComboBox()
        self.combobox_project_destination.setObjectName("host")
        self.combobox_project_destination.currentTextChanged.connect(
            self.update_windows_title
        )

        self.combobox_project_destination.addItems([item.value for item in list(HOST)])
        form_layout_project_properties.addRow(
            QLabel("Destination Host"), self.combobox_project_destination
        )

        self.lineedit_dest_url = QLineEdit()
        self.lineedit_dest_url.setObjectName("dst-url")
        self.lineedit_dest_url.textChanged.connect(self.update_windows_title)
        form_layout_project_properties.addRow(
            QLabel("Destination Url"), self.lineedit_dest_url
        )

        horizontal_Layout_output_directory = QHBoxLayout()
        self.lineedit_output = QLineEdit()
        self.lineedit_output.setObjectName("output")
        self.lineedit_output.textChanged.connect(self.update_windows_title)
        self.toolbutton_output_directory = QToolButton()
        self.toolbutton_output_directory.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/three-dots.svg")
        )
        horizontal_Layout_output_directory.addWidget(self.lineedit_output)
        horizontal_Layout_output_directory.addWidget(self.toolbutton_output_directory)
        self.toolbutton_output_directory.clicked.connect(self.get_output_directory)
        form_layout_project_properties.addRow(
            QLabel("Output Directory"), horizontal_Layout_output_directory
        )

        vertical_layout_additional_properties = QVBoxLayout()
        vertical_layout_additional_properties.addLayout(form_layout_project_properties)
        widget_project_properties.setLayout(vertical_layout_additional_properties)
        self.docked_widget_project_properties.setWidget(widget_project_properties)
        self.docked_widget_project_properties.setFeatures(
            QDockWidget.NoDockWidgetFeatures
        )

        self.docked_widget_project_properties.setMaximumHeight(200)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked_widget_project_properties)

        # =============================
        # Github Properties dock
        # =============================
        self.docked_widget_github_properties = QDockWidget("Github Setttings", self)
        self.docked_widget_github_properties.setMaximumHeight(100)

        widget_github_properties = QWidget()
        form_layout_github_properties = QFormLayout()

        self.lineedit_gh_repo = QLineEdit()
        self.lineedit_gh_repo.setObjectName("github-repository")
        self.lineedit_gh_repo.textChanged.connect(self.update_windows_title)
        form_layout_github_properties.addRow(
            QLabel("Repository Name"), self.lineedit_gh_repo
        )
        self.lineedit_gh_token = QLineEdit()
        self.lineedit_gh_token.setObjectName("github-token")
        self.lineedit_gh_token.textChanged.connect(self.update_windows_title)
        form_layout_github_properties.addRow(
            QLabel("GitHub Token"), self.lineedit_gh_token
        )

        vertical_layout_github_properties = QVBoxLayout()
        vertical_layout_github_properties.addLayout(form_layout_github_properties)
        widget_github_properties.setLayout(vertical_layout_github_properties)
        self.docked_widget_github_properties.setWidget(widget_github_properties)
        self.docked_widget_github_properties.setFeatures(
            QDockWidget.NoDockWidgetFeatures
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked_widget_github_properties)

        # =============================
        # Crawl Properties dock
        # =============================
        self.docked_widget_crawl_properties = QDockWidget("Crawl Settings", self)
        self.docked_widget_crawl_properties.setMinimumSize(QSize(400, 100))

        widget_crawl_properties = QWidget()
        form_layout_crawl_properties = QFormLayout()

        horizontal_Layout_wordpress = QHBoxLayout()
        self.lineedit_wp_user = QLineEdit()
        self.lineedit_wp_user.setMaximumWidth(80)
        self.lineedit_wp_user.setObjectName("wordpress-user")
        self.lineedit_wp_user.textChanged.connect(self.update_windows_title)
        horizontal_Layout_wordpress.addWidget(self.lineedit_wp_user)
        self.lineedit_wp_api_token = QLineEdit()
        self.lineedit_wp_api_token.setObjectName("wordpress-api-token")
        self.lineedit_wp_api_token.textChanged.connect(self.update_windows_title)
        horizontal_Layout_wordpress.addWidget(QLabel("API Token"))
        horizontal_Layout_wordpress.addWidget(self.lineedit_wp_api_token)
        form_layout_crawl_properties.addRow(
            QLabel("WordPress User"), horizontal_Layout_wordpress
        )

        horizontal_Layout_redirects = QHBoxLayout()
        self.combobox_redirects = QComboBox()
        self.combobox_redirects.setObjectName("redirects")
        self.combobox_redirects.currentTextChanged.connect(self.update_windows_title)
        self.combobox_redirects.addItems([item.value for item in list(REDIRECTS)])
        horizontal_Layout_redirects.addWidget(self.combobox_redirects)
        form_layout_crawl_properties.addRow(
            QLabel("Redirects Source"), horizontal_Layout_redirects
        )

        horizontal_Layout_sitemap = QHBoxLayout()
        self.lineedit_sitemap = QLineEdit()
        self.lineedit_sitemap.setObjectName("sitemap")
        self.lineedit_sitemap.textChanged.connect(self.update_windows_title)
        self.toolbutton_output_sitemap = QToolButton()
        self.toolbutton_output_sitemap.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/search.svg")
        )
        horizontal_Layout_sitemap.addWidget(self.lineedit_sitemap)
        horizontal_Layout_sitemap.addWidget(self.toolbutton_output_sitemap)
        self.toolbutton_output_sitemap.clicked.connect(self.get_sitemap_location)
        form_layout_crawl_properties.addRow(
            QLabel("Sitemap Location"), horizontal_Layout_sitemap
        )

        horizontal_Layout_search_404 = QHBoxLayout()
        self.lineedit_search = QLineEdit()
        self.lineedit_search.setObjectName("search")
        self.lineedit_search.textChanged.connect(self.update_windows_title)
        horizontal_Layout_search_404.addWidget(self.lineedit_search)
        horizontal_Layout_search_404.addWidget(QLabel("404 Page"))
        self.lineedit_404_page = QLineEdit()
        self.lineedit_404_page.setObjectName("404-error")
        self.lineedit_404_page.textChanged.connect(self.update_windows_title)
        horizontal_Layout_search_404.addWidget(self.lineedit_404_page)
        form_layout_crawl_properties.addRow(
            QLabel("Search Page"), horizontal_Layout_search_404
        )

        self.lineedit_delay = QLineEdit()
        self.lineedit_delay.setObjectName("delay")
        self.lineedit_delay.textChanged.connect(self.update_windows_title)
        form_layout_crawl_properties.addRow(
            QLabel("Delay (Seconds)"), self.lineedit_delay
        )

        form_layout_crawl_properties.addRow(QLabel("Additional Files"))
        self.textedit_additional = QTextEdit()
        self.textedit_additional.setObjectName("additional")
        self.textedit_additional.textChanged.connect(self.update_windows_title)
        form_layout_crawl_properties.addRow(self.textedit_additional)

        form_layout_crawl_properties.addRow(QLabel("Exclude Patterns"))
        self.textedit_exclude = QTextEdit()
        self.textedit_exclude.setObjectName("exclude")
        self.textedit_exclude.textChanged.connect(self.update_windows_title)
        form_layout_crawl_properties.addRow(self.textedit_exclude)

        vertical_layout_wp_properties = QVBoxLayout()
        vertical_layout_wp_properties.addLayout(form_layout_crawl_properties)
        widget_crawl_properties.setLayout(vertical_layout_wp_properties)
        self.docked_widget_crawl_properties.setWidget(widget_crawl_properties)
        self.docked_widget_crawl_properties.setFeatures(
            QDockWidget.NoDockWidgetFeatures
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked_widget_crawl_properties)

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

    @is_new_project
    @logging_decorator
    def get_output_directory(self):
        """"""
        output_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.appConfigurations.value("output-directory"),
        )
        if output_directory:
            self.lineedit_output.setText(output_directory)
            self.appConfigurations.setValue("output-directory", output_directory)

    @is_project_open
    @logging_decorator
    def clean_output_directory(self):
        """Clean Output Directory"""
        reply = QMessageBox.question(
            self,
            "Clean Output Folder Content",
            f"Existing content in Output folder will be delete?\n {self._project.output}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            rm_dir_tree(self._project.output)
            logging.info(
                f"Content of output folder at {self._project.output} are deleted"
            )

    @is_new_project
    @logging_decorator
    def get_sitemap_location(self):
        """ """
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_thread.started.connect(self._bg_worker.find_sitemap)
        self._bg_worker.signalSitemapLocation.connect(self.update_sitemap_location)
        self._bg_thread.start()

    def update_sitemap_location(self, sitemap_location):
        self._project.sitemap = sitemap_location
        logging.info(f"Found Sitemap location: {sitemap_location}")
        self.update_properties_widgets()

    @is_new_project
    @logging_decorator
    def extract_url_from_raw_text(self):
        rtp = RawTextWidget(
            src_url=self._project.src_url, dest_url=self._project.dst_url
        )
        if rtp.exec_():
            raw_text = rtp.textedit_raw_text_with_links.toPlainText()
            current_additional_urls = self.textedit_additional.toPlainText().split("\n")

            if raw_text:
                new_additional_links = extract_urls_from_raw_text(
                    raw_text, rtp.lineedit_dest_url.text(), rtp.linedit_src_url.text()
                )
                logging.info(f" {len(new_additional_links)} Additional Urls Found")
                current_additional_urls += new_additional_links
                self.textedit_additional.setText(
                    "\n".join(set(current_additional_urls))
                )

    @is_new_project
    @logging_decorator
    def clear_cache(self):
        """Clearing Crawl Cache"""
        logging.info(f"Clearing Crawl Cache")
        get_remote_content.cache_clear()

    def closeEvent(self, event):
        """ """
        reply = QMessageBox.question(
            self,
            "Exiting static-wordpress",
            "Do you really want to exit?.\nAny unsaved changes will be lost!",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
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
        w = ConfigWidget()
        if w.exec_():
            logging.info("Saved/Updated Default Configurations")

    def about(self):
        """ """
        msgBox = QMessageBox()
        msgBox.setText(
            f"Copyright {date.today().year} - SERP Wings"
            f"<br><br>{CONFIGS['APPLICATION_NAME']} Version - {VERISON}"
            "<br><br>This work is an opensource project under <br>GNU General Public License v3 or later (GPLv3+)"
            f"<br>More Information at <a href='https://{CONFIGS['ORGANIZATION_DOMAIN']}/'>{CONFIGS['ORGANIZATION_NAME']}</a>"
        )
        msgBox.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        msgBox.setTextFormat(Qt.RichText)
        msgBox.setWindowTitle("About Us")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    @logging_decorator
    def create_project(self):
        """Closing current project will automatically start a new project."""
        self.close_project()
        self._project.create()
        self.update_properties_widgets()

    @logging_decorator
    def open_project(self):
        """Opening static-wordpress Project File"""
        self.close_project()
        if not self._project.is_open():
            options = QFileDialog.Options()
            project_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Static-WordPress Project File",
                self.appConfigurations.value("last-project"),
                "JSON Files (*.json)",
                options=options,
            )

            if project_path:
                self._project.open(Path(project_path))

                if self._project.is_open():
                    if not self._project.is_older_version():
                        logging.warning(
                            f"Your Project was saved with an older version : {self._project.version}."
                        )
                    logging.info(f"Open Project {self._project.path} Successfully")
                    self.appConfigurations.setValue("last-project", project_path)
            else:
                msgBox = QMessageBox()
                msgBox.setText(f"Project cannot be opened." f"Please try again.")
                msgBox.setWindowIcon(
                    QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
                )
                msgBox.setTextFormat(Qt.RichText)
                msgBox.setWindowTitle("Open Project")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()

                logging.info(
                    "No New Project Opened. Unsaved project properties will be lost."
                )

        self.update_windows_title()
        self.update_properties_widgets()

    @is_project_open
    @logging_decorator
    def close_project(self):
        """Assign new project and old properties will be lost.
        Default is assigned as CLOSED project
        """
        reply = QMessageBox.question(
            self,
            "Close Existing Project",
            "Are you sure to close current project and open new one?.\n All existing project properties will be lost!",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._project = Project()
            self.update_properties_widgets()
            verifications = {
                "name": None,
                "src-url": None,
                "wordpress-user": None,
                "wordpress-api-token": None,
                "sitemap": None,
                "github-token": None,
                "github-repository": None,
            }
            self.update_expert_mode_widgets(verifications)

    @is_project_open
    @logging_decorator
    def save_project(self):
        """Saving Current static-wordpress Project"""
        if self.lineedit_project_name.text():
            new_project_path = self.appConfigurations.value("last-project")
            if self._project.is_new():
                options = QFileDialog.Options()
                new_project_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Select StaticWordPress Project File",
                    self.appConfigurations.value("last-project"),
                    "JSON Files (*.json)",
                    options=options,
                )
                if new_project_path:
                    self._project.path = Path(new_project_path)
                else:
                    return

            self.appConfigurations.setValue("last-project", new_project_path)
            self._project.name = self.lineedit_project_name.text()
            self._project.path = Path(new_project_path)
            self._project.src_url = self.lineedit_src_url.text()
            self._project.sitemap = self.lineedit_sitemap.text()
            self._project.wp_user = self.lineedit_wp_user.text()
            self._project.wp_api_token = self.lineedit_wp_api_token.text()
            self._project.search = self.lineedit_search.text()
            self._project._404 = self.lineedit_404_page.text()
            self._project.delay = float(self.lineedit_delay.text())
            self._project.redirects = REDIRECTS[self.combobox_redirects.currentText()]
            self._project.src_type = SOURCE[self.combobox_source_type.currentText()]
            self._project.user_agent = USER_AGENT[
                self.combobox_user_agent.currentText()
            ]
            self._project.host = HOST[self.combobox_project_destination.currentText()]
            self._project.output = Path(self.lineedit_output.text())
            self._project.dst_url = self.lineedit_dest_url.text()
            self._project.gh_token = self.lineedit_gh_token.text()
            self._project.gh_repo = self.lineedit_gh_repo.text()
            self._project.additional = self.textedit_additional.toPlainText().split(
                "\n"
            )
            self._project.exclude = self.textedit_exclude.toPlainText().split("\n")
            if not self._project.is_older_version():
                logging.warning(
                    f"Your Project will be saved with new version number : {VERISON}."
                )
                self._project.version = VERISON

            # save project
            self._project.save()
            if self._project.is_saved():
                logging.info(f"Project Saved Successfully at {self._project.path}")
                self.update_properties_widgets()
                self.update_windows_title()

    def check_project(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalVerification.connect(self.update_expert_mode_widgets)
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
        self._bg_thread.started.connect(self._bg_worker.verify_project)
        self._bg_thread.start()

    @is_project_open
    def start_batch_process(self):
        """Start Crawling"""
        if not self._project.output.exists():
            reply = QMessageBox.question(
                self,
                f"Output Folder",
                f"Following Output Folder doesnt not exit?.\n{self._project.output}\nDo You want to create it now?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
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
                    reply = QMessageBox.question(
                        self,
                        f"ZIP File Missing",
                        f"ZIP File not found. Please check your project configurations?",
                        QMessageBox.Yes,
                    )
                    if reply == QMessageBox.Yes:
                        return

            self._bg_thread = QThread(parent=self)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
            self._bg_thread.started.connect(self._bg_worker.batch_processing)
            self._bg_thread.start()

    @is_project_open
    def stop_process(self) -> None:
        if self._bg_worker.is_running():
            reply = QMessageBox.question(
                self,
                "Stop Crawling Process",
                "Do you really want to Stop Crawling Thrad?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self._bg_worker.stop_calcualations()
                self.update_statusbar_widgets("Stoping Processing", 100)

    @is_project_open
    def crawl_website(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()

        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()
        self._bg_worker.set_project(project_=self._project)
        self._bg_worker.moveToThread(self._bg_thread)
        self._bg_thread.finished.connect(self._bg_worker.deleteLater)
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
        self._bg_thread.started.connect(self._bg_worker.create_github_repositoy)
        self._bg_thread.start()

    @is_project_open
    def delete_github_repository(self) -> None:
        """"""
        reply = QMessageBox.question(
            self,
            "Deleting Repository on GitHub",
            f"Do you really want to delete {self._project.gh_repo} on GitHub?\nThis deletion is not reversible.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self._bg_thread.isRunning():
                self._bg_thread.quit()

            self._bg_worker = WorkflowGUI()
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.set_project(project_=self._project)
            self._bg_worker.moveToThread(self._bg_thread)
            self._bg_thread.finished.connect(self._bg_worker.deleteLater)
            self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
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
        self._bg_worker.signalProgress.connect(self.update_statusbar_widgets)
        self._bg_thread.started.connect(self._bg_worker.publish_github_repositoy)
        self._bg_thread.start()

    def update_statusbar_widgets(self, message_, percent_) -> None:
        if percent_ >= 0:
            self.progressBar.setValue(percent_)
            self.statusBar().showMessage(message_)
        else:
            self.progressBar.setFormat(message_)

        if percent_ >= 100:
            self.progressBar.setFormat(message_)

    def update_properties_widgets(self) -> None:
        self.lineedit_project_name.setText(self._project.name)
        self.lineedit_src_url.setText(self._project.src_url)
        self.lineedit_sitemap.setText(self._project.sitemap)
        self.lineedit_search.setText(self._project.search)
        self.lineedit_404_page.setText(self._project._404)
        self.lineedit_delay.setText(f"{self._project.delay}")
        self.combobox_source_type.setCurrentText(self._project.src_type.value)
        self.combobox_user_agent.setCurrentText(self._project.user_agent.value)
        self.lineedit_output.setText(str(self._project.output))
        self.lineedit_dest_url.setText(self._project.dst_url)
        self.lineedit_wp_user.setText(self._project.wp_user)
        self.lineedit_wp_api_token.setText(self._project.wp_api_token)
        self.lineedit_gh_token.setText(self._project.gh_token)
        self.lineedit_gh_repo.setText(self._project.gh_repo)
        self.textedit_additional.setText("\n".join(self._project.additional))
        self.textedit_exclude.setText("\n".join(self._project.exclude))
        self.combobox_redirects.setCurrentText(self._project.redirects.value)
        self.combobox_redirects.setEnabled(True)

        self.findChild(QMenu, "menu_github").setEnabled(self._project.has_github())
        self.findChild(QMenu, "menu_wordpress").setEnabled(
            self._project.has_wordpress()
        )
        self.findChild(QToolBar, "toolbar_github").setEnabled(
            self._project.has_github()
        )
        self.findChild(QToolBar, "toolbar_wordpres").setEnabled(
            self._project.has_wordpress()
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

    def update_expert_mode_widgets(self, verifications) -> None:
        for key, value in verifications.items():
            if value is not None:
                bg_color = (
                    CONFIGS["COLOR"]["SUCCESS"] if value else CONFIGS["COLOR"]["ERROR"]
                )
            else:
                bg_color = value

            self.findChild(QLineEdit, key).setStyleSheet(
                f"background-color: {bg_color}"
            )

    def update_windows_title(self) -> None:
        sender = self.sender()
        if (
            type(sender) in [QLineEdit, QComboBox, QTextEdit]
            and self._project.is_open()
        ):
            gui_value = sender.property("text")

            if type(sender) == QLineEdit:
                gui_value = sender.property("text")
                if sender.objectName() == "output":
                    gui_value = Path(sender.property("text"))
                elif sender.objectName() == "delay":
                    try:
                        gui_value = float(sender.property("text"))
                    except:  # mostly value error e.g. 0.^ as input
                        pass

            elif type(sender) == QComboBox:
                gui_value = ENUMS_MAP[sender.objectName()][
                    sender.property("currentText")
                ]
            elif type(sender) == QTextEdit:
                gui_value = [url for url in sender.toPlainText().split("\n") if url]

            project_value = self._project.get(sender.objectName())
            project_functions_dict = {
                "github-repository": self._project.gh_repo,
                "github-token": self._project.gh_token,
                "wordpress-user": self._project.wp_user,
                "wordpress-api-token": self._project.wp_api_token,
                "src-url": self._project.src_url,
                "source": self._project.src_type,
                "output": self._project.output,
                "dst-url": self._project.dst_url,
                "404-error": self._project._404,
            }

            if sender.objectName() in project_functions_dict:
                project_value = project_functions_dict[sender.objectName()]

            if gui_value != project_value and not self._project.is_new():
                self._project.status = PROJECT.UPDATE

        status_string = (
            f"{'' if self._project.is_saved() else '*'} {self._project.name}"
        )
        new_window_title = (
            f"{status_string} - {CONFIGS['APPLICATION_NAME']}  Version - {VERISON}"
        )
        if self._project.status == PROJECT.NOT_FOUND:
            new_window_title = f"{CONFIGS['APPLICATION_NAME']} Version - {VERISON}"

        self.setWindowTitle(new_window_title)


def main():
    app = QApplication(sys.argv)
    wind = StaticWordPressGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    pass
