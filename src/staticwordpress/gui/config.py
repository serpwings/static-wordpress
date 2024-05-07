# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/gui/config.py
    
    Copyright (C) 2020-2024 Faisal Shahzad <info@serpwings.com>

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
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtWidgets import (
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QStyle,
    QTabWidget,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QTextEdit,
    QLabel,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QColorDialog,
)
from PyQt5.QtCore import QSize, QPoint, QRect, QSettings
from PyQt5.QtGui import QPaintEvent, QIcon

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import (
    LANGUAGES,
    REDIRECTS,
    USER_AGENT,
    CONFIGS,
    SHARE_FOLDER_PATH,
    save_configs,
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWConfigTabBar(QTabBar):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        return

    def tabSizeHint(self, index: int) -> QSize:
        s = super().tabSizeHint(index)
        s.transpose()
        return s

    def paintEvent(self, event: QPaintEvent) -> None:
        painter: QStylePainter = QStylePainter(self)
        opt: QStyleOptionTab = QStyleOptionTab()
        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s: QSize = opt.rect.size()
            s.transpose()
            r: QRect = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c: QPoint = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()
        return


class SWConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(SWConfigDialog, self).__init__(parent=parent)
        self.app_configurations = QSettings(
            CONFIGS["APPLICATION_NAME"], CONFIGS["APPLICATION_NAME"]
        )

        self.tabswidget_configs = QTabWidget()
        self.tabswidget_configs.setTabBar(SWConfigTabBar())
        self.tabswidget_configs.setTabPosition(QTabWidget.West)

        self.tab_general = QWidget()
        vbox_layout_general = QVBoxLayout()
        group_box_system = QGroupBox("System")
        form_layout_system = QFormLayout()
        group_box_system.setLayout(form_layout_system)

        vbox_layout_language = QHBoxLayout()
        self.combobox_language = QComboBox()
        self.combobox_language.setFixedWidth(80)
        self.combobox_language.addItems([item.value for item in list(LANGUAGES)])
        vbox_layout_language.addWidget(self.combobox_language)
        vbox_layout_language.addStretch()
        vbox_layout_language.setContentsMargins(0, 0, 0, 0)
        form_layout_system.addRow(QLabel("Language"), vbox_layout_language)

        vbox_layout_scheme = QHBoxLayout()
        self.combobox_scheme = QComboBox()
        self.combobox_scheme.setFixedWidth(80)
        self.combobox_scheme.addItems(CONFIGS["SCHEMES"])
        self.combobox_scheme.setCurrentText(CONFIGS["DEFAULT_SCHEME"])
        vbox_layout_scheme.addWidget(self.combobox_scheme)
        vbox_layout_scheme.addStretch()
        vbox_layout_scheme.setContentsMargins(0, 0, 0, 0)
        form_layout_system.addRow(QLabel("Scheme"), vbox_layout_scheme)

        self.checkbox_clean_url = QCheckBox("")
        self.checkbox_clean_url.setChecked(CONFIGS["CLEAN"]["URL"])
        form_layout_system.addRow("Clean Url", self.checkbox_clean_url)
        self.lineedit_clean_chars = QLineEdit(CONFIGS["CLEAN"]["CHARS"])
        form_layout_system.addRow("Clean Chars", self.lineedit_clean_chars)

        group_box_colors = QGroupBox("Colors")
        form_layout_colors = QFormLayout()
        group_box_colors.setLayout(form_layout_colors)

        vbox_layout_color_success = QHBoxLayout()
        self.pushbutton_color_success = QPushButton("")
        self.pushbutton_color_success.setObjectName("success")
        self.pushbutton_color_success.setFixedWidth(80)
        self.pushbutton_color_success.clicked.connect(self.open_color_dialog)
        self.pushbutton_color_success.setStyleSheet(
            f"background-color: {CONFIGS['COLOR']['SUCCESS']}"
        )
        vbox_layout_color_success.addWidget(self.pushbutton_color_success)
        vbox_layout_color_success.addStretch()
        form_layout_colors.addRow("Success", vbox_layout_color_success)

        vbox_layout_color_warning = QHBoxLayout()
        self.pushbutton_color_warning = QPushButton("")
        self.pushbutton_color_warning.setObjectName("warning")
        self.pushbutton_color_warning.setFixedWidth(80)
        self.pushbutton_color_warning.clicked.connect(self.open_color_dialog)
        self.pushbutton_color_warning.setStyleSheet(
            f"background-color: {CONFIGS['COLOR']['WARNING']}"
        )
        vbox_layout_color_warning.addWidget(self.pushbutton_color_warning)
        vbox_layout_color_warning.addStretch()
        form_layout_colors.addRow("Warning", vbox_layout_color_warning)

        vbox_layout_color_error = QHBoxLayout()
        self.pushbotton_color_error = QPushButton("")
        self.pushbotton_color_error.setObjectName("error")
        self.pushbotton_color_error.setFixedWidth(80)
        self.pushbotton_color_error.clicked.connect(self.open_color_dialog)
        self.pushbotton_color_error.setStyleSheet(
            f"background-color: {CONFIGS['COLOR']['ERROR']}"
        )
        vbox_layout_color_error.addWidget(self.pushbotton_color_error)
        vbox_layout_color_error.addStretch()
        form_layout_colors.addRow("Error", vbox_layout_color_error)

        group_box_search = QGroupBox("Search")
        form_layout_search = QFormLayout()

        layout_search_include = QHBoxLayout()
        self.checkbox_search_content = QCheckBox("Textual Content")
        self.checkbox_search_content.setChecked(CONFIGS["SEARCH"]["INCLUDE"]["CONTENT"])
        self.checkbox_search_iamge = QCheckBox("Feature Image")
        self.checkbox_search_iamge.setChecked(CONFIGS["SEARCH"]["INCLUDE"]["IMAGE"])
        layout_search_include.addWidget(self.checkbox_search_content)
        layout_search_include.addWidget(self.checkbox_search_iamge)
        layout_search_include.addStretch()
        form_layout_search.addRow("Include", layout_search_include)
        self.lineedit_search_html_tags = QLineEdit(
            ",".join(CONFIGS["SEARCH"]["HTML_TAGS"])
        )
        form_layout_search.addRow("HTML Tags", self.lineedit_search_html_tags)

        self.lineedit_search_src = QLineEdit(CONFIGS["SEARCH"]["INDEX"]["src"])
        form_layout_search.addRow("Source File", self.lineedit_search_src)
        self.lineedit_lunar_src = QLineEdit(CONFIGS["LUNR"]["src"])
        form_layout_search.addRow("Lunr JS File", self.lineedit_lunar_src)
        self.lineedit_lunar_integrity = QLineEdit(CONFIGS["LUNR"]["integrity"])
        form_layout_search.addRow("Lunr Integrity", self.lineedit_lunar_integrity)
        group_box_search.setLayout(form_layout_search)

        vbox_layout_general.addWidget(group_box_system)
        vbox_layout_general.addWidget(group_box_colors)
        vbox_layout_general.addWidget(group_box_search)
        vbox_layout_general.addStretch()
        self.tab_general.setLayout(vbox_layout_general)
        self.tabswidget_configs.addTab(self.tab_general, "General")

        self.tab_crawl = QWidget()
        vbox_layout_crawl = QVBoxLayout()

        group_box_user_agent = QGroupBox("User Agents")
        form_layout_user_agent = QFormLayout()
        self.lineedit_user_agent_firefrox = QLineEdit(
            CONFIGS["HEADER"]["FIREFOX"]["User-Agent"]
        )
        form_layout_user_agent.addRow("FireFox", self.lineedit_user_agent_firefrox)
        self.lineedit_user_agent_chrome = QLineEdit(
            CONFIGS["HEADER"]["CHROME"]["User-Agent"]
        )
        form_layout_user_agent.addRow("Chrome", self.lineedit_user_agent_chrome)
        self.lineedit_user_agent_custom = QLineEdit(
            CONFIGS["HEADER"]["CUSTOM"]["User-Agent"]
        )
        form_layout_user_agent.addRow("Custom", self.lineedit_user_agent_custom)
        self.combobox_default_user_agent = QComboBox()
        self.combobox_default_user_agent.setFixedWidth(120)
        self.combobox_default_user_agent.addItems(
            [item.value for item in list(USER_AGENT)]
        )
        self.combobox_default_user_agent.setCurrentText(CONFIGS["DEFAULT_USER_AGENT"])
        form_layout_user_agent.addRow("Default", self.combobox_default_user_agent)
        group_box_user_agent.setLayout(form_layout_user_agent)

        group_box_redirects = QGroupBox("Redirects")
        form_layout_redirects = QFormLayout()

        vbox_layout_redirects_plugins = QHBoxLayout()
        self.combobox_redirects_plugin = QComboBox()
        self.combobox_redirects_plugin.setFixedWidth(120)
        self.combobox_redirects_plugin.addItems(
            [item.value for item in list(REDIRECTS)]
        )
        vbox_layout_redirects_plugins.addWidget(self.combobox_redirects_plugin)
        vbox_layout_redirects_plugins.addStretch()
        vbox_layout_redirects_plugins.setContentsMargins(0, 0, 0, 0)
        form_layout_redirects.addRow("Plugin", vbox_layout_redirects_plugins)
        group_box_redirects.setLayout(form_layout_redirects)

        self.lineedit_redirection_api = QLineEdit(
            CONFIGS["REDIRECTS"][self.combobox_redirects_plugin.currentText()]["API"]
        )
        self.combobox_redirects_plugin.currentIndexChanged.connect(
            self.update_redirects_api
        )
        form_layout_redirects.addRow("API", self.lineedit_redirection_api)

        group_box_simply_static = QGroupBox("Simply Static")
        form_layout_simply_static = QFormLayout()
        self.lineedit_simply_static_api = QLineEdit(CONFIGS["SIMPLYSTATIC"]["API"])
        form_layout_simply_static.addRow("API", self.lineedit_simply_static_api)
        self.lineedit_simply_static_folder = QLineEdit(
            CONFIGS["SIMPLYSTATIC"]["FOLDER"]
        )
        form_layout_simply_static.addRow("Path", self.lineedit_simply_static_folder)
        group_box_simply_static.setLayout(form_layout_simply_static)

        group_box_exclude = QGroupBox("Exclude")
        vbox_layout_exclude = QVBoxLayout()
        self.textedit_exclude = QTextEdit()
        self.textedit_exclude.setObjectName("exclude")
        self.textedit_exclude.setText("\n".join(CONFIGS["EXCLUDE"]))
        vbox_layout_exclude.addWidget(self.textedit_exclude)
        group_box_exclude.setLayout(vbox_layout_exclude)

        vbox_layout_crawl.addWidget(group_box_user_agent)
        vbox_layout_crawl.addWidget(group_box_redirects)
        vbox_layout_crawl.addWidget(group_box_simply_static)
        vbox_layout_crawl.addWidget(group_box_exclude)
        self.tab_crawl.setLayout(vbox_layout_crawl)
        self.tabswidget_configs.addTab(self.tab_crawl, "Crawl")

        self.tab_sitemaps = QWidget()
        sitemap_layout = QVBoxLayout()
        self.checkbox_auto_sitemap_finder = QCheckBox("Auto Sitemap Finder")
        self.checkbox_auto_sitemap_finder.setChecked(CONFIGS["SITEMAP"]["AUTO"])
        sitemap_layout.addWidget(self.checkbox_auto_sitemap_finder)
        sitemap_layout.addWidget(QLabel("Possible Sitemap Locations"))
        self.textedit_sitemap_locations = QTextEdit()
        self.textedit_sitemap_locations.setObjectName("sitemap-locations")
        self.textedit_sitemap_locations.setText(
            "\n".join(CONFIGS["SITEMAP"]["SEARCH_PATHS"])
        )
        sitemap_layout.addWidget(self.textedit_sitemap_locations)
        self.tab_sitemaps.setLayout(sitemap_layout)
        self.tabswidget_configs.addTab(self.tab_sitemaps, "Sitemaps")

        # formats
        self.tab_data_formats = QWidget()
        data_format_layout = QVBoxLayout()

        group_box_image_formats = QGroupBox("Image Formats")
        vbox_layout_image_formats = QVBoxLayout()
        self.textedit_image_formats = QTextEdit()
        self.textedit_image_formats.setObjectName("image-foramts")
        self.textedit_image_formats.setText("\n".join(CONFIGS["FORMATS"]["IMAGE"]))
        vbox_layout_image_formats.addWidget(self.textedit_image_formats)
        group_box_image_formats.setLayout(vbox_layout_image_formats)
        data_format_layout.addWidget(group_box_image_formats)

        group_box_font_formats = QGroupBox("Font Formats")
        vbox_layout_font_formats = QVBoxLayout()
        self.textedit_font_formats = QTextEdit()
        self.textedit_font_formats.setObjectName("image-foramts")
        self.textedit_font_formats.setText("\n".join(CONFIGS["FORMATS"]["FONTS"]))
        vbox_layout_font_formats.addWidget(self.textedit_font_formats)
        group_box_font_formats.setLayout(vbox_layout_font_formats)
        data_format_layout.addWidget(group_box_font_formats)

        self.tab_data_formats.setLayout(data_format_layout)
        self.tabswidget_configs.addTab(self.tab_data_formats, "File Formats")

        # robots.txt
        with open(f"{SHARE_FOLDER_PATH}/robots.txt", "r") as f:
            robots_txt_content = f.read()

        self.tab_robots_txt = QWidget()
        vbox_layout_robots_format = QVBoxLayout()
        self.textedit_robots_txt = QTextEdit()
        self.textedit_robots_txt.setObjectName("robots-txt")
        self.textedit_robots_txt.setText(robots_txt_content)
        vbox_layout_robots_format.addWidget(self.textedit_robots_txt)
        self.tab_robots_txt.setLayout(vbox_layout_robots_format)
        self.tabswidget_configs.addTab(self.tab_robots_txt, "Robots.txt")

        button_box_dialog = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        pushbutton_ok_cancel = button_box_dialog.buttons()
        pushbutton_ok_cancel[0].setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))
        pushbutton_ok_cancel[1].setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))
        button_box_dialog.accepted.connect(self.accept)
        button_box_dialog.rejected.connect(self.reject)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(1, 3, 3, 3)

        self.layout.addWidget(self.tabswidget_configs)
        self.layout.addWidget(button_box_dialog)
        self.setLayout(self.layout)
        self.setFixedWidth(620)
        self.setWindowTitle("Default Configurations")
        self.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))

    def open_color_dialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.sender().setStyleSheet(f"background-color: {color.name()}")
            CONFIGS["COLOR"][self.sender().objectName().upper()] = color.name()

    def update_redirects_api(self):
        self.lineedit_redirection_api.setText(
            CONFIGS["REDIRECTS"][self.combobox_redirects_plugin.currentText()]["API"]
        )

    def accept(self) -> None:
        # General
        CONFIGS["LANGUAGE"] = self.combobox_language.currentText()
        CONFIGS["DEFAULT_SCHEME"] = self.combobox_scheme.currentText()
        CONFIGS["CLEAN"]["URL"] = self.checkbox_clean_url.isChecked()
        CONFIGS["CLEAN"]["CHARS"] = self.lineedit_clean_chars.text()
        CONFIGS["SEARCH"]["INDEX"]["src"] = self.lineedit_search_src.text()
        CONFIGS["SEARCH"]["INCLUDE"][
            "CONTENT"
        ] = self.checkbox_search_content.isChecked()
        CONFIGS["SEARCH"]["INCLUDE"]["IMAGE"] = self.checkbox_search_iamge.isChecked()
        CONFIGS["SEARCH"]["HTML_TAGS"] = self.lineedit_search_html_tags.text().split(
            ","
        )
        CONFIGS["LUNR"]["src"] = self.lineedit_lunar_src.text()
        CONFIGS["LUNR"]["integrity"] = self.lineedit_lunar_integrity.text()

        # Crawl
        redirect_type = self.combobox_redirects_plugin.currentText()
        CONFIGS["REDIRECTS"][redirect_type][
            "API"
        ] = self.lineedit_redirection_api.text()

        CONFIGS["SIMPLYSTATIC"]["API"] = self.lineedit_simply_static_api.text()
        CONFIGS["SIMPLYSTATIC"]["FOLDER"] = self.lineedit_simply_static_folder.text()
        CONFIGS["HEADER"]["CHROME"][
            "User-Agent"
        ] = self.lineedit_user_agent_chrome.text()
        CONFIGS["HEADER"]["CUSTOM"][
            "User-Agent"
        ] = self.lineedit_user_agent_custom.text()
        CONFIGS["HEADER"]["FIREFOX"][
            "User-Agent"
        ] = self.lineedit_user_agent_firefrox.text()

        CONFIGS["DEFAULT_USER_AGENT"] = self.combobox_default_user_agent.currentText()
        CONFIGS["EXCLUDE"] = self.textedit_exclude.toPlainText().split("\n")

        # Sitemap
        CONFIGS["SITEMAP"]["AUTO"] = self.checkbox_auto_sitemap_finder.isChecked()
        CONFIGS["SITEMAP"][
            "SEARCH_PATHS"
        ] = self.textedit_sitemap_locations.toPlainText().split("\n")

        # file formats
        CONFIGS["FORMATS"]["IMAGE"] = self.textedit_image_formats.toPlainText().split(
            "\n"
        )
        CONFIGS["FORMATS"]["FONTS"] = self.textedit_font_formats.toPlainText().split(
            "\n"
        )

        # save/update configs
        save_configs()

        # robots.txt save
        with open(f"{SHARE_FOLDER_PATH}/robots.txt", "w") as f:
            f.write(self.textedit_robots_txt.toPlainText())

        return super().accept()
