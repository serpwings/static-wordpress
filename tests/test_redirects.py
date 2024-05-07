# -*- coding: utf-8 -*-

"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    tests\test_redirects.py
    
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
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from staticwordpress.core.redirects import Redirects, Redirect
from staticwordpress.core.constants import REDIRECTS


def test_redirect():
    red = Redirect(
        from_="/",
        to_="https://seowings.org",
        status_=200,
        query_=None,
        force_=True,
        source_=REDIRECTS.REDIRECTION,
    )

    assert red.as_line() == "/\thttps://seowings.org\t200"
    assert red.as_json() == {"from": "/", "status": 200, "to": "https://seowings.org"}
