# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    src/staticwordpress/core/github.py
    
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

import logging
from datetime import datetime
from pathlib import Path

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# 3rd PARTY LIBRARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import git
import github

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class GitHub:
    def __init__(self, gh_token_: str, gh_repo_: str, repo_dir_: str) -> None:
        assert gh_token_ != ""
        assert gh_repo_ != ""
        assert repo_dir_ != ""

        self._gh_token = gh_token_
        self._gh_repo = gh_repo_

        if Path(f"{repo_dir_}/.git").exists():
            self._repo = git.Repo(repo_dir_)
        else:
            self._repo = git.Repo.init(repo_dir_)

        self._gh_object = github.Github(self._gh_token)

    # decorators
    def check_gh_token(func):
        def inner(self):
            try:
                self._gh_object.get_user().name
                return func(self)
            except:
                pass

        return inner

    def check_repo_dir(func):
        def inner(self):
            try:
                _ = self._repo.git_dir
                return func(self)
            except git.exc.InvalidGitRepositoryError:
                pass

        return inner

    @check_gh_token
    def is_token_valid(self) -> bool:
        logging.info(f"Verifying Github Token.")
        return self._gh_object.get_user().name != ""

    @check_gh_token
    def is_repo_valid(self) -> bool:
        logging.info(f"Verifying Github Repository.")
        return self._gh_object.get_user().get_repo(self._gh_repo) is not None

    @check_gh_token
    def create(self) -> None:
        """create new repo at github"""
        if self._gh_repo:
            all_respos = [repo.name for repo in self._gh_object.get_user().get_repos()]
            if self._gh_repo not in all_respos:
                self._gh_object.get_user().create_repo(self._gh_repo, private=True)
                logging.info(
                    f"Creating Remote Repository Successfully: {self._gh_repo}"
                )

    @check_gh_token
    def delete(self) -> None:
        """delete repo"""
        if self._gh_repo and self._gh_object.get_user():
            all_respos = [repo.name for repo in self._gh_object.get_user().get_repos()]
            if self._gh_repo in all_respos:
                self._gh_object.get_user().get_repo(self._gh_repo).delete()
                logging.info(
                    f"Deleting Remote Repository: {self._gh_repo} successfully"
                )

    @check_gh_token
    def initialize(self) -> None:
        """init repoinit repo"""
        logging.info(
            f"Initializing Git Repository - Orgins to GitHub will be set automatically"
        )

        login = self._gh_object.get_user().login
        remote_url = (
            f"https://{login}:{self._gh_token}@github.com/{login}/{self._gh_repo}"
        )

        if self._repo.remotes:
            origin = self._repo.remotes.origin
            origin.set_url(remote_url, origin.url)
        else:
            origin = self._repo.create_remote("origin", url=remote_url)

        logging.info(f"Origin Exsitig for Git functionalities: {origin.exists()} ")

        assert origin.exists()

        logging.info(f"Updating Local Copy of Git Repository")
        origin.fetch()

    @check_repo_dir
    def commit(self) -> None:
        """commit to local repository"""
        logging.info(f"Start Committing Changes to Local Repository")
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
        self._repo.git.add("--all")
        self._repo.index.commit(f"{date_time}: Update using static-wordpress software")
        logging.info(f"All Changes Committed to Local Repository")

    @check_repo_dir
    def publish(self):
        """publish to github"""
        self._repo.create_head("main")
        if self._repo.remotes:
            logging.info(f"Pushing Repository Changes to GitHub!")
            self._repo.remotes[0].push("main")
        else:
            logging.error(f"Pushing Remote Repository on GitHub Failed.!")
