#!/usr/bin/env python3
import pathlib
from setuptools import setup

import sketchfab

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sketchfab",
    version=sketchfab.VERSION,
    description="Sketchfab client",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/habx/lib-py-sketchfab",
    author="Florent Clairambault",
    author_email="florent@habx.fr",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: 3D Rendering"
    ],
    keywords='sketchfab 3d-model client-library development',
    packages=["sketchfab"],
    scripts=["scripts/sketchfab"],
    python_requires=">=3.7",
    install_requires=["requests==2.22.0", "urllib3"],
    extras_require={
        'dev': ['pdoc3'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/habx/lib-py-sketchfab/issues',
        'Source': 'https://github.com/habx/lib-py-sketchfab',
    },
)
