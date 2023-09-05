#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""
Static WordPress
https://github.com/serpwings/static-wordpress

A Python Library to prepare and deploy static version of a WordPress Installation on Netlify (Static Hosting Service Providers).


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
# FUNCTIONS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++


def string_formatter(str):
    """
    String formatter for html formatting output.

    Args:
        ua_name (str, required): string to be formatted.
    """
    return str


def log_to_console(typ="INFO", message=""):
    """
    help to log text streams (input as message) to console.

    Args:
        typ (str, optional): Type of log. Default to ``INFO`` but can be any arbitrary value e.g. ``ERROR``, ``DEBUG`` and etc.
        message (str, required): message string to be logged into console.
    """
    print(f"{typ}: {message}")


def update_links(content="", link_from="", link_to=""):
    """
    Usefull for fixing schema or other links which Static-WordPress cannot fix.

    Args:
        content (str, required): Text which you want to update links e.g. Cotent on Home Page.
        link_from (str, required): string values of link which you want to change.
        link_to (str, required): string values of links to be replaced with.
    """
    if link_from and link_to and content:
        link_from = link_from.split("://")[-1]
        link_to = link_to.split("://")[-1]
        return content.replace(link_from, link_to)
    return content


if __name__ == "__main__":
    pass
