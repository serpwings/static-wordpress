# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/staticwordpress

    src/staticwordpress/core/redirects.py
    
    Copyright (C) 2020-2023 Faisal Shahzad <info@serpwings.com>

<LICENSE_BLOCK>
The contents of this file are subject to version 3 of the 
GNU General Public License (GPL-3.0). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/gpl-3.0.txt
https://github.com/serpwings/staticwordpress/blob/master/LICENSE


Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# STANDARD LIBARY IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
import requests
import hashlib

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from ..core.constants import HOST, REDIRECTS

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPLEMENATIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


class Redirect:
    def __init__(self, from_, to_, query_, status, force_, source_) -> None:
        self._from = from_
        self._to = to_
        self._query = query_
        self._status = status
        self._force = force_
        self._source = source_
        self._hash = hashlib.sha256(from_.encode("utf-8")).hexdigest()

    @property
    def hash(self):
        return self._hash

    def as_json(self) -> dict:
        return {"from": self._from, "to": self._to, "status": self._status}

    def as_line(self, new_line_: bool = False) -> str:
        nl = "\n" if new_line_ else ""
        return f"{self._from}\t{self._to}\t{self._status}{nl}"

    def as_toml(self) -> str:
        # need cleanup here
        if self._query:
            return f'[[redirects]]\nfrom = "{self._from}"\nto = "{self._to}"\nquery = {self._query}\nstatus = {self._status}\nforce = {str(self._force).lower()}\n\n'
        else:
            return f'[[redirects]]\nfrom = "{self._from}"\nto = "{self._to}"\nstatus = {self._status}\nforce = {str(self._force).lower()}\n\n'


class Redirects:
    def __init__(self) -> None:
        self._items = dict()

    def add_redirect(self, redirect_: Redirect) -> None:
        if redirect_.hash not in self._items:
            self._items[redirect_.hash] = redirect_

    def consolidate(self) -> None:
        pass

    def add_redirects(self, redirects_list_: list) -> None:
        for redirect in redirects_list_:
            self.add_redirect(redirect)

    def save(self, output_file_, host_: HOST) -> None:
        with open(
            output_file_,
            "w",
            encoding="utf-8",
        ) as f:
            for _, redirect in self._items.items():
                if host_ == HOST.NETLIFY:
                    f.write(redirect.as_toml())
                else:
                    f.write(redirect.as_line(True))

    def get_from_plugin(self, redirects_api_path: str, wp_auth_token_: str):
        red_response = requests.get(
            redirects_api_path, headers={"Authorization": "Basic " + wp_auth_token_}
        )

        redirects_dict = json.loads(red_response.content)
        for red in redirects_dict["items"]:
            self.add_redirect(
                redirect_=Redirect(
                    from_=red["url"],
                    to_=red["action_data"]["url"],
                    status=red["action_code"],
                    query_=None,
                    force_=True,
                    source_=REDIRECTS.REDIRECTION.value,
                )
            )

    def add_search(self, search_page: str):
        self.add_redirect(
            Redirect(
                from_="/*",
                to_=f"/{search_page}/",
                status=301,
                query_='{s = ":s"}',
                force_=True,
                source_=REDIRECTS.NONE.value,
            )
        )
