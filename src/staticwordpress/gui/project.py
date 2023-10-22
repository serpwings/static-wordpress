# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/staticwordpress

    src\staticwordpress\gui\project.py
    
    Copyright (C) 2020-2023 Faisal Shahzad <info@serpwings.com>

<LICENSE_BLOCK>
The contents of this file are subject to version 3 of the 
GNU General Public License (GPL-3.0). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/gpl-3.0.txt
https://github.com/serpwings/staticwordpress/blob/master/LICENSE


Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# STANDARD LIBARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import logging
from pathlib import Path

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtWidgets import (
    QTabWidget,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QLabel,
    QGroupBox,
    QToolButton,
    QButtonGroup,
    QRadioButton,
    QDoubleSpinBox,
    QMessageBox,
    QFileDialog,
    QPushButton,
)
from PyQt5.QtCore import Qt, QSettings, QSize, QThread
from PyQt5.QtGui import QIcon

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import (
    REDIRECTS,
    USER_AGENT,
    CONFIGS,
    SHARE_FOLDER_PATH,
    SOURCE,
    HOST,
)

from ..core.project import Project
from ..core.utils import is_url_valid
from ..gui.workflow import WorkflowGUI

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class ProjectDialog(QDialog):
    def __init__(self, parent, project_, title_="Project Settings"):
        super(ProjectDialog, self).__init__(parent=parent)
        self.appConfigurations = QSettings(
            CONFIGS["APPLICATION_NAME"], CONFIGS["APPLICATION_NAME"]
        )

        self._project = project_
        self._bg_thread = QThread(parent=self)
        self._bg_worker = WorkflowGUI()

        vertical_layout_project = QVBoxLayout()
        groupbox_general_settings = QGroupBox("General Settings")
        form_layout_general_settings = QFormLayout()

        self.lineedit_project_name = QLineEdit(self._project.name)
        self.lineedit_project_name.setObjectName("name")
        form_layout_general_settings.addRow(
            QLabel("Project Name"), self.lineedit_project_name
        )

        self.lineedit_src_url = QLineEdit(self._project.src_url)
        self.lineedit_src_url.setObjectName("src-url")
        form_layout_general_settings.addRow(QLabel("Source Url"), self.lineedit_src_url)

        horizontal_Layout_output_directory = QHBoxLayout()
        self.lineedit_output = QLineEdit(str(self._project.output))
        self.lineedit_output.setObjectName("output")
        self.toolbutton_output_directory = QToolButton()
        self.toolbutton_output_directory.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/three-dots.svg")
        )
        self.toolbutton_output_directory.clicked.connect(self.get_output_directory)
        horizontal_Layout_output_directory.addWidget(self.lineedit_output)
        horizontal_Layout_output_directory.addWidget(self.toolbutton_output_directory)
        form_layout_general_settings.addRow(
            QLabel("Output Directory"), horizontal_Layout_output_directory
        )

        horizontal_layout_crawl_delay_user_agent = QHBoxLayout()
        self.double_spinbox_delay = QDoubleSpinBox()
        self.double_spinbox_delay.setMinimumWidth(120)
        self.double_spinbox_delay.setMinimum(0)
        self.double_spinbox_delay.setSingleStep(0.05)
        self.double_spinbox_delay.setMaximum(2)
        self.double_spinbox_delay.setMinimumWidth(120)
        self.double_spinbox_delay.setValue(self._project.delay)
        self.double_spinbox_delay.setObjectName("delay")
        horizontal_layout_crawl_delay_user_agent.addWidget(self.double_spinbox_delay)

        self.combobox_user_agent = QComboBox()
        self.combobox_user_agent.setObjectName("user-agent")
        self.combobox_user_agent.setMinimumWidth(120)
        self.combobox_user_agent.addItems([item.value for item in list(USER_AGENT)])
        self.combobox_user_agent.setCurrentText(self._project.user_agent.value)
        horizontal_layout_crawl_delay_user_agent.addWidget(QLabel("User Agent"))
        horizontal_layout_crawl_delay_user_agent.addWidget(self.combobox_user_agent)

        form_layout_general_settings.addRow(
            QLabel("Crawl Delay(sec)"), horizontal_layout_crawl_delay_user_agent
        )

        horitzontal_layout_project_type = QHBoxLayout()
        button_group_project_type = QButtonGroup()

        self.radiobutton_seo = QRadioButton("SEO", self)
        self.radiobutton_seo.setObjectName("radio-seo")
        self.radiobutton_seo.setEnabled(False)
        self.radiobutton_seo.toggled.connect(self.update_widgets)

        self.radiobutton_static_website = QRadioButton("Static Website", self)
        self.radiobutton_static_website.setObjectName("radio-static-website")
        self.radiobutton_static_website.setChecked(True)
        self.radiobutton_static_website.toggled.connect(self.update_widgets)

        button_group_project_type.addButton(self.radiobutton_seo)
        button_group_project_type.addButton(self.radiobutton_static_website)

        horitzontal_layout_project_type.addWidget(self.radiobutton_seo)
        horitzontal_layout_project_type.addWidget(self.radiobutton_static_website)
        horitzontal_layout_project_type.addStretch()
        form_layout_general_settings.addRow(
            QLabel("Project Type"), horitzontal_layout_project_type
        )

        groupbox_general_settings.setLayout(form_layout_general_settings)

        widget_static_website_tab = QWidget()
        form_layout_static_website_properties = QFormLayout()

        horizontal_Layout_project_scource = QHBoxLayout()
        self.combobox_source_type = QComboBox()
        self.combobox_source_type.setObjectName("source")
        self.combobox_source_type.setMinimumWidth(120)
        self.combobox_source_type.addItems([item.value for item in list(SOURCE)])
        self.combobox_source_type.setCurrentText(self._project.src_type.value)
        horizontal_Layout_project_scource.addWidget(self.combobox_source_type)
        horizontal_Layout_project_scource.addStretch()

        form_layout_static_website_properties.addRow(
            QLabel("Data Source"), horizontal_Layout_project_scource
        )

        horizontal_Layout_project_redirects = QHBoxLayout()
        self.combobox_redirects = QComboBox()
        self.combobox_redirects.setObjectName("redirects")
        self.combobox_redirects.setMinimumWidth(120)
        self.combobox_redirects.addItems([item.value for item in list(REDIRECTS)])
        self.combobox_redirects.setCurrentText(self._project.redirects.value)

        horizontal_Layout_project_redirects.addWidget(self.combobox_redirects)
        horizontal_Layout_project_redirects.addStretch()
        form_layout_static_website_properties.addRow(
            QLabel("Redirects Source"), horizontal_Layout_project_redirects
        )

        horizontal_Layout_project_destination = QHBoxLayout()
        self.combobox_project_destination = QComboBox()
        self.combobox_project_destination.setObjectName("host")
        self.combobox_project_destination.setMinimumWidth(120)
        self.combobox_project_destination.addItems([item.value for item in list(HOST)])
        self.combobox_project_destination.setCurrentText(self._project.host.value)

        horizontal_Layout_project_destination.addWidget(
            self.combobox_project_destination
        )
        horizontal_Layout_project_destination.addStretch()
        form_layout_static_website_properties.addRow(
            QLabel("Destination Host"), horizontal_Layout_project_destination
        )

        self.lineedit_dest_url = QLineEdit(self._project.dst_url)
        self.lineedit_dest_url.setObjectName("dst-url")
        form_layout_static_website_properties.addRow(
            QLabel("Destination Url"), self.lineedit_dest_url
        )

        self.lineedit_search = QLineEdit(self._project.search)
        self.lineedit_search.setObjectName("search")
        form_layout_static_website_properties.addRow(
            QLabel("Search Page"), self.lineedit_search
        )

        self.lineedit_404_page = QLineEdit(self._project._404)
        self.lineedit_404_page.setObjectName("404-error")
        form_layout_static_website_properties.addRow(
            QLabel("404 Page"), self.lineedit_404_page
        )
        widget_static_website_tab.setLayout(form_layout_static_website_properties)

        horizontal_Layout_sitemap = QHBoxLayout()
        self.lineedit_sitemap = QLineEdit(self._project.sitemap)
        self.lineedit_sitemap.setObjectName("sitemap")
        self.toolbutton_output_sitemap = QToolButton()
        self.toolbutton_output_sitemap.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/search.svg")
        )
        self.toolbutton_output_sitemap.clicked.connect(self.get_sitemap_location)
        horizontal_Layout_sitemap.addWidget(self.lineedit_sitemap)
        horizontal_Layout_sitemap.addWidget(self.toolbutton_output_sitemap)
        form_layout_static_website_properties.addRow(
            QLabel("Sitemap Location"), horizontal_Layout_sitemap
        )

        self.textedit_additional_urls = QTextEdit()
        self.textedit_additional_urls.setText("\n".join(self._project.additional))
        self.textedit_additional_urls.setObjectName("additional")
        self.textedit_exclude_patterns = QTextEdit()
        self.textedit_exclude_patterns.setText("\n".join(self._project.exclude))
        self.textedit_exclude_patterns.setObjectName("exclude")

        widget_project_api_tab = QWidget()
        vertical_layout_project_api = QVBoxLayout()

        groupbox_wp_api = QGroupBox("WordPress")
        form_layout_wp_api = QFormLayout()
        self.lineedit_wp_user = QLineEdit(self._project.wp_user)
        self.lineedit_wp_user.setObjectName("wordpress-user")
        form_layout_wp_api.addRow(QLabel("User Name"), self.lineedit_wp_user)

        self.lineedit_wp_api_token = QLineEdit(self._project.wp_api_token)
        self.lineedit_wp_api_token.setEchoMode(QLineEdit.Password)
        self.lineedit_wp_api_token.setObjectName("wordpress-api-token")

        toolbutton_show_wp_api_token = QToolButton()
        toolbutton_show_wp_api_token.setObjectName("toolbutton_show_wp_api_token")
        toolbutton_show_wp_api_token.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/visibility.svg")
        )
        toolbutton_show_wp_api_token.setCheckable(True)
        toolbutton_show_wp_api_token.clicked.connect(self.change_password_visiblity)

        horizontal_layout_wp_api_token = QHBoxLayout()
        horizontal_layout_wp_api_token.addWidget(self.lineedit_wp_api_token)
        horizontal_layout_wp_api_token.addWidget(toolbutton_show_wp_api_token)

        form_layout_wp_api.addRow(QLabel("API Token"), horizontal_layout_wp_api_token)
        groupbox_wp_api.setLayout(form_layout_wp_api)

        groupbox_gh_api = QGroupBox("GitHub")
        form_layout_gh_api = QFormLayout()

        self.lineedit_gh_repo = QLineEdit(self._project.gh_repo)
        self.lineedit_gh_repo.setObjectName("github-repository")
        form_layout_gh_api.addRow(QLabel("Repository"), self.lineedit_gh_repo)

        self.lineedit_gh_token = QLineEdit(self._project.gh_token)
        self.lineedit_gh_token.setEchoMode(QLineEdit.Password)
        self.lineedit_gh_token.setObjectName("github-token")
        horizontal_layout_gh_token = QHBoxLayout()
        horizontal_layout_gh_token.addWidget(self.lineedit_gh_token)

        toolbutton_show_gh_token = QToolButton()
        toolbutton_show_gh_token.setObjectName("toolbutton_show_gh_token")
        toolbutton_show_gh_token.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/visibility.svg")
        )
        toolbutton_show_gh_token.setCheckable(True)
        toolbutton_show_gh_token.clicked.connect(self.change_password_visiblity)
        horizontal_layout_gh_token.addWidget(toolbutton_show_gh_token)
        form_layout_gh_api.addRow(QLabel("API Token"), horizontal_layout_gh_token)

        groupbox_gh_api.setLayout(form_layout_gh_api)
        vertical_layout_project_api.addWidget(groupbox_wp_api)
        vertical_layout_project_api.addWidget(groupbox_gh_api)

        widget_project_api_tab.setLayout(vertical_layout_project_api)

        self.tabwidget_dialog = QTabWidget()
        self.tabwidget_dialog.addTab(widget_static_website_tab, "Static &Website")
        self.tabwidget_dialog.addTab(widget_project_api_tab, "&API")
        self.tabwidget_dialog.addTab(self.textedit_additional_urls, "Additional &Files")
        self.tabwidget_dialog.addTab(
            self.textedit_exclude_patterns, "Exclude &Patterns"
        )

        vertical_layout_project.addWidget(groupbox_general_settings)
        vertical_layout_project.addWidget(self.tabwidget_dialog)
        vertical_layout_project.addStretch()

        self.pushbutton_verify = QPushButton("&Verify")
        self.pushbutton_verify.setIcon(
            QIcon(f"{SHARE_FOLDER_PATH}/icons/check_project.svg")
        )
        self.pushbutton_verify.clicked.connect(self.check_project)

        self.pushbutton_save = QPushButton("&Save")
        self.pushbutton_save.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))
        self.pushbutton_save.setDefault(True)
        self.pushbutton_save.clicked.connect(self.accept)

        self.pushbutton_cancel = QPushButton("&Cancel")
        self.pushbutton_cancel.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))
        self.pushbutton_cancel.clicked.connect(self.reject)

        horizontal_layout_buttons = QHBoxLayout()
        horizontal_layout_buttons.addWidget(self.pushbutton_verify)
        horizontal_layout_buttons.addStretch()
        horizontal_layout_buttons.addWidget(self.pushbutton_save)
        horizontal_layout_buttons.addWidget(self.pushbutton_cancel)
        vertical_layout_project.addLayout(horizontal_layout_buttons)

        self.setLayout(vertical_layout_project)
        self.setWindowTitle(title_)
        self.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))

    def change_password_visiblity(self):
        if not self.sender().isChecked():
            self.sender().setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/visibility.svg"))
            self.sender().setChecked(False)
            if self.sender().objectName() == "toolbutton_show_gh_token":
                self.lineedit_gh_token.setEchoMode(QLineEdit.Password)
            elif self.sender().objectName() == "toolbutton_show_wp_api_token":
                self.lineedit_wp_api_token.setEchoMode(QLineEdit.Password)

        else:
            self.sender().setIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/visibility_lock.svg")
            )
            self.sender().setChecked(True)
            if self.sender().objectName() == "toolbutton_show_gh_token":
                self.lineedit_gh_token.setEchoMode(QLineEdit.Normal)
            elif self.sender().objectName() == "toolbutton_show_wp_api_token":
                self.lineedit_wp_api_token.setEchoMode(QLineEdit.Normal)

    def update_widgets(self):
        if self.sender().objectName() == "radio-static-website":
            self.tabwidget_dialog.setVisible(True)
            self.setFixedSize(QSize(448, 437))
        elif self.sender().objectName() == "radio-seo":
            self.tabwidget_dialog.setVisible(False)
            self.setFixedSize(QSize(448, 208))
        else:
            pass

    def get_output_directory(self):
        """"""
        output_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            str(self.appConfigurations.value("last-project")),
        )
        if output_directory:
            self.lineedit_output.setText(output_directory)
            self.appConfigurations.setValue("last-project", output_directory)

    def get_sitemap_location(self):
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
        self.lineedit_sitemap.setText(sitemap_location)

    def check_project(self):
        """"""
        # TODO: Add checks for WP_API and Gh_API and if not present then disable them.
        # TODO: Move these checks to background thread
        if not (self.lineedit_wp_api_token.text() and self.lineedit_wp_user.text()):
            self.combobox_redirects.setCurrentText(REDIRECTS.NONE.value)

        if self.lineedit_project_name.text():
            self.lineedit_project_name.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['SUCCESS']}"
            )
        else:
            self.lineedit_project_name.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['ERROR']}"
            )

        if is_url_valid(self.lineedit_src_url.text()):
            self.lineedit_src_url.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['SUCCESS']}"
            )
        else:
            self.lineedit_src_url.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['ERROR']}"
            )

        if self.lineedit_output.text() and Path(self.lineedit_output.text()).is_dir():
            self.lineedit_output.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['SUCCESS']}"
            )
        else:
            self.lineedit_output.setStyleSheet(
                f"background-color: {CONFIGS['COLOR']['ERROR']}"
            )

    def reject(self) -> None:
        if self._bg_thread.isRunning():
            self._bg_thread.quit()
            del self._bg_thread
            del self._bg_worker

        return super().reject()

    def accept(self) -> None:
        """"""

        if self._bg_thread.isRunning():
            self._bg_thread.quit()
            del self._bg_thread
            del self._bg_worker

        if all(
            [
                self.lineedit_project_name.text(),
                self.lineedit_output.text(),
                is_url_valid(self.lineedit_src_url.text()),
                Path(self.lineedit_output.text()).is_dir(),
            ]
        ):
            logging.info(f"Current Project: {self.lineedit_output.text()} is valid")
            logging.info(f"Current Url: {self.lineedit_src_url.text()} is valid")
            logging.info(
                f"Current Project Path: {self.lineedit_output.text()} is valid"
            )

            if not self._project.is_open():
                self._project = Project()
                self._project.create()

            self._project.output = Path(self.lineedit_output.text())
            self._project.path = Path(f"{self._project.output}/._data/.project.json")
            self._project.name = self.lineedit_project_name.text()
            self._project.src_url = self.lineedit_src_url.text()
            self._project.sitemap = self.lineedit_sitemap.text()
            self._project.wp_user = self.lineedit_wp_user.text()
            self._project.wp_api_token = self.lineedit_wp_api_token.text()
            self._project.search = self.lineedit_search.text()
            self._project._404 = self.lineedit_404_page.text()
            self._project.delay = self.double_spinbox_delay.value()
            self._project.redirects = REDIRECTS[self.combobox_redirects.currentText()]
            self._project.src_type = SOURCE[self.combobox_source_type.currentText()]
            self._project.user_agent = USER_AGENT[
                self.combobox_user_agent.currentText()
            ]
            self._project.host = HOST[self.combobox_project_destination.currentText()]
            self._project.dst_url = self.lineedit_dest_url.text()
            self._project.gh_token = self.lineedit_gh_token.text()
            self._project.gh_repo = self.lineedit_gh_repo.text()
            self._project.additional = (
                self.textedit_additional_urls.toPlainText().split("\n")
            )
            self._project.exclude = self.textedit_exclude_patterns.toPlainText().split(
                "\n"
            )
            return super().accept()
        else:
            logging.info(f"Current Project Settings are not valid.")

            msgBox = QMessageBox(parent=self)
            msgBox.setText(
                "Cannot start this project.<br>Please check project settings."
            )
            msgBox.addButton(QMessageBox.Ok).setIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg")
            )
            msgBox.setWindowIcon(
                QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg")
            )
            msgBox.setTextFormat(Qt.RichText)
            msgBox.setWindowTitle(
                "Invalid Project Settings",
            )
            msgBox.exec()
