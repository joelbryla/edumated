import setuptools
from edumated.__version__ import __author__, __title__, __version__

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email="",
    description="When you've check mated edumate",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ninjakow/edumated",
    install_requires=open("requirements.txt").readlines(),
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["edumated=edumated.edumate:main"]},
)
