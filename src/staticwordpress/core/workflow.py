# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/workflow.py
    
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

import time
import glob
import shutil
import codecs
import logging
import random
from pathlib import Path

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import requests
from bs4 import BeautifulSoup

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from .search import Search
from .github import GitHub
from .crawler import Crawler
from .project import Project
from .redirects import Redirects
from .sitemaps import find_sitemap_location, extract_sitemap_paths
from .utils import extract_zip_file, rm_dir_tree, update_links
from .constants import (
    CONFIGS,
    SHARE_FOLDER_PATH,
    URL,
    HOST,
    SOURCE,
    PROJECT,
    REDIRECTS,
)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Workflow:
    def __init__(self):
        self._project = Project()
        self._redirects = Redirects()
        self._search = Search()
        self._crawler = Crawler(loc_="", type_=URL.NONE)
        self._urls = dict()
        self._github = None
        self._keep_running = True

    @property
    def sitemap(self) -> str:
        return self._project.sitemap

    def clear(self):
        self._urls = dict()

    def create_project(
        self,
        project_name_: str = "",
        project_path_: str = "",
        wp_user_: str = "",
        wp_api_token_: str = "",
        src_url_: str = "",
        dst_url_: str = "",
        output_folder_: str = "",
        custom_404_: str = "",
        custom_search_: str = "",
        src_type_: SOURCE = SOURCE.ZIP,
        host_type_: HOST = HOST.NETLIFY,
    ) -> None:
        self._project.status = PROJECT.NEW
        
        if src_type_ == SOURCE.ZIP:
            self._project.redirects = REDIRECTS.REDIRECTION
        
        self._project.name = project_name_
        self._project.path = project_path_
        self._project._404 = custom_404_
        self._project.search = custom_search_

        self._project.wordpress = {"user": wp_user_, "api-token": wp_api_token_}
        self._project.destination = {
            "host": host_type_,
            "url": dst_url_,
            "output": output_folder_,
        }

        self._project.src_type = src_type_
        self._project.src_url = src_url_

        # TODO: Add Support for GH Repo ??? Do We need it?
        if all(
            [
                self._project.gh_token != "",
                self._project.output != "",
                self._project.gh_repo != "",
            ]
        ):
            self._github = GitHub(
                gh_token_=self._project.gh_token,
                repo_dir_=self._project.output,
                gh_repo_=self._project.gh_repo,
            )

        self._project.update_ss()

    def set_project(self, project_: Project) -> None:
        self._project = project_

        if all(
            [
                self._project.gh_token != "",
                self._project.output != "",
                self._project.gh_repo != "",
            ]
        ):
            self._github = GitHub(
                gh_token_=self._project.gh_token,
                repo_dir_=self._project.output,
                gh_repo_=self._project.gh_repo,
            )

        if self._project.src_type == SOURCE.ZIP:
            self._project.update_ss()

    def stop_calculations(self):
        self._keep_running = False
        logging.warn(f"Background Processings will Stop. Please wait!")

    def open_project(self):
        pass

    def save_project(self):
        pass

    def close_project(self):
        pass

    def download_zip_file(self) -> None:
        if self._keep_running:
            rm_dir_tree(self._project.output, delete_root=False)
            self._crawler = Crawler(loc_=self._project.zip_file_url, type_=URL.ZIP)
            self._crawler.fetch()
            self._crawler.save(full_output_folder=self._project.output)

    def setup_zip_folders(self) -> None:
        if self._keep_running:
            extract_zip_file(
                self._project.zip_file_path,
                output_location=Path(self._project.output),
            )
            rm_dir_tree(Path(f"{self._project.output}/{self._project.ss_folder}"))
            extracted_paths = glob.glob(
                f"{self._project.output}/**/{self._project.ss_archive}", recursive=True
            )
            if extracted_paths:
                archive_folder = Path(extracted_paths[0])
                shutil.copytree(
                    archive_folder, self._project.output, dirs_exist_ok=True
                )
                zip_download_folder = archive_folder.relative_to(self._project.output)
                rm_dir_tree(
                    Path(f"{self._project.output}/{zip_download_folder.parts[0]}"),
                    delete_root=True,
                )

    def add_search(self) -> None:
        """Now Process all folders with content/index.html files
        only include html pages with content (blogs, pages)"""
        if self._project.search_path.exists():
            self._search = Search(
                search_page_=self._project.search_path, dst_url_=self._project.dst_url
            )

            for _path in glob.glob(f"{self._project.output}/**", recursive=True):
                current_path = Path(_path)
                if (
                    all(
                        [
                            exclude not in current_path.parts
                            for exclude in self._project.exclude
                        ]
                    )
                    and current_path.parts[-1] == "index.html"
                ):
                    if self._keep_running:
                        with codecs.open(current_path, "r", "utf-8") as f:
                            content = f.read()
                            content = update_links(
                                content,
                                self._project.src_url,
                                self._project.dst_url,
                            )

                            url_path = current_path.parent.relative_to(
                                self._project.output
                            )

                            soup = BeautifulSoup(content, "lxml")
                            if str(url_path) == self._project.search:
                                self._search.update(
                                    soup_=soup, output_path_=current_path
                                )
                            else:
                                self._search.add(
                                    soup_=soup,
                                    url_path_=url_path,
                                )

            self._search.copy_scripts()
            self._search.save()

    def add_redirects(self) -> None:
        if self._keep_running:
            if self._project.redirects != REDIRECTS.NONE:
                self._redirects.get_from_plugin(
                    redirects_api_path=self._project.redirects_api_url,
                    wp_auth_token_=self._project.wp_auth_token,
                )

            if self._project.search_path.exists():
                self._redirects.add_search(search_page=self._project.search)

            redirect_ouputfile = f"{self._project.output}/{CONFIGS['REDIRECTS']['DESTINATION'][self._project.host.value]}"
            self._redirects.save(
                output_file_=redirect_ouputfile, host_=self._project.host
            )

    def add_robots_txt(self) -> None:
        if self._keep_running:
            src = Path(f"{SHARE_FOLDER_PATH}/robots.txt")
            dst = Path(f"{self._project.output}/robots.txt")

            if src.exists():
                shutil.copyfile(src, dst)

    def add_404_page(self) -> None:
        if self._keep_running:
            self._crawler = Crawler(
                loc_=self._project._404_url,
                type_=URL.HTML,
                scheme_=self._project.scheme,
            )
            self._crawler.fetch()
            self._crawler.save(full_output_folder=self._project.output)

            if self._project.src_type == SOURCE.ZIP:
                if self._project._404_path.exists():
                    shutil.copy2(
                        src=f"{self._project._404_path}/index.html",
                        dst=f"{self._project.output}/404.html",
                    )
                    shutil.rmtree(self._project._404_path)

    # crawl Actions
    def find_sitemap(self) -> None:
        self._project.sitemap = find_sitemap_location(self._project.src_url)

    def crawl_sitemap(self) -> None:
        if self._project.sitemap:
            sitemap_paths = extract_sitemap_paths(sitemap_url=self._project.sitemap_url)
            for sitemap_path in sitemap_paths:
                if self._keep_running:
                    self.crawl_url(loc_=sitemap_path)

    def crawl_url(self, loc_):
        current_url = Crawler(loc_=loc_, scheme_=self._project.scheme)
        if current_url.hash not in self._urls:
            current_url.fetch()
            full_output_path = current_url.save(
                self._project.output, dst_url=self._project.dst_url
            )
            self._urls[current_url._hash] = current_url

            custom_message = "Saved"
            if current_url.status_code >= 400 or current_url._type == URL.NONE:
                custom_message = "Ignored"

            logging.info(
                f"{custom_message}: {current_url.status_code} {current_url._type} {full_output_path}"
            )

            for internal_link in current_url.internal_links:
                time.sleep(self._project.delay + random.random() / 100)
                if self._keep_running:
                    self.crawl_url(internal_link)

    # Project Verifications
    def verify_project_name(self):
        logging.info(f"Verifying Project Name!")
        return self._project.name != ""

    def verify_src_url(self):
        logging.info(f"Verifying Source Url!")
        current_url = Crawler(loc_=self._project.src_url, scheme_=self._project.scheme)
        current_url.fetch()
        return current_url.status_code < 399  # non error status codes

    def verify_output(self):
        logging.info(f"Verifying Output Folder!")
        return self._project.output.exists()

    def verify_wp_user(self):
        logging.info(f"Verifying WordPress User Name!")

        response = requests.get(
            self._project.redirects_api_url,
            headers={"Authorization": "Basic " + self._project.wp_auth_token},
        )
        return response.status_code < 399

    def verify_sitemap(self):
        logging.info(f"Verifying Sitemap!")

        response = requests.get(
            self._project.sitemap_url,
            headers={"Authorization": "Basic " + self._project.wp_auth_token},
        )
        return response.status_code < 399

    def verify_github_token(self):
        return self._github.is_token_valid()

    def verify_github_repo(self):
        return self._github.is_repo_valid()

    def verify_simply_static(self):
        logging.info(f"Verifying simply static plugin!")

        response = requests.get(
            self._project.src_url + CONFIGS["SIMPLYSTATIC"]["API"],
            headers={"Authorization": "Basic " + self._project.wp_auth_token},
        )

        ss_found = response.status_code < 399
        logging.info(f"Simply Static Plugin {'found' if ss_found else 'not found'}!")
        logging.info("".join(140 * ["-"]))
        return ss_found

    # Github Actions
    def create_github_repositoy(self):
        if self._keep_running:
            self._github.create()

    def delete_github_repositoy(self):
        if self._keep_running:
            self._github.delete()

    def init_git_repositoy(self):
        if self._keep_running:
            self._github.initialize()

    def commit_git_repositoy(self):
        if self._keep_running:
            self._github.commit()

    def publish_github_repositoy(self):
        if self._keep_running:
            self._github.publish()
