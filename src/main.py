#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""
Static WordPress
https://github.com/serpwings/static-wordpress

A Python Library to prepare and deploy static version of a WordPress Installation on any Static Web Hosting.


MIT License
Copyright (c) 2023 SERP Wings <www.serpwings.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORTS (Standard Library)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys
import glob
import codecs
from pathlib import Path
from zipfile import ZipFile
import shutil
import base64
import json
import re
from urllib import parse

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORTS (3rd Party)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
import requests
from requests.structures import CaseInsensitiveDict

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# Local Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import helpers

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONSTANTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

LUNR = {
    "src": "https://cdnjs.cloudflare.com/ajax/libs/lunr.js/2.3.9/lunr.min.js",
    "integrity": "sha512-4xUl/d6D6THrAnXAwGajXkoWaeMNwEKK4iNfq5DotEbLPAfk6FSxSP3ydNxqDgCw1c/0Z1Jg6L8h2j+++9BZmg==",
    "crossorigin": "anonymous",
    "referrerpolicy": "no-referrer",
}

SEARCH_INDEX = {"src": "search.js"}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class SimplyStaticPostProcess:
    """
    This is a class processing Simply Static WordPress Plugin and converting it to static site.

    Attributes:
        config (dic): Contains all important configurations about the class.
        output_folder (Path): Contains Path for output folder location
        zip_file_path (Path): ZIP File Path to download simply-static-zip file freom remote server.
        redirect_page (Path): Contains Path of redirect page
        robots_txt_page (Path): Contains Path of robots.txt page
        self._404_page (Path): Contains Path of 404 Page
    """

    def __init__(self, config_=None):
        """Initialize SimplyStaticPostProcess objet with a config values.

        Args:
            config_ (dict, optional): contains diverse conditions for SimplyStaticPostProcess object.
        """
        if config_:
            self.config = config_
            self.output_folder = Path(self.config["root"], self.config["output_folder"])
            self.zip_file_path = Path(self.config["root"], self.config["zip_file_name"])
            self.redirect_page = Path(
                self.output_folder, self.config["pages"]["redirect"]
            )
            self.all_redirects = self.config["pages"]["all-redirects"]
            self.robots_txt_page = Path(
                self.output_folder, self.config["pages"]["robots"]
            )
            self._404_page = Path(
                self.output_folder, self.config["pages"]["404"], "index.html"
            )

    def download_zip_file(self):
        """Download zip file from remote server"""

        helpers.log_to_console("INFO", configurations["zip_url"])

        headers = CaseInsensitiveDict()
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        headers["Pragma"] = "no-cache"
        headers["Expires"] = "0"

        current_session = requests.session()
        response = current_session.get(configurations["zip_url"], headers=headers)

        if response.status_code == 200:
            import os

            with open(self.config["zip_file_name"], "wb") as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)
            helpers.log_to_console("INFO", "Simply Static Zip File Downloaded")
        else:
            helpers.log_to_console("ERROR", "Simply Static Zip File Not available")

        current_session.cookies.clear()

    def create_output_folder(self):
        """Create Ouput Folder it it doesnot exist."""

        if not self.output_folder.is_dir():
            self.output_folder.mkdir(parents=True, exist_ok=True)
            helpers.log_to_console("INFO", "Output Folder Created")
        else:
            helpers.log_to_console("ERROR", "Cannot Create Output Folder")

    def create_robots_txt(self):
        """Create Robots.txt File using robots-txt page. Default would be ``User-agent: *``"""
        robots_path = Path(
            self.robots_txt_page,
            "index.html",
        )

        if robots_path.exists():
            with codecs.open(robots_path, "r", "utf-8") as f:
                robots_txt_contents = f.read()
                soup = BeautifulSoup(robots_txt_contents, "lxml")
                robots_table = soup.find_all("table")[0]

                with open(f"{self.output_folder}/robots.txt", "w") as f:
                    for row in robots_table.tbody.find_all("tr"):
                        f.write("".join([cell.text.strip("\r") for cell in row("td")]))
                        f.write("\n")

                shutil.rmtree(Path(self.output_folder, self.config["pages"]["robots"]))
        else:
            with open(f"{self.output_folder}/robots.txt", "w") as f:
                f.write("User-agent: * \n")
                f.write("Disallow: /wp-admin/ \n")
                f.write("Allow: /wp-admin/admin-ajax.php \n")

        helpers.log_to_console("INFO", "Created robots.txt file")

    def setup_output_folders(self) -> None:
        # Copy all extract files/folders to output fold and delete the source
        extracted_paths = glob.glob(
            f"{self.output_folder}/**/{self.config['zip_file_name'].split('.zip')[0]}",
            recursive=True,
        )
        if extracted_paths:
            archive_ext_folder = Path(extracted_paths[0])
            shutil.copytree(archive_ext_folder, self.output_folder, dirs_exist_ok=True)
            zip_download_folder = archive_ext_folder.relative_to(self.output_folder)
            shutil.rmtree(Path(f"{self.output_folder}/{zip_download_folder.parts[0]}"))

    def extract_zip_file(self):
        """Extract simply static zip file to ouput folder."""
        if self.output_folder.is_dir():
            zf = ZipFile(self.zip_file_path, "r")
            zf.extractall(self.output_folder)
            zf.close()
            helpers.log_to_console("INFO", "Zip File Extracted")
            self.setup_output_folders()
        else:
            helpers.log_to_console("ERROR", "Cannot extract Zip File")

    def fix_404_error_page(self):
        """Fix 404 page by moving it to home directory. It deletes old folder."""
        try:
            with codecs.open(self._404_page, "r", "utf-8") as f:
                contents_404_page = f.read()
                contents_404_page = helpers.update_links(
                    contents_404_page,
                    self.config["callback_home"],
                    self.config["callback_deploy_url"],
                )

                with open(
                    Path(self.output_folder, "404.html"), "w", encoding="utf-8"
                ) as f:
                    f.write(contents_404_page)
            helpers.log_to_console("INFO", "404 Page Created")
            shutil.rmtree(Path(self.output_folder, self.config["pages"]["404"]))
            helpers.log_to_console("INFO", "404 Folder Removed")

        except:
            helpers.log_to_console("ERROR", "404 Page Not Created")

    def fix_home_page(self):
        """Fix Schemas and other links on home page which are ignored by simply static plugin."""
        home_page_path = Path(self.output_folder, "index.html")

        try:
            with codecs.open(home_page_path, "r", "utf-8") as f:
                contents_home_page = f.read()
                contents_home_page = helpers.update_links(
                    contents_home_page,
                    self.config["callback_home"],
                    self.config["callback_deploy_url"],
                )

                with open(home_page_path, "w", encoding="utf-8") as f:
                    f.write(contents_home_page)
            helpers.log_to_console("INFO", "Fixed Home Page")

        except:
            helpers.log_to_console("ERROR", "Home Page can not be fixed")

    def build_search_index(self):
        """Buidl search index by using title, body content and href of a given page"""
        helpers.log_to_console("INFO", "Start Building Search Index")

        try:
            # Copy Search.js into search folder
            source_path = Path(self.config["root"], "src/search.js")
            target_path = Path(
                self.output_folder, f"{self.config['pages']['search']}/search.js"
            )
            shutil.copyfile(source_path, target_path)

            # Now Process all foldre with content/index.html files
            paths_to_pages = [
                path.split("index.html")[0]
                for path in glob.glob(f"{self.output_folder}/**", recursive=True)
                if path.endswith("index.html")
            ]

            search_index_output = []

            for page_path in paths_to_pages:
                make_title = self.config["search"]["title"]
                make_url = self.config["search"]["url"]
                make_text = self.config["search"]["text"]
                make_images = self.config["search"]["images"]
                document_path = Path(page_path, "index.html")

                if document_path.exists():
                    with codecs.open(document_path, "r", "utf-8") as f:
                        contents_document_page = f.read()
                        contents_document_page = helpers.update_links(
                            contents_document_page,
                            self.config["callback_home"],
                            self.config["callback_deploy_url"],
                        )

                        soup = BeautifulSoup(contents_document_page, "lxml")
                        # append tags only if search page is specified
                        if "/search/" in str(document_path):
                            script_text = [
                                soup.new_tag(
                                    "script",
                                    src=LUNR["src"],
                                    integrity=LUNR["integrity"],
                                    crossorigin=LUNR["crossorigin"],
                                    referrerpolicy=LUNR["referrerpolicy"],
                                ),
                                soup.new_tag(
                                    "script",
                                    src=SEARCH_INDEX["src"],
                                ),
                            ]

                            for script in script_text:
                                soup.find("head").append(str(script))

                        # TODO: In future add support for minification check
                        updated_content = soup.prettify(
                            formatter=HTMLFormatter(helpers.string_formatter)
                        )

                        with open(document_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)

                        title = soup.find("title")
                        title = title.string if title else None
                        url = soup.find("meta", {"property": "og:url"})
                        url = url["content"] if url else None
                        canonical = soup.find("link", {"rel": "canonical"})
                        if canonical:
                            url = canonical["href"]

                        all_strings = soup.body.find_all(["h1", "h2", "h3", "p"])
                        output = [
                            strings for bd in all_strings for strings in bd.strings
                        ]
                        text = " ".join(output)

                        if url and document_path.parts[-2] not in [
                            self.config["pages"][page] for page in self.config["pages"]
                        ]:
                            out = {
                                "title": title if make_title else "",
                                "content": text if make_text else "",
                                "href": url if make_url else "",
                            }
                            search_index_output.append(out)
                            helpers.log_to_console("INFO", url)

            search_index_json_file_path = Path(
                self.output_folder,
                self.config["pages"]["search"],
                "lunr.json",
            )

            with open(search_index_json_file_path, "w") as fl:
                json.dump(search_index_output, fl, indent=4)

            helpers.log_to_console(
                "INFO", "Prepare Search Index for title, Url and Text"
            )

        except:
            helpers.log_to_console("ERROR", "Search Index not Generated")

    def clean_directory_check(self):
        """ """
        helpers.log_to_console(
            "INFO", "Started Removing Bad URLs/Directories for forceful deploy."
        )

        files = [f for f in glob.glob(f"{self.output_folder}/**/*", recursive=True)]
        for f in files:
            if "#" in f or "?" in f:
                if os.path.exists(f) and os.path.isdir(f):
                    print(f"removing {f} for forceful deploy.")
                    shutil.rmtree(f)

        helpers.log_to_console("INFO", "Removed Bad URLs/Directories from deployement.")

    def create_redirect_toml_file(self):
        """Create netlify.toml file with redirects information freom redirect page."""
        helpers.log_to_console(
            "INFO", "Source Redirect Page " + self.config["pages"]["redirect"]
        )
        redirect_path = Path(
            self.redirect_page,
            "index.html",
        )

        rules = [
            [
                "[[redirects]]\n",
                'from = "/*"\n',
                f'to = "/{self.config["pages"]["search"]}"\n',
                "status = 301\n",
                'query = {s = ":s"}\n',
                "force = true\n",
                "\n",
            ]
        ]

        if redirect_path.exists():
            with codecs.open(redirect_path, "r", "utf-8") as f:
                contents = f.read()
                soup = BeautifulSoup(contents, "lxml")
                redirect_table = soup.find_all("table")[0]
                table_data = [
                    [cell.text.strip("\r") for cell in row("td")]
                    for row in redirect_table.tbody.find_all("tr")
                ]

                helpers.log_to_console(
                    "WARNING", f"Redirect Rules found - {len(table_data)}"
                )

                if len(table_data) > 1:
                    for data in table_data[1:]:
                        if data[3].strip() == "1":
                            rules.append(
                                [
                                    f"[[redirects]]\n",
                                    f'{table_data[0][0].lower().strip()} = "{data[0].strip()}"\n',
                                    f'{table_data[0][1].lower().strip()} = "{data[1].strip()}"\n',
                                    f"{table_data[0][2].lower().strip()} = {data[2].strip()}\n",
                                    "\n",
                                ]
                            )

            shutil.rmtree(self.redirect_page)

        else:
            helpers.log_to_console("WARNING", "No Redirect File found")

        for redirect in self.all_redirects:
            rules.append(
                [
                    f"[[redirects]]\n",
                    f'from = "{redirect["from"]}"\n',
                    f'to = "{redirect["to"]}"\n',
                    f'status = {redirect["status"]}\n',
                    "force = true\n",
                    "\n",
                ]
            )

        netlify_toml_file = Path(self.output_folder, "netlify.toml")

        with open(netlify_toml_file, "w", encoding="utf-8") as f:
            f.writelines(["".join(rule) for rule in rules])

        helpers.log_to_console("INFO", "Netlify toml File Created Successfully")


