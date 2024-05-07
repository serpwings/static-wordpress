# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/crawler.py
    
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

import re
import hashlib
import json
from urllib import parse
from pathlib import Path

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import requests
from requests import PreparedRequest
from requests.structures import CaseInsensitiveDict

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.utils import get_mock_response, get_remote_content, get_clean_url
from ..core.constants import CONFIGS, URL, LINK_REGEX

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Crawler:
    def __init__(self, loc_: str, typ_: URL = URL.FOLDER, scheme_: str = "") -> None:
        loc_ = parse.unquote(loc_).replace("\/", "/")
        if not any([loc_.startswith(f"{scheme}://") for scheme in CONFIGS["SCHEMES"]]):
            loc_ = f"{CONFIGS['DEFAULT_SCHEME']}://{loc_}"

        if CONFIGS["CLEAN"]["URL"]:
            loc_ = get_clean_url(loc_, "", scheme_)

        self._typ = typ_
        self._loc = loc_
        self._urlparse = parse.urlparse(self._loc)

        file_ext = self._urlparse.path.split(".")[-1].upper()
        if file_ext:
            for keys in CONFIGS["FORMATS"]:
                if file_ext in CONFIGS["FORMATS"][keys]:
                    self._typ = URL[keys]

        if any(
            [exclule_url in self._urlparse.path for exclule_url in CONFIGS["EXCLUDE"]]
        ):
            self._typ = URL.NONE

        if self._typ == URL.FOLDER:
            self._loc = (
                f"{self._loc}{'/' if not self._urlparse.path.endswith('/') else ''}"
            )
            self._urlparse = parse.urlparse(self._loc)

        self._response = get_mock_response(url_=self._urlparse)
        self._internal_links = []
        self._externals_links = []
        self._hash = hashlib.sha256(self._loc.encode("utf-8")).hexdigest()

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def typ(self) -> str:
        return self._typ

    @property
    def external_links(self) -> list:
        return self._externals_links

    @property
    def internal_links(self) -> list:
        return self._internal_links

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def loc(self) -> str:
        return self._loc

    @property
    def scheme(self) -> str:
        return self._urlparse.scheme

    @property
    def netloc(self) -> str:
        return self._urlparse.netloc

    @property
    def path(self) -> str:
        return self._urlparse.path

    @property
    def params(self) -> str:
        return self._urlparse.params

    @property
    def fragment(self) -> str:
        return self._urlparse.fragment

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def elapsed(self) -> float:
        return self._response.elapsed

    @property
    def encoding(self) -> str:
        return self._response.encoding

    @property
    def headers(self):  # -> CaseInsensitiveDict[str]:
        return self._response.headers

    @property
    def history(self) -> list:
        return self._response.history

    @property
    def is_permanent_redirect(self) -> bool:
        return self._response.is_permanent_redirect

    @property
    def is_redirect(self) -> bool:
        return self._response.is_redirect

    @property
    def ok(self) -> bool:
        return self._response.ok

    @property
    def reason(self) -> str:
        return self._response.reason

    @property
    def request(self) -> PreparedRequest:
        return self._response.request

    @property
    def text(self) -> str:
        return self._response.text

    @property
    def url(self) -> str:
        return self._response.url

    @property
    def redirects_chain(self) -> list:
        return [history.url for history in self._response.history]

    @property
    def is_valid(self) -> bool:
        return all(
            [
                len(self._urlparse.scheme) > 0,
                len(self._urlparse.netloc) > 0,
                len(self._urlparse.netloc.split(".")) > 1,
                len(self._urlparse.path) > 0 or self._typ == URL.HOME,
            ]
        )

    def update_scheme(self, new_schema: str = "https") -> None:
        self._loc = self._loc.replace(self._urlparse.scheme, new_schema)
        self._urlparse = parse.urlparse(self._loc)
        self._hash = hashlib.sha256(self._loc.encode("utf-8")).hexdigest()

    def fetch(self) -> None:
        if self.is_valid:
            self._response = get_remote_content(self._urlparse)

            if self._typ in [URL.FOLDER, URL.HTML, URL.JS, URL.HOME]:
                extracted_urls = set(
                    [link[0] for link in re.findall(LINK_REGEX, self._response.text)]
                )

                self._internal_links = [
                    url for url in extracted_urls if self._urlparse.netloc in url
                ]
                self._externals_links = [
                    url for url in extracted_urls if self._urlparse.netloc not in url
                ]

    def save(self, full_output_folder: Path, dst_url: str = "") -> str:
        folder_path = (
            Path(self.path[1:]) if self.path.startswith("/") else Path(self.path)
        )

        full_output_path = Path(f"{full_output_folder}/{folder_path}")

        if self._response.status_code == 404:
            self._typ = URL.HTML
            full_output_path = full_output_folder / Path("404.html")

        if self._typ in [URL.FOLDER, URL.HOME]:
            full_output_path = full_output_path / Path("index.html")

        if self._typ not in [URL.NONE]:
            full_output_path.parent.mkdir(parents=True, exist_ok=True)

        if self._typ in [
            URL.HTML,
            URL.XML,
            URL.FOLDER,
            URL.JS,
            URL.CSS,
            URL.TXT,
            URL.HOME,
        ]:
            _text = self._response.text
            if dst_url:
                dest_url_parse = parse.urlparse(dst_url)
                _text = self._response.text.replace(
                    f"{self._urlparse.scheme}://{self._urlparse.netloc}",
                    f"{dest_url_parse.scheme}://{dest_url_parse.netloc}",
                )
                _text = _text.replace(self._urlparse.netloc, dest_url_parse.netloc)

            with open(full_output_path, "w", encoding="utf-8") as f:
                f.write(_text)

        elif self._typ in [URL.IMAGE, URL.PDF, URL.BINARY]:
            with open(full_output_path, "wb") as file:
                file.write(self._response.content)

        elif self._typ in [URL.JSON]:
            with open(full_output_path, "w", encoding="utf-8") as file:
                json.dump(json.loads(self._response.text), file, indent=4)

        elif self._typ == URL.ZIP:
            headers = CaseInsensitiveDict()
            headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"

            current_session = requests.session()
            response = current_session.get(self._loc, headers=headers)

            if response.status_code == 200:
                with open(full_output_path, "wb") as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)
            current_session.cookies.clear()

        elif self._typ == URL.FONTS:
            totalbits = 0
            if self._response.status_code == 200:
                with open(full_output_path, "wb") as f:
                    for chunk in self._response.iter_content(chunk_size=1024):
                        if chunk:
                            totalbits += 1024
                            f.write(chunk)

        return self._urlparse.path
