from setuptools import setup, find_packages
from pathlib import Path

# Discover all bin scripts and make console entry points
BIN_DIR = Path("eqnlint/bin")
entry_points = [
    f"{script.stem.replace('_', '-')} = eqnlint.bin.{script.stem}:main"
    for script in BIN_DIR.glob("*.py") if script.stem != "__init__"
]

setup(
    name="eqnlint",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Optional: load from file
        # line.strip() for line in open("requirements.txt") if line.strip()
        "httpx",
        "aiofiles",
        "aiohttp",  # if needed by any async backends
        "beautifulsoup4",
        "lxml",     # for LaTeX or XBRL parsing if needed
        "tiktoken", # if token counting is used
    ],
    entry_points={
        "console_scripts": [
            "audit-units = eqnlint.bin.audit_units:main",
            "dimensional-audit = eqnlint.bin.dimensional_audit:main",
            # add more if needed
        ],
    },
    author="John Ryan",
    author_email="tambotitree@gmail.com",
    description="Equation linting tools for dimensional, symbolic, and prose auditing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)