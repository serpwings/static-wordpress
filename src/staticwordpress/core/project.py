# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/project.py
    
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
import json
import base64
import requests
from copy import deepcopy
from urllib import parse
from pathlib import Path, PosixPath, WindowsPath

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import (
    PROJECT,
    REDIRECTS,
    HOST,
    SOURCE,
    USER_AGENT,
    CONFIGS,
    VERISON,
    LINK_REGEX,
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Project(dict):
    def __init__(self, path_: str = None) -> None:
        super().__init__()

        if isinstance(path_, str):
            path_ = Path(path_)

        assert type(path_) == PosixPath or type(path_) == WindowsPath or path_ == None

        self["version"] = VERISON
        self["path"] = path_
        self["status"] = PROJECT.NOT_FOUND
        self["name"] = ""
        self["scheme"] = CONFIGS["DEFAULT_SCHEME"]
        self["user-agent"] = USER_AGENT.FIREFOX
        self["source"] = {
            "type": SOURCE.CRAWL,
            "url": "",
            "simply-static": {
                "folder": CONFIGS["SIMPLYSTATIC"]["FOLDER"],
                "archive": "",
            },
        }
        self["destination"] = {
            "host": HOST.NETLIFY,
            "url": "",
            "output": "",
        }

        self["wordpress"] = {"user": "", "api-token": ""}
        self["github"] = {"token": "", "repository": ""}
        self["redirects"] = REDIRECTS.NONE
        self["sitemap"] = "sitemap_index.xml"
        self["search"] = "search"
        self["404"] = "404-error"
        self["additional"] = []
        self["exclude"] = CONFIGS["EXCLUDE"]
        self["delay"] = 0.1

    def check_path_type(func):
        def inner(self, path: str = None):
            if isinstance(path, str):
                path = Path(path)
            return func(self, path)

        return inner

    def is_older_version(self) -> bool:
        # TODO: compare major, minor and revision seperately
        return self["version"] == VERISON

    def is_open(self) -> bool:
        """Check if a Project is Open

        Returns:
            bool: True/False if a Porject is already open.
        """
        return all(
            [
                self.status
                in [
                    PROJECT.OPEN,
                    PROJECT.SAVED,
                    PROJECT.UPDATE,
                    PROJECT.NEW,
                ],
            ]
        )

    def is_new(self) -> bool:
        return self["status"] == PROJECT.NEW

    def is_saved(self) -> bool:
        return self["status"] == PROJECT.SAVED

    def is_valid(self) -> bool:
        return all(
            [
                self["name"] != "",
                self["source"]["url"] != "",
                self["destination"]["output"] != "",
            ]
        )

    def has_github(self) -> bool:
        return self["github"]["token"] != "" and self["github"]["repository"] != ""

    def has_wordpress(self) -> bool:
        return self["source"]["type"] == SOURCE.CRAWL or (
            self["wordpress"]["api-token"] != "" and self["wordpress"]["user"] != ""
        )

    def can_crawl(self) -> bool:
        return all(
            [
                self["source"]["type"] == SOURCE.CRAWL,
                self["source"]["url"] != "",
                self["destination"]["output"] != "",
            ]
        )

    def create(self) -> None:
        self["status"] = PROJECT.NEW

    def update_ss(self) -> None:
        response = requests.get(
            self.src_url + CONFIGS["SIMPLYSTATIC"]["API"],
            headers={"Authorization": "Basic " + self.wp_auth_token},
        )

        if response.status_code < 399:
            ss_settings = json.loads((response).content)
            ss_archive_urls = [
                url[0]
                for url in re.findall(
                    LINK_REGEX,
                    ss_settings["archive_status_messages"]["create_zip_archive"][
                        "message"
                    ],
                )
                if url
            ]

            if ss_archive_urls:
                self["source"]["simply-static"]["folder"] = parse.urlparse(
                    ss_archive_urls[0]
                ).path.split(ss_settings["archive_name"])[0]

            self["source"]["simply-static"]["archive"] = ss_settings["archive_name"]

    @check_path_type
    def open(self, path_: str = None) -> None:
        if path_ and isinstance(path_, Path):
            self["path"] = path_

        self["status"] = PROJECT.NOT_FOUND
        if self["path"] and self["path"].exists():
            with self["path"].open("r") as f:
                data = json.load(f)
                if "version" not in data.keys():
                    return
                for key in self.keys():
                    self[key] = data[key]
                self["path"] = Path(data["path"])
                self["source"]["type"] = SOURCE[data["source"]["type"]]
                self["user-agent"] = USER_AGENT[data["user-agent"]]
                self["destination"]["host"] = HOST[data["destination"]["host"]]
                self["destination"]["output"] = Path(data["destination"]["output"])
                self["redirects"] = REDIRECTS(data["redirects"])
                self["scheme"] = parse.urlparse(self["source"]["url"]).scheme

            # TODO: Check version and update to latest (if required)
            self["status"] = PROJECT.SAVED

    @check_path_type
    def save_as(self, path_: str = None) -> None:
        if path_ and isinstance(path_, Path):
            self["path"] = path_
        self.save()

    def save(self) -> None:
        if self.is_open() and self["path"]:
            with self["path"].open("w") as f:
                self_copy = deepcopy(self)
                self_copy["path"] = str(self["path"])
                self_copy["user-agent"] = self["user-agent"].value
                self_copy["source"]["type"] = self["source"]["type"].value
                self_copy["destination"]["host"] = self["destination"]["host"].value
                self_copy["redirects"] = self["redirects"].value
                self_copy["destination"]["output"] = str(self["destination"]["output"])
                self_copy["status"] = PROJECT.SAVED.value

                json.dump(self_copy, f, indent=4)

            self["status"] = PROJECT.SAVED

    @property
    def status(self) -> PROJECT:
        return self["status"]

    @status.setter
    def status(self, status_: PROJECT) -> None:
        self["status"] = status_

    @property
    def scheme(self) -> str:
        return self["scheme"]

    @property
    def name(self) -> str:
        return self["name"]

    @name.setter
    def name(self, name_: str) -> None:
        self["name"] = name_

    @property
    def path(self) -> Path:
        return self["path"]

    @path.setter
    def path(self, path_: str) -> None:
        self["path"] = Path(path_) if isinstance(path_, str) else path_

    @property
    def version(self) -> str:
        return self["version"]

    @property
    def user_agent(self) -> str:
        return self["user-agent"]

    @user_agent.setter
    def user_agent(self, user_agent_: USER_AGENT) -> None:
        self["user-agent"] = user_agent_

    @property
    def sitemap(self) -> str:
        return self["sitemap"]

    @sitemap.setter
    def sitemap(self, sitemap_: str) -> None:
        self["sitemap"] = sitemap_

    @property
    def sitemap_url(self) -> str:
        return f"{self.src_url}/{self['sitemap']}"

    @property
    def destination(self) -> str:
        return self["destination"]

    @destination.setter
    def destination(self, destination_: dict) -> None:
        self["destination"] = destination_

    @property
    def output(self) -> Path:
        return self["destination"]["output"]

    @output.setter
    def output(self, output_: Path) -> None:
        self["destination"]["output"] = output_

    @property
    def dst_url(self) -> str:
        return self["destination"]["url"]

    @dst_url.setter
    def dst_url(self, dst_url_: str) -> None:
        self["destination"]["url"] = dst_url_

    @property
    def host(self) -> str:
        return self["destination"]["host"]

    @host.setter
    def host(self, host_: HOST) -> None:
        self["destination"]["host"] = host_

    @property
    def delay(self) -> float:
        return self["delay"]

    @delay.setter
    def delay(self, delay_: float) -> None:
        self["delay"] = delay_

    @property
    def src_type(self) -> SOURCE:
        return self["source"]["type"]

    @src_type.setter
    def src_type(self, src_type_: str) -> None:
        self["source"]["type"] = src_type_

    @property
    def src_url(self) -> str:
        return self["source"]["url"]

    @src_url.setter
    def src_url(self, src_url_: str) -> None:
        self["source"]["url"] = src_url_

    @property
    def ss_archive(self) -> str:
        return self["source"]["simply-static"]["archive"]

    @ss_archive.setter
    def ss_archive(self, ss_archive_name_: str) -> None:
        self["source"]["simply-static"]["archive"] = ss_archive_name_

    @property
    def ss_folder(self) -> str:
        return self["source"]["simply-static"]["folder"]

    @ss_folder.setter
    def ss_folder(self, ss_folder_: str) -> None:
        self["source"]["simply-static"]["folder"] = ss_folder_

    @property
    def zip_file_url(self) -> str:
        return f"{self.src_url}{self.ss_folder}{self.ss_archive}.zip"

    @property
    def zip_file_path(self) -> Path:
        return Path(f"{self.output}/{self.ss_folder}{self.ss_archive}.zip")

    @property
    def wordpress(self) -> str:
        return self["wordpress"]

    @wordpress.setter
    def wordpress(self, wp_settings_: dict) -> None:
        self["wordpress"] = wp_settings_

    @property
    def wp_user(self) -> str:
        return self["wordpress"]["user"]

    @wp_user.setter
    def wp_user(self, wp_user_: str) -> None:
        self["wordpress"]["user"] = wp_user_

    @property
    def wp_api_token(self) -> str:
        return self["wordpress"]["api-token"]

    @wp_api_token.setter
    def wp_api_token(self, wp_api_token_: str) -> None:
        self["wordpress"]["api-token"] = wp_api_token_

    @property
    def wp_auth_token(self) -> str:
        if self.wp_user and self.wp_api_token:
            return base64.b64encode(
                f"{self.wp_user}:{self.wp_api_token}".encode()
            ).decode("utf-8")
        return ""

    @property
    def github(self) -> str:
        return self["github"]

    @property
    def gh_repo(self) -> str:
        return self["github"]["repository"]

    @gh_repo.setter
    def gh_repo(self, gh_repo_: str) -> None:
        self["github"]["repository"] = gh_repo_

    @property
    def gh_token(self) -> str:
        return self["github"]["token"]

    @gh_token.setter
    def gh_token(self, gh_token_: str) -> None:
        self["github"]["token"] = gh_token_

    @property
    def additional(self) -> list:
        return self["additional"]

    @additional.setter
    def additional(self, additional_: list) -> None:
        self["additional"] = [url for url in additional_ if url]

    @property
    def exclude(self) -> list:
        return self["exclude"]

    @exclude.setter
    def exclude(self, exclude_: list) -> None:
        self["exclude"] = [url for url in exclude_ if url]

    @property
    def redirects(self) -> REDIRECTS:
        return self["redirects"]

    @redirects.setter
    def redirects(self, redirects_: REDIRECTS) -> None:
        self["redirects"] = redirects_

    @property
    def redirects_api_url(self) -> str:
        if self.redirects != REDIRECTS.NONE:
            return f'{self.src_url}/{ CONFIGS["REDIRECTS"][self["redirects"].value]["API"]}'
        return None

    @property
    def search(self) -> str:
        return self["search"]

    @search.setter
    def search(self, search_: str) -> None:
        self["search"] = search_

    @property
    def search_path(self) -> Path:
        return Path(f"{self.output}/{self['search']}")

    @property
    def _404_path(self) -> Path:
        return Path(f"{self.output}/{self['404']}")

    @property
    def _404_url(self) -> str:
        return f"{self.src_url}/{self['404']}"

    @property
    def _404(self) -> str:
        return self["404"]

    @_404.setter
    def _404(self, page_404_) -> None:
        self["404"] = page_404_
