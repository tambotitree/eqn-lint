from setuptools import setup, find_packages

setup(
    name="eqnlint",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # These should match what's in requirements.txt, or you can read that file here
    ],
    entry_points={
        "console_scripts": [
            "dimensional-audit = eqnlint.bin.dimensional_audit:main",
        ],
    },
    author="John Ryan",
    author_email="johnryan@mac.com",
    description="Equation linting tools for dimensional and symbolic auditing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
