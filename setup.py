""" Package setup file. """

from setuptools import setup, find_packages

with open("README.md","r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name='NREL-emerge',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='1.0.0',
    description='Emerging technologies Management and Risk evaluation on distributions Grid Evolution',
    author='Kapil Duwadi',
    author_email='kapil.duwadi@nrel.gov',
    packages=find_packages(),
    url="https://github.com/NREL/EMeRGE",
    keywords="Distribution System DER technologies management risk impact analysis",
    install_requires=requirements,
    # package_dir={"emerge": "emerge"}, 
    entry_points={
        "console_scripts": [
            "emerge=emerge.cli.cli:cli"
        ],
    },
    python_requires=">=3.10",  
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ]
)