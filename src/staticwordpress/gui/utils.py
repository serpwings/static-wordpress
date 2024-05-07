# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/gui/utils.py
    
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
# STANDARD LIBARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import logging
import json

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import SHARE_FOLDER_PATH

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

GUI_JSON_PATH = SHARE_FOLDER_PATH / "gui.json"
with GUI_JSON_PATH.open("r") as f:
    GUI_SETTINGS = json.load(f)


def logging_decorator(function):
    def add_logs(cls):
        if function.__doc__:
            logging.info(function.__doc__.split("\n")[0])

        logging.info(f"Start Function: {function.__name__}")
        try:
            function(cls)
            logging.info(f"Stop Function: {function.__name__}")
        except:
            logging.error(f"Failed Function: {function.__name__}")

        logging.info("".join(140 * ["-"]))

    return add_logs
