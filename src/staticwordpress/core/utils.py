# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/utils.py
    
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

import os
import re
import stat
import shutil
from urllib import parse
from urllib.request import urlopen
from pathlib import Path
from zipfile import ZipFile
from functools import lru_cache
from unittest.mock import Mock

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import requests
from requests.adapters import HTTPAdapter
from requests.models import Response

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import CONFIGS, LINK_REGEX


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


def string_formatter(str):
    """string formatter

    Args:
        str (string): Input Strings

    Returns:
        _type_: Resulted Strings
    """
    return str


def rmtree_permission_error(func, path, exc_info):
    """Deleteing folders/files after changing permissions.

    Args:
        func (_type_): Sender Function
        path (_type_): Path to be delete
        exc_info (_type_): executable information
    """
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def get_clean_url(url_: str = "", path_: str = "", scheme_: str = "") -> str:
    """Get Clean Url from URL and change Path of Final Url

    Args:
        url_ (str, optional): Dirty Url. Defaults to "".
        path_ (str, optional): Desired Path of the clean Url (default is Path of dirty url).

    Returns:
        str: Clean Url with desired Path.
    """
    if isinstance(url_, str):
        url_ = parse.urlparse(url_)

    url_ = parse.urlunparse(
        parse.ParseResult(
            scheme=scheme_ if scheme_ else url_.scheme,
            netloc=url_.netloc,
            path=path_ if path_ else url_.path,
            params="",
            query="",
            fragment="",
        )
    )

    url_ = url_.split("</")[0]
    pattern = "\\" + "|\\".join([*CONFIGS["CLEAN"]["CHARS"]])
    url_ = re.sub(pattern, "", url_)
    return url_


def rm_dir_tree(dir_path_: str = None, delete_root_: bool = False) -> None:
    """Delte Directry tree at dir_path

    Args:
        dir_path (Path | str, optional): Path/tree which need to be remvoed.
        delete_root (bool, optional): If True then Parnt/root folder is not delted.
    """
    if dir_path_ and isinstance(dir_path_, str):
        dir_path_ = Path(dir_path_)

    if not dir_path_.exists():
        return

    for _path in dir_path_.glob("**/*"):
        if _path.is_file() and _path.stem not in [".gitignore", ".project"]:
            _path.unlink()
        elif _path.is_dir() and _path.stem != "_data":
            shutil.rmtree(_path, onerror=rmtree_permission_error)

    if delete_root_:
        dir_path_.rmdir()


def get_mock_response(url_: str = None) -> Response:
    """Genreate Mock HTTP Response

    Args:
        url_ (str, optional): Input Url. Defaults to None.

    Returns:
        Response: Mock response with 9999 as status code
    """
    response = Mock(spec=Response)
    response.text = ""
    response.history = []
    response.status_code = 9999
    response.url = url_
    return response


@lru_cache
def get_remote_content(url_: parse.ParseResult, max_retires: int = 5) -> Response:
    """Get remote content using request library

    Args:
        url (str): url needed to be fetched
        max_retires (int, optional): maximum tries to fetch the content. Defaults to 5.
    Returns:
        Response: request response object.
    """
    url = get_clean_url(url_=url_)
    try:
        s = requests.Session()
        s.mount(url, HTTPAdapter(max_retries=max_retires))
        default_user_agent = CONFIGS["DEFAULT_USER_AGENT"]
        return s.get(url, headers=CONFIGS["HEADER"][default_user_agent])
    except:
        return get_mock_response(url_=url)


def update_links(content: str, from_: str, to_: str) -> str:
    """update links in content by replacing from_ urls with to_urls

    Args:
        content (str): Content where links will be updated
        from_ (str): Source Urls
        to_ (str): Destination Url

    Returns:
        str: _description_
    """
    from_ = parse.unquote(from_).replace("\/", "/")
    to_ = parse.unquote(to_).replace("\/", "/")
    from_ = from_[0:-1]
    to_ = to_[0:-1]
    return content.replace(from_, to_)


def extract_urls_from_raw_text(raw_text_: str, dest_url_: str, src_url_: str) -> list:
    """Extract Urls form a Raw Text using Regex

    Args:
        raw_text (str): Text containing Urls
        dest_url (str): Desitnation Url Path (required if an update is necessary)
        src_url (str): Source Url Path (required if an update is necessary)

    Returns:
        list: List of Urls extracted
    """
    new_additional_links = []
    for link in re.findall(LINK_REGEX, raw_text_):
        item = link[0].replace("\/", "/").split("?")[0]
        item = re.sub("\(|\)|\[|\]", "", item)
        new_additional_link = update_links(item, dest_url_, src_url_)

        if new_additional_link and src_url_ in new_additional_link:
            new_additional_links.append(new_additional_link)

    return new_additional_links


def extract_zip_file(zip_file_path_: Path, output_location_: Path) -> None:
    """Extract ZipFile content to output_location Path

    Args:
        zip_file_path (Path): Zip File Path
        output_location (Path): Ouput File Path
    """
    if output_location_.is_dir() and zip_file_path_.exists():
        with ZipFile(zip_file_path_, "r") as zf:
            zf.extractall(output_location_)


def is_url_valid(url_: str) -> bool:
    url_parsed_ = parse.urlparse(url_)

    if all([url_parsed_.scheme, url_parsed_.netloc]):
        # return get_remote_content(url_parsed_, max_retires=1).status_code < 399
        try:
            return urlopen(url_).getcode() < 399
        except:
            return False
    return False
