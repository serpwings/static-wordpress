#!/usr/bin/python

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    ss_script.py
    
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

import os
import sys
from pathlib import Path
import logging

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from src.staticwordpress.core.workflow import Workflow
from src.staticwordpress.core.constants import SOURCE, HOST

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
        stream=sys.stdout,
    )

    env_wp_user = os.environ.get("user")
    env_wp_api_token = os.environ.get("token")
    env_src_url = os.environ.get("src")
    env_dst_url = os.environ.get("dst")

    assert env_wp_user != ""
    assert env_wp_api_token != ""
    assert env_src_url != ""
    assert env_dst_url != ""

    env_404 = os.environ.get("404") if os.environ.get("404") else "404-error"
    env_search = os.environ.get("search") if os.environ.get("search") else "search"
    env_output = os.environ.get("output") if os.environ.get("output") else "output"

    # create output path if not exists
    Path(env_output).mkdir(parents=True, exist_ok=True)

    ss_zip_obj = Workflow()
    ss_zip_obj.create_project(
        project_name_="simply-static-zip-deploy",
        wp_user_=env_wp_user,
        wp_api_token_=env_wp_api_token,
        src_url_=env_src_url,
        dst_url_=env_dst_url,
        output_folder_=env_output,
        custom_404_=env_404,
        custom_search_=env_search,
        src_type_=SOURCE.ZIP,
        host_type_=HOST.NETLIFY,
    )

    ss_zip_obj.download_zip_file()
    ss_zip_obj.setup_zip_folders()
    ss_zip_obj.add_404_page()
    ss_zip_obj.add_robots_txt()
    ss_zip_obj.add_redirects()
    ss_zip_obj.add_search()
