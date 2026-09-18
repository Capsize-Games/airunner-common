"""setup.py for the standalone airunner-common package.

Extracted from Capsize-Games/airunner's shared/ directory (issue #2197,
part of the repository-split tracker #2185). This is the foundation of
the dependency graph -- every other AIRunner distribution depends on it
and it depends on none of them.

The build metadata below is vendored statically rather than imported
from ``airunner_common.package_metadata`` -- self-importing a package
from its own setup.py is fragile under PEP 517 build isolation (a
fresh build environment doesn't have this project's own directory
importable), and every sibling package in the source repository
already avoids this for the same reason (issue #2038). Keep the
values in this file in sync with
``airunner_common/package_metadata.py`` when a dependency changes.
"""

from pathlib import Path

from setuptools import setup

VERSION = "6.1.6"

# The project is GPL-3.0-only, matching the source application. Mirrored
# from airunner_common/package_metadata.py.
LICENSE_CLASSIFIERS = [
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
]

# Supply-chain hardening; see airunner_common/package_metadata.py for the
# full rationale (PyPI rejects direct references, so depend on a real
# published release by version instead of a hash-pinned archive URL).
FACEHUGGERSHIELD_REQUIREMENT = "facehuggershield==1.0.0"

README = (Path(__file__).resolve().parent / "README.md").read_text(
    encoding="utf-8"
)

DEVELOPMENT_REQUIREMENTS = ["pytest", "pytest-timeout"]

setup(
    name="airunner-common",
    version=VERSION,
    author="Capsize LLC",
    description="Shared foundation (settings, contracts, layout) for AIRunner packages",
    long_description=README,
    long_description_content_type="text/markdown",
    license="GPL-3.0-only",
    classifiers=LICENSE_CLASSIFIERS,
    author_email="contact@capsizegames.com",
    url="https://github.com/Capsize-Games/airunner-common",
    package_dir={"": "."},
    packages=["airunner_common"],
    python_requires=">=3.13.3",
    install_requires=[
        "python-dotenv==1.2.2",
        FACEHUGGERSHIELD_REQUIREMENT,
    ],
    extras_require={
        "development": DEVELOPMENT_REQUIREMENTS,
        "dev": DEVELOPMENT_REQUIREMENTS,
    },
    include_package_data=True,
)
