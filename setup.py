"""
STATIC WORDPRESS: WordPress as Static Site Generator
A Python Package for Converting WordPress Installation to a Static Website
https://github.com/serpwings/static-wordpress

    setup.py
    
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

import os
from setuptools import (
    find_packages,
    setup,
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# INTERNAL IMPORTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

from src.staticwordpress.core import __version__

# +++++++++++++++++++++++++++++++++++++++++++++++++++++
# DATABASE/CONSTANTS LIST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

python_minor_min = 8
python_minor_max = 12
confirmed_python_versions = [
    "Programming Language :: Python :: 3.{MINOR:d}".format(MINOR=minor)
    for minor in range(python_minor_min, python_minor_max + 1)
]

# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

# Define source directory (path)
SRC_DIR = "src"

# Requirements for dev and gui
extras_require = {
    "dev": [
        "black",
        "python-language-server[all]",
        "setuptools",
        "twine",
        "wheel",
        "setuptools",
        "pytest",
        "pytest-cov",
        "twine",
        "wheel",
        "mkdocs",
        "mkdocs-gen-files",
        "mkdocstrings[python]",
        "pymdown-extensions",
    ],
    "gui": ["pyqt5", "qtconsole"],
}
extras_require["all"] = list(
    {rq for target in extras_require.keys() for rq in extras_require[target]}
)

# Install package
setup(
    name="staticwordpress",
    packages=find_packages(SRC_DIR),
    package_dir={"": SRC_DIR},
    version=__version__,
    description="Python Package for Converting WordPress Installation to a Static Website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Faisal Shahzad",
    author_email="info@serpwings.com",
    url="https://github.com/serpwings/static-wordpress",
    download_url="https://github.com/serpwings/static-wordpress/releases/v%s.tar.gz"
    % __version__,
    license="GPLv3+",
    keywords=[
        "wordpress",
        "static-site-generators",
        "search-engines",
        "seo",
    ],
    scripts=[],
    include_package_data=True,
    python_requires=">=3.{MINOR:d}".format(MINOR=python_minor_min),
    setup_requires=[],
    install_requires=[
        "click",
        "pyyaml",
        "requests",
        "beautifulsoup4",
        "lxml",
        "GitPython",
        "PyGithub",
        "PyYAML",
    ],
    extras_require=extras_require,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "staticwordpress = staticwordpress.gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ]
    + confirmed_python_versions
    + [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: System",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
