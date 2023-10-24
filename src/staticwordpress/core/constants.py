# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/constants.py
    
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

import re
import json
from pathlib import Path
from enum import Enum

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONSTANTS LIST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_REVISION = 4
VERISON = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_REVISION}"

SHARE_FOLDER_PATH = Path(
    Path(__file__).resolve().parent,
    "..",
    "share",
)

LINK_REGEX = re.compile(
    "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)",
    re.DOTALL,
)

CONFIG_PATH = SHARE_FOLDER_PATH / "config.json"
with CONFIG_PATH.open("r") as f:
    CONFIGS = json.load(f)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


def save_configs():
    with CONFIG_PATH.open("w") as f:
        json.dump(CONFIGS, f, indent=4)


class ExtendedEnum(Enum):
    """An extended enum class to convert list of items in an enumration."""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class PROJECT(Enum):
    """An enum for the different project operations."""

    NEW = "NEW"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    SAVED = "SAVED"
    UPDATE = "UPDATE"
    NOT_FOUND = "NOT_FOUND"


class HOST(ExtendedEnum):
    """An enum for the different Hostings."""

    NETLIFY = "NETLIFY"
    # CLOUDFLARE = "CLOUDFLARE"
    # LOCALHOST = "LOCALHOST"


class URL(ExtendedEnum):
    """Supported URL types"""

    NONE = "NONE"
    BINARY = "BINARY"
    IMAGE = "IMAGE"
    PDF = "PDF"
    HTML = "HTML"
    JS = "JS"
    CSS = "CSS"
    TXT = "TXT"  # robots.txt
    XML = "XML"  # sitemap
    JSON = "JSON"
    FOLDER = "FOLDER"
    HOME = "HOME"
    FONTS = "FONTS"
    ZIP = "ZIP"


class LANGUAGES(ExtendedEnum):
    """Supported languages"""

    en_US = "en_US"
    de_DE = "de_DE"


class SOURCE(ExtendedEnum):
    """List of Data Sources"""

    CRAWL = "CRAWL"
    ZIP = "ZIP"


class REDIRECTS(ExtendedEnum):
    """Redirection Sources"""

    NONE = "NONE"  # Do not include Redirects
    REDIRECTION = "REDIRECTION"  # redirects Plugin from WP Plugin Repository


class USER_AGENT(ExtendedEnum):
    """Crawlers"""

    FIREFOX = "FIREFOX"
    CHROME = "CHROME"
    CUSTOM = "CUSTOM"


# Dict with enumeration mapping
ENUMS_MAP = {
    "redirects": REDIRECTS,
    "host": HOST,
    "source": SOURCE,
    "user-agent": USER_AGENT,
}
