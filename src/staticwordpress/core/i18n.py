# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/i18n.py
    
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

import yaml
from pathlib import Path

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from .constants import LANGUAGES, CONFIGS

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class _Translator(dict):
    def __init__(self) -> None:
        super().__init__()
        self._lang = LANGUAGES[CONFIGS["LANGUAGE"]]
        self._path = Path(
            Path(__file__).resolve().parent,
            "..",
            "share",
            "translations.yaml",
        )

    def __call__(self, index: str) -> str:
        assert len(index) > 0
        return self.get(index, {}).get(self._lang.value, index)

    def load(self) -> None:
        with open(self._path, "r", encoding="UTF-8") as f:
            self.update(yaml.load(f.read(), Loader=yaml.CLoader))

    @property
    def language(self) -> LANGUAGES:
        return self._lang

    @language.setter
    def language(self, language_) -> None:
        self._lang = language_


tr = _Translator()
tr.load()
