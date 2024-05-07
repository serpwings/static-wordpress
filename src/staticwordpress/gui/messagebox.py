# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/staticwordpress

    src\staticwordpress\gui\messagebox.py
    
    Copyright (C) 2020-2024 Faisal Shahzad <info@serpwings.com>

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
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import SHARE_FOLDER_PATH


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWMessageBox(QMessageBox):
    def __init__(
        self,
        parent,
        title_: str = "",
        message_: str = "",
        icon_: QMessageBox.Icon = QMessageBox.Question,
        no_button_: bool = True,
    ):
        super(SWMessageBox, self).__init__(parent=parent)

        self.setIcon(icon_)
        self.setWindowTitle(title_)
        self.setText(message_)
        self.pushbutton_ok = self.addButton("OK", QMessageBox.YesRole)
        self.pushbutton_ok.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/ok.svg"))

        if no_button_:
            pushbutton_no = self.addButton("Cancel", QMessageBox.NoRole)
            pushbutton_no.setIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/cancel.svg"))

        self.setDefaultButton(self.pushbutton_ok)
        self.setWindowIcon(QIcon(f"{SHARE_FOLDER_PATH}/icons/static-wordpress.svg"))
        self.setTextFormat(Qt.RichText)
