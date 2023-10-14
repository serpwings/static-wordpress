# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/gui/workflow.py
    
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
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from PyQt5.QtCore import QObject, pyqtSignal

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.project import Project
from ..core.constants import SOURCE
from ..core.workflow import Workflow
from ..gui.utils import logging_decorator, progress_decorator


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class WorkflowGUI(QObject):
    signalSitemapLocation = pyqtSignal(str)
    signalProgress = pyqtSignal(str, int)
    signalVerification = pyqtSignal(dict)

    _work_flow = Workflow()

    def set_project(self, project_: Project) -> None:
        if project_.is_open():
            self._work_flow.set_project(project_=project_)

    @progress_decorator("Verifying Project Settings", 100)
    @logging_decorator
    def verify_project(self):
        self.signalVerification.emit(
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

    @logging_decorator
    def stop_calcualations(self):
        self._work_flow.stop_calculations()

    def is_running(self):
        return self._work_flow._keep_running

    def batch_processing(self):
        self._work_flow._keep_running = True
        if self._work_flow._project.src_type == SOURCE.CRAWL:
            self.crawl_sitemap()
            self.crawl_additional_files()

        self.pre_processing()
        self.add_404_page()
        self.add_robots_txt()
        self.add_redirects()
        self.add_search()

    @progress_decorator("Pre-Processing", 100)
    @logging_decorator
    def pre_processing(self):
        if self._work_flow._project.src_type == SOURCE.ZIP:
            self.download_zip_file()
            self.setup_zip_folders()
        else:
            self.crawl_url(loc_=self._work_flow._project.src_url)

    @progress_decorator("Downloading Zip File", 100)
    @logging_decorator
    def download_zip_file(self) -> None:
        self._work_flow.download_zip_file()

    @progress_decorator("Setting Up Directories", 100)
    def setup_zip_folders(self) -> None:
        self._work_flow.setup_zip_folders()

    @progress_decorator("Saving 404 Page", 100)
    @logging_decorator
    def add_404_page(self) -> None:
        self._work_flow.add_404_page()

    @progress_decorator("Copying robots.txt", 100)
    @logging_decorator
    def add_robots_txt(self) -> None:
        self._work_flow.add_robots_txt()

    @progress_decorator("Writing Redirects File", 100)
    @logging_decorator
    def add_redirects(self) -> None:
        self._work_flow.add_redirects()

    @progress_decorator("Generating Search Index", 100)
    @logging_decorator
    def add_search(self) -> None:
        self._work_flow.add_search()

    @progress_decorator("Searching Sitemap", 100)
    @logging_decorator
    def find_sitemap(self) -> None:
        self._work_flow.find_sitemap()
        self.signalSitemapLocation.emit(self._work_flow.sitemap)

    @progress_decorator("Crawling Sitemap", 100)
    @logging_decorator
    def crawl_sitemap(self) -> None:
        self._work_flow.crawl_sitemap()

    def crawl_url(self, loc_):
        self._work_flow.clear()
        self._work_flow.crawl_url(loc_=loc_)

    @progress_decorator("Crawling Additional Pages", 100)
    @logging_decorator
    def crawl_additional_files(self) -> None:
        for additiona_url in self._work_flow._project.additional:
            self.crawl_url(loc_=additiona_url)

    @progress_decorator("Creating Website on GitHub", 100)
    @logging_decorator
    def create_github_repositoy(self):
        self._work_flow.create_github_repositoy()

    @progress_decorator("Deleting from GitHub", 100)
    @logging_decorator
    def delete_github_repositoy(self):
        self._work_flow.delete_github_repositoy()

    @progress_decorator("Initalizing Website", 100)
    @logging_decorator
    def init_git_repositoy(self):
        self._work_flow.init_git_repositoy()

    @progress_decorator("Commiting Website to Repo", 100)
    @logging_decorator
    def commit_git_repositoy(self):
        self._work_flow.commit_git_repositoy()

    @progress_decorator("Pushing Website to GitHub", 100)
    @logging_decorator
    def publish_github_repositoy(self):
        self._work_flow.publish_github_repositoy()
