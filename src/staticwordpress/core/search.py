# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/search.py
    
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

import shutil
import json
from pathlib import Path, PurePosixPath

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.utils import get_clean_url, string_formatter
from ..core.constants import CONFIGS, SHARE_FOLDER_PATH

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Search:
    """Class to Geneate Search from HTML documents"""

    def __init__(self, search_page_: Path = None, dst_url_="") -> None:
        """Intilialize with Path of Search Page as HTML

        Args:
            search_page_ (Path, optional): Search Page Path.
            dst_url_ (str, optional): Desitnation Url where Search Will be hosted".
        """
        self._search_index = []
        self._search_path = search_page_
        self._search_path_lunr = Path(f"{search_page_}/lunr.json")
        self._search_path_script = Path(
            f"{search_page_}/{CONFIGS['SEARCH']['INDEX']['src']}"
        )
        self._dst_url = dst_url_

    def update(self, soup_: BeautifulSoup, output_path_: str) -> None:
        """Update search page by adding new tags

        Args:
            soup_ (BeautifulSoup): Soup of the HTML Page
            output_path_ (str | Path): Save location for Search Index Page
        """
        lunr_script_tag = [
            soup_.new_tag(
                "script",
                src=CONFIGS["LUNR"]["src"],
                integrity=CONFIGS["LUNR"]["integrity"],
                crossorigin=CONFIGS["LUNR"]["crossorigin"],
                referrerpolicy=CONFIGS["LUNR"]["referrerpolicy"],
            ),
            soup_.new_tag(
                "script",
                src=CONFIGS["SEARCH"]["INDEX"]["src"],
            ),
        ]

        for script in lunr_script_tag:
            soup_.find("head").append(str(script))

        # TODO: In future add support for minification check
        content = soup_.prettify(formatter=HTMLFormatter(string_formatter))

        with open(output_path_, "w", encoding="utf-8") as f:
            f.write(content)

    def add(self, soup_: BeautifulSoup, url_path_: str) -> None:
        """Add new (as soup) page to search indexs

        Args:
            soup_ (BeautifulSoup): Soup of the HTML Page
            url_path_ (str): URL of the HTML page
            make_text (bool): If True then Text from Page is included in Search
        """
        clean_url = get_clean_url(self._dst_url, str(PurePosixPath(url_path_)))
        title = soup_.find("title")

        if title and clean_url:
            all_text_content = soup_.body.find_all(CONFIGS["SEARCH"]["HTML_TAGS"])

            # TODO: need more cleaning here
            search_text = " ".join(
                [text for _t in all_text_content for text in _t.strings]
            )

            # update search index array
            # TODO: include feature images
            self._search_index.append(
                {
                    "title": title.string,
                    "content": search_text
                    if CONFIGS["SEARCH"]["INCLUDE"]["CONTENT"]
                    else title.string,
                    "href": clean_url,
                }
            )

    def copy_scripts(self):
        """Copy Search.js into search folder"""
        src = Path(f'{SHARE_FOLDER_PATH}/{CONFIGS["SEARCH"]["INDEX"]["src"]}')
        if src.exists():
            shutil.copyfile(src, self._search_path_script)

    def save(self) -> None:
        """Save Search Index as Json File into Lunr.json"""
        if self._search_path.is_dir():
            with open(self._search_path_lunr, "w", encoding="utf-8") as fl:
                json.dump(self._search_index, fl, indent=4, ensure_ascii=False)
