# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/sitemaps.py
    
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

from urllib import parse

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from bs4 import BeautifulSoup

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import CONFIGS
from ..core.utils import get_clean_url, get_remote_content, is_url_valid

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


def find_sitemap_location(home_url_: str) -> str:
    """Finding Sitemap Location Using Home Url

    Args:
        home_url (str): Source URL of the Website

    Returns:
        str: Location of Sitemap
    """
    if is_url_valid(home_url_):
        for sitemap_path in CONFIGS["SITEMAP"]["SEARCH_PATHS"]:
            sitemap_url = get_clean_url(home_url_, sitemap_path)
            response = get_remote_content(sitemap_url)
            if response.status_code < 400:
                return parse.urlparse(response.url).path

        # robots.txt
        robots_txt = get_clean_url(home_url_, "robots.txt")
        response = get_remote_content(robots_txt)
        if response:
            for item in response.text.split("\n"):
                if item.startswith("Sitemap:"):
                    return item.split("Sitemap:")[-1].strip()

        # check home page for link rel=sitemap
        response = get_remote_content(home_url_)
        if response:
            soup = BeautifulSoup(response.text, features="xml")
            for link in soup.find_all("link"):
                if link.has_attr("sitemap"):
                    return link["href"]
        return ""
    return ""


def extract_sitemap_paths(sitemap_url_: str) -> list:
    """Extract Sub-Sitemap from Index Sitemap

    Args:
        sitemap_url (str): Index Sitemap Url

    Returns:
        list: List of Sub-Sitemaps
    """
    sitemap_paths = []
    response = get_remote_content(sitemap_url_)
    for item in response.text.split("\n"):
        if ".xsl" in item:
            st = item.find("//")
            en = item.find(".xsl")
            sitemap_paths.append(f"http:{item[st:en+4]}")

    soup = BeautifulSoup(response.text, features="xml")
    if len(soup.find_all("sitemapindex")) > 0:
        sitemap_paths += [
            sitemap.findNext("loc").text for sitemap in soup.find_all("sitemap")
        ]

    return sitemap_paths
