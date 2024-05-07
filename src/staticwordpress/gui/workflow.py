# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/gui/workflow.py
    
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

from time import sleep
from random import random
import logging

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtCore import QObject, pyqtSignal

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.project import Project
from ..core.constants import SOURCE, URL
from ..core.workflow import Workflow
from ..core.crawler import Crawler
from ..gui.utils import logging_decorator


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SWWorkflowObject(QObject):
    emit_sitemap_location = pyqtSignal(str)
    emit_progress = pyqtSignal(str, int)
    emit_verification = pyqtSignal(dict)
    emit_tabulate_crawl_data = pyqtSignal(list)

    _work_flow = Workflow()
    _approximate_crawl_count = 1

    @property
    def work_flow(self) -> Workflow():
        return self._work_flow

    def set_project(self, project_: Project) -> None:
        if project_.is_open():
            self._work_flow.set_project(project_=project_)

    @logging_decorator
    def verify_project(self):
        self.emit_verification.emit(
            {
                "name": self._work_flow.verify_project_name(),
                "src-url": self._work_flow.verify_src_url(),
                "wordpress-user": self._work_flow.verify_wp_user(),
                "wordpress-api-token": self._work_flow.verify_wp_user(),
                "sitemap": self._work_flow.verify_sitemap(),
                "github-token": self._work_flow.verify_github_token(),
                "github-repository": self._work_flow.verify_github_repo(),
            }
        )
        self.emit_progress.emit("Verifyied Project Settings", 100)

    @logging_decorator
    def stop_calcualations(self):
        self._work_flow.stop_calculations()

    def is_running(self):
        return self._work_flow._keep_running

    def batch_processing(self):
        self._work_flow.clear()
        self._work_flow._keep_running = True
        if self._work_flow._project.src_type == SOURCE.CRAWL:
            self.crawl_sitemap()
            self.crawl_additional_files()

        self.start_crawling()
        self.add_404_page()
        self.add_robots_txt()
        self.add_redirects()
        self.add_search()

    @logging_decorator
    def start_crawling(self):
        if self._work_flow._project.src_type == SOURCE.ZIP:
            self.download_zip_file()
            self.setup_zip_folders()
        else:
            self.crawl_url(loc_=self._work_flow._project.src_url)

        self.emit_progress.emit("Crawling Done", 100)

    @logging_decorator
    def download_zip_file(self) -> None:
        self._work_flow.download_zip_file()
        self.emit_progress.emit("Downloaded Zip File", 100)

    def setup_zip_folders(self) -> None:
        self._work_flow.setup_zip_folders()
        self.emit_progress.emit("Setup Directories", 100)

    @logging_decorator
    def add_404_page(self) -> None:
        self._work_flow.add_404_page()
        self.emit_progress.emit("Saved 404 Page", 100)

    @logging_decorator
    def add_robots_txt(self) -> None:
        self._work_flow.add_robots_txt()
        self.emit_progress.emit("Copyied robots.txt", 100)

    @logging_decorator
    def add_redirects(self) -> None:
        self._work_flow.add_redirects()
        self.emit_progress.emit("Written Redirects File", 100)

    @logging_decorator
    def add_search(self) -> None:
        self._work_flow.add_search()
        self.emit_progress.emit("Generated Search Index", 100)

    @logging_decorator
    def find_sitemap(self) -> None:
        self._work_flow.find_sitemap()
        self.emit_sitemap_location.emit(self._work_flow.sitemap)
        self.emit_progress.emit("Searched Sitemap", 100)

    @logging_decorator
    def crawl_sitemap(self) -> None:
        self.emit_progress.emit("Crawling Sitemap", 50)
        self._work_flow.crawl_sitemap()
        self.emit_progress.emit("Crawled Sitemap", 100)

    def crawl_url(self, loc_: str):
        current_crawler = Crawler(loc_=loc_, scheme_=self._work_flow._project.scheme)
        if current_crawler.hash not in self._work_flow._urls:
            sleep(self._work_flow._project.delay + random() / 100)
            current_crawler.fetch()
            full_output_path = current_crawler.save(
                self._work_flow._project.output,
                dst_url=self._work_flow._project.dst_url,
            )
            self._work_flow._urls[current_crawler._hash] = current_crawler
            custom_message = "Saved"
            if current_crawler.status_code >= 400 or current_crawler._typ == URL.NONE:
                custom_message = "Ignored"

            logging.info(
                f"{custom_message}: {current_crawler.status_code} {current_crawler._typ} {full_output_path}"
            )

            table_row = [
                len(self._work_flow._urls),  # current_url.hash,
                current_crawler.url,
                current_crawler.path,
                current_crawler.typ.value,
                current_crawler.status_code,
                custom_message,
            ]
            self._approximate_crawl_count += len(current_crawler.internal_links) / 5

            self.emit_tabulate_crawl_data.emit(table_row)
            self.emit_progress.emit(
                "Crawling Pages",
                int(100 * len(self._work_flow._urls) / self._approximate_crawl_count),
            )

            for internal_link in current_crawler.internal_links:
                if self._work_flow._keep_running:
                    self.crawl_url(loc_=internal_link)

    @logging_decorator
    def crawl_additional_files(self) -> None:
        for additiona_url in self._work_flow._project.additional:
            self.crawl_url(loc_=additiona_url)
        self.emit_progress.emit("Crawled Additional Pages", 100)

    @logging_decorator
    def create_github_repositoy(self):
        self._work_flow.create_github_repositoy()
        self.emit_progress.emit("Created Website on GitHub", 100)

    @logging_decorator
    def delete_github_repositoy(self):
        self._work_flow.delete_github_repositoy()
        self.emit_progress.emit("Deleted from GitHub", 100)

    @logging_decorator
    def init_git_repositoy(self):
        self._work_flow.init_git_repositoy()
        self.emit_progress.emit("Initalized Static Website", 100)

    @logging_decorator
    def commit_git_repositoy(self):
        self._work_flow.commit_git_repositoy()
        self.emit_progress.emit("Committed Website to Repo", 100)

    @logging_decorator
    def publish_github_repositoy(self):
        self._work_flow.publish_github_repositoy()
        self.emit_progress.emit("Pushed Website to GitHub", 100)
