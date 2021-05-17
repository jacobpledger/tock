from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="tock",
    version="0.1.0",
    description="A Tickspot client for batch updates.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Jacob Pledger",
    author_email="tock@jacob.jacobpledger.ca",
    url="https://github.com/jacobpledger/tock",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
