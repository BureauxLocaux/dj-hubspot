import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dj-hubspot",
    version="0.1",
    author="Mathieu Richardoz",
    author_email="mathieu.richardoz@bureauxlocaux.com",
    description="A package to facilitate Django-Hubspot integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bureauxlocaux/dj-hubspot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