if __name__ == "__main__":
    user_name = os.environ.get("user")
    api_token = os.environ.get("token")
    src_url = os.environ.get("src")
    dst_url = os.environ.get("dst")

    page_404 = "404-error"
    page_redirects = "redirects"
    page_robots = "robots"
    page_search = "search"

    wp_token = base64.b64encode(f"{user_name}:{api_token}".encode()).decode("utf-8")
    ss_source = src_url + "/wp-json/simplystatic/v1/settings"
    response = requests.get(ss_source, headers={"Authorization": "Basic " + wp_token})

    ss_settings = json.loads(response.content)
    archive_name = ss_settings["archive_name"]

    wordpress_simply_static_zip_url = (
        src_url
        + "/wp-content/uploads/simply-static/temp-files/"
        + archive_name
        + ".zip"
    )

    try:
        link_regex = re.compile(
            "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)",
            re.DOTALL,
        )

        for link in re.findall(
            link_regex,
            ss_settings["archive_status_messages"]["create_zip_archive"]["message"],
        ):
            wordpress_simply_static_zip_url = link[0].replace("\/", "/").split("?")[0]

    except:
        pass

    # redirects
    all_redirects = []
    try:
        redirects_source = src_url + "/wp-json/redirection/v1/redirect"
        red_response = requests.get(
            redirects_source, headers={"Authorization": "Basic " + wp_token}
        )

        redirects_dict = json.loads(red_response.content)

        all_redirects = [
            {
                "from": red["url"],
                "to": red["action_data"]["url"],
                "status": red["action_code"],
                "force": True,
            }
            for red in redirects_dict["items"]
        ]
    except:
        pass

    if wordpress_simply_static_zip_url:
        configurations = {
            "root": "",
            "callback_home": src_url,
            "callback_deploy_url": dst_url,
            "output_folder": "output",
            "zip_url": wordpress_simply_static_zip_url,
            "zip_file_name": archive_name + ".zip",
            "pages": {
                "404": page_404,
                "redirect": page_redirects,
                "robots": page_robots,
                "search": page_search,
                "all-redirects": all_redirects,
            },
            "search": {
                "title": "true",
                "url": "true",
                "text": "true",
                "images": "false",
            },
        }

        helpers.log_to_console("DEBUG", configurations)
        sspp = SimplyStaticPostProcess(config_=configurations)
        sspp.download_zip_file()
        sspp.create_output_folder()
        sspp.extract_zip_file()
        sspp.fix_404_error_page()
        sspp.fix_home_page()
        sspp.build_search_index()
        sspp.create_redirect_toml_file()
        sspp.create_robots_txt()

        force_deploy = True  # TODO: Pass via simply-static-github-callback

        if force_deploy:
            sspp.clean_directory_check()

    else:
        helpers.log_to_console("ERROR", "Zip File not avialable to deploy")
