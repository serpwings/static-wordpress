# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/staticwordpress

    src\staticwordpress\gui\editor.py
    
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
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from collections import namedtuple


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtCore import QSize
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWIPythonWidget(RichJupyterWidget):
    def __init__(self, interface_: dict = {}, *args, **kwargs):
        super(SWIPythonWidget, self).__init__(*args, **kwargs)

        self.ipython_kernal_manager = QtInProcessKernelManager()
        self.ipython_kernal_manager.start_kernel()
        self.kernel_client = self.ipython_kernal_manager.client()
        self.kernel_client.start_channels()

        import_custom_modules = ["import requests"]
        for module in import_custom_modules:
            self._execute(module, hidden=True)

        SWInterface = namedtuple("SWInterface", interface_.keys())(**interface_)
        self.ipython_kernal_manager.kernel.shell.push({"iface": SWInterface})

        def stop():
            self.kernel_client.stop_channels()
            self.ipython_kernal_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()

        self.exit_requested.connect(stop)

    def sizeHint(self):
        return QSize(620, 75)
